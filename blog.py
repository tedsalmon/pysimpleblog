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
        abort(404, "Not Found")
    recent = entries.get_recent()
    return template('main', settings, page_id=page_id, posts=posts,
                    user_login=login_data,blog_links=links.get_links(),
                    recent_posts=recent)


@blog_app.route('/<url:re:[a-z0-9]{6}>', apply=[auth_check()])
@blog_app.route('/<year:int>/<url>', apply=[auth_check()])
def show_post(url, login_data=False, year=False,):
    post_data = entries.get_post(url, year=year)
    if not post_data:
        abort(404, "Not Found")
    return template('post', settings, sub_title=post_data['title'],
                    post=post_data, user_login=login_data,
                    blog_links=links.get_links())


@blog_app.route('/archive', apply=[auth_check()])
def show_archives(login_data=False,):
    return template('archive', settings, sub_title='Archives',
                    user_login=login_data, special=entries.get_archive(),
                    blog_links=links.get_links())


@blog_app.route('/special/<page_name>', apply=[auth_check()])
def show_special_page(page_name, login_data=False, ):
    page = entries.get_page(page_name)
    if not page:
        abort(404, "Not Found")
    return template('special', settings, sub_title=page['title'],
                    user_login=login_data, page=page,
                    blog_links=links.get_links())


@blog_app.route('/tags/<tag_name>', apply=[auth_check()])
def show_tags(tag_name, login_data=False, ):
    tag_name = tag_name.replace('-',' ')
    post_by_tags = entries.get_by_tags([tag_name])
    return template('tags', settings, sub_title='Posts Tagged %s' % tag_name,
                    tag=tag_name, posts=post_by_tags, user_login=login_data,
                    blog_links=links.get_links())


@blog_app.route('/logout', apply=[auth_check()])
def logout(login_data=False, ):
    if login_data:
        s_id = request.get_cookie('session_id')
        sessions.expire_session(s_id)
        response.delete_cookie(s_id)
    redirect('/')


# Admin functions
@blog_app.route('/admin', apply=[auth_check(required=True)])
def show_admin(login_data=False, ):
    return template('admin/main', settings, user_login=login_data,
                    blog_links=links.get_links())


@blog_app.route('/admin/new-post', apply=[auth_check(required=True)])
def show_new_post(login_data=False, ):
    return template('admin/post_editor', settings, user_login=login_data,
                    blog_links=links.get_links())


# @todo Rename edit-post
@blog_app.route('/admin/post-editor/<post_id:re:[a-z0-9]{6}>',
                apply=[auth_check(required=True)])
def show_post_editor(post_id, login_data=False, ):
    post = entries.get_post_internal(post_id)
    if not post:
        abort(404, "Not Found")
    return template('admin/post_editor', settings, user_login=login_data,
                    post_data=post, blog_links=links.get_links())


@blog_app.route('/admin/manage-posts', apply=[auth_check(required=True)])
@blog_app.route('/admin/manage-posts/<page_num:int>',
                apply=[auth_check(required=True)])
def show_post_manager(page_num=1, login_data=False, ):
    posts = entries.get_posts(page_num, all_posts=True)
    if not posts:
        abort(404, "Not Found")
    return template('admin/post_management', settings, user_login=login_data,
                    posts=posts, blog_links=links.get_links())


@blog_app.route('/admin/comment-approver', apply=[auth_check(required=True)])
def show_pending_comments(login_data=False, ):
    comments = entries.get_unapproved_comments()
    return template('admin/comments', settings, user_login=login_data,
                    comments=comments, blog_links=links.get_links())

@blog_app.route('/admin/manage-links', apply=[auth_check(required=True)])
def show_link_manager(login_data=False, ):
    return template('admin/link_management', settings, user_login=login_data,
                    links=links.get_links(True), blog_links=links.get_links())


@blog_app.route('/admin/view-profile', apply=[auth_check(required=True)])
def show_profile(login_data=False, ):
    profile_data = users.get_user(login_data)
    if not profile_data:
        abort("404", "Not Found")
    return template("admin/profile_editor", settings, user_login=login_data,
                    profile_data=profile_data, blog_links=links.get_links())

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
    req_data = request.json
    post_data = entries.get_post(req_data['post_id'])
    if not req_data['comment']:
        return_data['error'] = 'No comment given'
    for key in req_data:
        req_data[key] = str(utils.escape(req_data[key]))
    comment = {'name': req_data['name'],
               'email': req_data['email'],
               'comment': req_data['comment'],}
    if not entries.create_comment(comment, req_data['post_id'], post_data):
        return_data['error'] = 'Parent post not found'
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
    data = sterilize(request.json, ['url','title'])
    if not data:
        return_data['error'] = 'Missing Parameters'
    links.edit_link(link_id, data)
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
        '500 Internal Server Error': 'Error encountered while\
                                      processing your request.',
        '403 Forbidden': 'Please login to view this page.',
        '401 Unauthorized': 'You are not authorized to be here.',
        '404 Not Found': 'The page you are looking cannot be found.',
        '405 Method Not Allowed': 'Method not allowed!',
    }
    err_msg = 'Something really bad happened!'
    try:
        err_msg = err_msgs[response.status]
    except KeyError:
        pass
    if settings['debug'] and error.traceback:
        err_msg = '<pre>%s</pre>' % error.traceback
    login_data, blog_links = False, False
    if '404' in response.status:
        blog_links = links.get_links()
        login_data = verify_auth()
    return template('error', settings, error=err_msg, user_login=login_data,
                    blog_links=blog_links)

def sterilize(data, required_fields, ):
    return_data = {}
    for key in required_fields:
        if key not in data:
            return False
        return_data[key] = str(utils.escape(data[key]))
    return return_data
