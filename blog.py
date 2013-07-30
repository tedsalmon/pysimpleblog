#!/usr/bin/python
# -*- coding: utf-8 -*-
from bottle import abort, Bottle, redirect, response, request, static_file, jinja2_template as template
from jinja2 import utils
from pysimpleblog.core.functions import BASE, Settings
from pysimpleblog.core.models import Blog, Links, Users, Sessions

blog_app = Bottle()
# Models
entries = Blog()
users = Users()
sessions = Sessions()
links = Links()
# Settings
settings = Settings()

def auth_check(required=False, api=False, ):
    # This has to be applied to routes via
    # the 'apply' param because of a bug in Bottle
    # https://github.com/defnull/bottle/issues/384
    def decorator(fn):
        def wrapper(*args, **kwargs):
            auth_status = verify_auth()
            kwargs.update(login_data=auth_status)
            if not auth_status:
                if required:
                    if not api:
                        abort(403, "Forbidden")
                    else:
                        response.status = 401
                        return False
                return fn(*args, **kwargs)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@blog_app.route('/', apply=[auth_check()])
@blog_app.route('/page/<page_id>', apply=[auth_check()])
def show_listing(login_data=False, page_id=None,):
    page_id = 1 if not page_id else int(page_id)
    posts = entries.get_posts(page_id)
    if not posts:
        abort(404, 'Not Found')
    page_variables = generate_pagevars(login_data)
    return template('main', page_variables, page_id=page_id,
                    posts=posts, recent_posts=entries.get_recent())


@blog_app.route('/<url:re:[a-z0-9]{6}>', apply=[auth_check()])
@blog_app.route('/<year:int>/<url>', apply=[auth_check()])
def show_post(url, login_data=False, year=False,):
    post_data = entries.get_post(url, year=year)
    if not post_data:
        abort(404, "Not Found")
    page_variables = generate_pagevars(login_data, post_data['title'])
    return template('post', page_variables, post=post_data)


@blog_app.route('/archive', apply=[auth_check()])
def show_archives(login_data=False,):
    page_variables = generate_pagevars(login_data, 'Archives')
    return template('archive', page_variables, posts=entries.get_archive())


@blog_app.route('/special/<page_name>', apply=[auth_check()])
def show_special_page(page_name, login_data=False, ):
    page = entries.get_page(page_name)
    if not page:
        abort(404, "Not Found")
    page_variables = generate_pagevars(login_data, page['title'])
    return template('special', page_variables, page=page)


@blog_app.route('/tags/<tag_name>', apply=[auth_check()])
def show_tags(tag_name, login_data=False, ):
    tag_name = tag_name.replace('-',' ')
    post_by_tags = entries.get_by_tags([tag_name.lower()])
    page_variables = generate_pagevars(login_data,
                                       'Posts Tagged %s' % tag_name)
    return template('tags', page_variables, tag=tag_name, posts=post_by_tags)


# Admin functions
@blog_app.route('/admin', apply=[auth_check(required=True)])
def show_admin(login_data=False, ):
    page_variables = generate_pagevars(login_data, 'Admin')
    return template('admin/main', page_variables, settings=settings)


@blog_app.route('/admin/new-post', apply=[auth_check(required=True)])
def show_new_post(login_data=False, ):
    page_variables = generate_pagevars(login_data, 'New Post')
    return template('admin/post_editor', page_variables)


# @todo Rename edit-post
@blog_app.route('/admin/post-editor/<post_id:re:[a-z0-9]{6}>',
                apply=[auth_check(required=True)])
def show_post_editor(post_id, login_data=False, ):
    post = entries.get_post_internal(post_id)
    if not post:
        abort(404, "Not Found")
    page_variables = generate_pagevars(login_data)
    return template('admin/post_editor', page_variables, post_data=post)


@blog_app.route('/admin/manage-posts', apply=[auth_check(required=True)])
@blog_app.route('/admin/manage-posts/<page_num:int>',
                apply=[auth_check(required=True)])
def show_post_manager(page_num=1, login_data=False, ):
    posts = entries.get_posts(page_num, all_posts=True)
    if not posts:
        abort(404, "Not Found")
    page_variables = generate_pagevars(login_data, 'Manage Posts')
    return template('admin/post_management', page_variables, posts=posts)


@blog_app.route('/admin/comment-approver', apply=[auth_check(required=True)])
def show_pending_comments(login_data=False, ):
    comments = entries.get_unapproved_comments()
    page_variables = generate_pagevars(login_data, 'Manage Comments')
    return template('admin/comments', page_variables, comments=comments)

@blog_app.route('/admin/manage-links', apply=[auth_check(required=True)])
def show_link_manager(login_data=False, ):
    page_variables = generate_pagevars(login_data, 'Manage Links')
    return template('admin/link_management', page_variables,
                    links=links.get_links(True))


@blog_app.route('/admin/view-profile', apply=[auth_check(required=True)])
def show_profile(login_data=False, ):
    profile_data = users.get_user(login_data)
    if not profile_data:
        abort("404", "Not Found")
    page_variables = generate_pagevars(login_data, 'Edit Profile')
    return template("admin/profile_editor", page_variables,
                    profile_data=profile_data)

@blog_app.route('/logout', apply=[auth_check()])
def do_logout(login_data=False, ):
    if login_data:
        s_id = request.get_cookie('session_id')
        sessions.expire_session(s_id)
        response.delete_cookie(s_id)
    redirect('/')

#
# RESTful API Begins here
# Read-only functions:
# GET => /api/post, GET => /api/posts, POST => /api/comment
# All other functions require BASIC Auth or a Session ID Cookie
#
@blog_app.route('/api/login', method='POST')
def api_login():
    return_data = {'error': False}
    fields = ['username', 'password']
    req_data = sterilize(request.json, fields)
    if not req_data:
        return_data['error'] = 'Missing Parameters'
        return return_data
    user = users.verify_login(req_data['username'], req_data['password'])
    if not user:
        return_data['error'] = users.error
        return return_data
    # Start Session
    session = sessions.create_session(user['_id'])
    response.set_cookie('session_id', session['session_id'],
                        expires=session['expiry'], path='/', )
    return return_data
    

@blog_app.route('/api/admin/post', method='POST',
                apply=[auth_check(required=True, api=True)])
def api_post_create(login_data=False, ):
    return_data = {'error': False}
    fields = ['title', 'body', 'tags', 'status', 'type']
    post_data = sterilize(request.json, fields)
    if not post_data:
        return_data['error'] = 'Missing Parameters'
        return return_data
    post_data['tags'] = [tag.strip() for tag in post_data['tags'].split(',')]
    NS = 0 if post_data['type'] == '0' else 1
    new_post = entries.create_post(post_data, login_data, NS)
    if not new_post:
        return_data['error'] = 'Failed to create post!'
        return return_data
    return_data['location'] = new_post
    return return_data


@blog_app.route('/api/post', method='GET')
@blog_app.route('/api/post/<page_num:int>', method='GET')
def api_post_getmany(page_num=1, ):
    return_data = {'posts': []}
    return_data['posts'] = entries.get_posts(page_num)
    for i in xrange(0, len(return_data['posts'])):
        post = return_data['posts'][i]
        post['date'] = str(post['date'])
        del post['comments']
        del post['body']
    return return_data


@blog_app.route('/api/post/<post_id>', method='GET')
def api_post_get(post_id, ):
    post_data = {'post': {}}
    post = entries.get_post(post_id)
    if post:
        post['date'] = str(post['date'])
        for j in xrange(0, len(post['comments'])):
            comment = post['comments'][j]
            comment['date'] = str(comment['date'])
        post_data['post'] = post
    return post_data


@blog_app.route('/api/post/<post_id>', method='DELETE',
                apply=[auth_check(required=True, api=True)])
def api_post_delete(post_id, login_data=False, ):
    return_data = {'error': False}
    if not entries.delete_post(post_id):
        return_data['error'] = 'Invalid Post ID'
        return return_data
    return return_data


@blog_app.route('/api/post/<post_id>', method='PUT',
                apply=[auth_check(required=True, api=True)])
def api_post_edit(post_id, login_data=False, ):
    return_data = {'error': False}
    req_data = request.json
    post = entries.get_post_internal(post_id)
    if not post:
        return_data['error'] = 'Invalid Post ID'
        return return_data
    post_data = dict((key, post[key]) for key in post)
    special_types =  ['status', 'type'] 
    for key in post_data:
        if key in req_data:
            if key in special_types:
                post_data[key] = int(req_data[key])
            else:
                post_data[key] = req_data[key]
    url = entries.edit_post(post_id, post_data)
    if not url:
        return_data['error'] = 'Error Updating post'
    return_data['location'] = url
    return return_data


@blog_app.route('/api/comment', method='POST')
def api_comment_create():
    return_data = {'error': False}
    req_data = sterilize(request.json,
                         ['post_id', 'name', 'email', 'body'], escape=True)
    if not req_data:
        return_data['error'] = 'Missing Parameters'
        return return_data
    comment = dict((key, req_data[key]) for key in ['name', 'body', 'email'])
    if not entries.create_comment(comment, req_data['post_id']):
        return_data['error'] = 'Parent post not found.'
    else:
        return_data['msg'] = 'Comment submitted for approval.'
    return return_data


@blog_app.route('/api/comment/<comment_id>', method='PUT',
                apply=[auth_check(required=True, api=True)])
def api_comment_approve(comment_id, login_data=False, ):
    entries.approve_comment(comment_id)
    return True


@blog_app.route('/api/comment/<comment_id>', method='DELETE',
                apply=[auth_check(required=True, api=True)])
def api_comment_deny(comment_id, login_data=False, ):
    entries.deny_comment(comment_id)
    return True


@blog_app.route('/api/link', method='POST',
                apply=[auth_check(required=True, api=True)])
def api_link_create(login_data=False, ):
    return_data = {'error': False}
    data = sterilize(request.json, ['url','title'])
    if not data:
        return_data['error'] = 'Missing Parameters'
    else:
        link_id = links.create_link(data, login_data)
    return return_data


@blog_app.route('/api/link/<link_id>', method='DELETE',
                apply=[auth_check(required=True, api=True)])
def api_link_delete(link_id, login_data=False, ):
    return_data = {'error': False}
    if not links.delete_link(link_id):
        return_data['error'] = 'Invalid Link ID'
    return return_data


@blog_app.route('/api/link/<link_id>', method='PUT',
                apply=[auth_check(required=True, api=True)])
def api_link_edit(link_id, login_data=False, ):
    return_data = {'error': False}
    data = sterilize(request.json, required_fields=False, escape=True)
    link = links.get_link(link_id)
    if not link:
        return_data['error'] = 'Link does not exists!'
        return return_data
    for key, val in data.items():
        if key in link:
            link[key] = val
    links.edit_link(link)
    return return_data
    

@blog_app.route('/api/changepassword/<username>', method='PUT',
                apply=[auth_check(required=True, api=True)])
def api_password_edit(login_data=False, ):
    return_data = {'error': False}
    req_data = request.json
    fields = ['new', 'confirm', 'old']
    pw_data = {}
    for field in fields:
        if field not in req_data:
            return_data['error'] = 'No %s password provided' % field
            return return_data
        pw_data['%s'] = req_data['field']
    return_data['output'] = users.edit_password(pw_data)
    return return_data

# Static handler when run in debug mode
@blog_app.route('/static/<file_type>/<file_name>')
def static(file_type, file_name, ):
    return static_file(file_name, root='%s/static/%s' % (BASE, file_type), )

# Error handling
@blog_app.error(401)
@blog_app.error(403)
@blog_app.error(404)
@blog_app.error(405)
@blog_app.error(500)
def error_handler(error, ):
    err_msgs = {
        '401 Unauthorized': 'You are not authorized to be here.',
        '403 Forbidden': 'Please login to view this page.',
        '404 Not Found': 'The page you are looking cannot be found.',
        '405 Method Not Allowed': 'Method not allowed!',
        '500 Internal Server Error': 'Error encountered while\
                              processing your request.',
    }
    msg = 'Something really bad happened!'
    try:
        msg = err_msgs[response.status]
    except KeyError:
        pass
    p_vars, strace = False, False
    if settings['debug'] and error.traceback:
        strace = error.traceback
    if '404' in response.status:
        p_vars = generate_pagevars(verify_auth(), 'Error')
    return template('error', page_variables=p_vars, error=msg, stacktrace=strace)

# Helper methods
def generate_pagevars(login_data=False, sub_title=False, ):
    nav_links = links.get_links()
    return_data = {
        'user_id': login_data, 'nav_links': nav_links, 'sub_title': sub_title
    }
    for key, val in settings.items():
        if 'site_' in key:
            return_data[key] = val
    return return_data


def sterilize(data, required_fields, escape=False, ):
    return_data = {}
    if required_fields:
        for key in required_fields:
            if key not in data:
                return False
            if not escape:
                return_data[key] = data[key]
            else:
                return_data[key] = utils.escape(data[key])
    else:
        for key in data:
            if not escape:
                return_data[key] = data[key]
            else:
                return_data[key] = utils.escape(data[key])
    return return_data


def verify_auth():
    s_id = request.get_cookie('session_id')
    auth = request.auth
    if not s_id and not auth:
        return False
    login_data = sessions.verify_session(s_id)
    if login_data:
        return login_data
    if auth:
        user, passwd = auth
        login_data = users.verify_login(user, passwd)
        if login_data:
            return login_data['username']
    return False
