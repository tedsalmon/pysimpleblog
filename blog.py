#!/usr/bin/python
# -*- coding: utf-8 -*-
from bottle import abort, Bottle, redirect, response, request, static_file, jinja2_template as template
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
                        realm = 'Basic realm="API"'
                        err_msg = "Please provide BASIC auth or a Session ID"
                        response.headers['WWW-Authenticate'] = realm
                        response.status = 401
                        return {"error": err_msg}
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
    post_data = entries.get_post(url, year=year, auth=login_data)
    if not post_data:
        abort(404, "Not Found")
    page_variables = generate_pagevars(login_data, post_data['title'],
                                       ', '.join(post_data['tags']))
    return template('post', page_variables, post=post_data)


@blog_app.route('/archive', apply=[auth_check()])
def show_archives(login_data=False,):
    page_variables = generate_pagevars(login_data, 'Archives', 'blog, archive')
    return template('archive', page_variables, posts=entries.get_archive())


@blog_app.route('/special/<page_name>', apply=[auth_check()])
def show_special_page(page_name, login_data=False, ):
    page = entries.get_page(page_name)
    if not page:
        abort(404, "Not Found")
    page_variables = generate_pagevars(login_data, page['title'],
                                       page['title'].replace(' ', ', '))
    return template('special', page_variables, page=page)


@blog_app.route('/tags/<tag_name>', apply=[auth_check()])
def show_tags(tag_name, login_data=False, ):
    tag_name = tag_name.replace('-',' ')
    post_by_tags = entries.get_by_tags([tag_name.lower()])
    page_variables = generate_pagevars(login_data,
                                       'Posts Tagged %s' % tag_name,
                                       'tags, %s' % tag_name)
    return template('tags', page_variables, tag=tag_name, posts=post_by_tags)


# Admin functions
@blog_app.route('/admin', apply=[auth_check(required=True)])
def show_admin(login_data=False, ):
    page_variables = generate_pagevars(login_data, 'Admin')
    return template('admin/settings', page_variables, settings=settings)


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
    return template('admin/comment_management', page_variables, comments=comments)

@blog_app.route('/admin/manage-links', apply=[auth_check(required=True)])
def show_link_manager(login_data=False, ):
    page_variables = generate_pagevars(login_data, 'Manage Links')
    return template('admin/link_management', page_variables,
                    links=links.get_links(True))


@blog_app.route('/admin/manage-users', apply=[auth_check(required=True)])
def show_link_manager(login_data=False, ):
    page_variables = generate_pagevars(login_data, 'Manage Users')
    return template('admin/user_management', page_variables,
                    users=users.get_users())


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
# GET => /api/v1/post, GET => /api/v1/posts, POST => /api/v1/comment
# All other functions require BASIC Auth or a Session ID Cookie
#
@blog_app.route('/api/v1/login', method='POST')
def api_login():
    return_data = {'error': False}
    user = users.verify_login(request.json)
    if not user:
        return_data['error'] = users.get_last_error()
        return return_data
    # Start Session
    s_timeout = None
    if 'remember' in request.json:
        if request.json['remember'] == 1:
            s_timeout = -86400 * 90
    session = sessions.create_session(user['_id'], session_lifespan=s_timeout)
    response.set_cookie('session_id', session['session_id'],
                        expires=session['expiry'], path='/', )
    return return_data


@blog_app.route('/api/v1/posts/<page_num:int>', method='GET')
def api_post_list(page_num, ):
    return_data = {'posts': entries.get_post_list(page_num)}
    return return_data


@blog_app.route('/api/v1/post', method='POST',
                apply=[auth_check(required=True, api=True)])
def api_post_create(login_data=False, ):
    return_data = {'error': False}    
    new_post = entries.create_post(request.json, login_data)
    if not new_post:
        return_data['error'] = entries.get_last_error()
        return return_data
    return_data['location'] = new_post
    return return_data


@blog_app.route('/api/v1/post/<post_id>', method='GET')
def api_post_get(post_id, ):
    post_data = {'post': entries.get_post_clean(post_id)}
    return post_data


@blog_app.route('/api/v1/post/<post_id>', method='DELETE',
                apply=[auth_check(required=True, api=True)])
def api_post_delete(post_id, login_data=False, ):
    return_data = {'error': False}
    if not entries.delete_post(post_id):
        return_data['error'] = entries.get_last_error()
        return return_data
    return return_data


@blog_app.route('/api/v1/post/<post_id>', method='PUT',
                apply=[auth_check(required=True, api=True)])
def api_post_edit(post_id, login_data=False, ):
    return_data = {'error': False}
    res = entries.edit_post(post_id, request.json)
    if not res:
        return_data['error'] = entries.get_last_error()
        return False
    return_data['location'] = entries.get_uri(post_id)
    return return_data


@blog_app.route('/api/v1/post/<post_id>/comment', method='POST')
def api_comment_create(post_id, ):
    return_data = {'error': False}
    if not entries.create_comment(post_id, request.json):
        return_data['error'] = entries.get_last_error()
    else:
        return_data['msg'] = 'Comment submitted for approval.'
    return return_data


@blog_app.route('/api/v1/post/<post_id>/comment/<comment_id>', method='PUT',
                apply=[auth_check(required=True, api=True)])
def api_comment_approve(comment_id, post_id, login_data=False, ):
    return {"error": not bool(entries.approve_comment(post_id, comment_id))}


@blog_app.route('/api/v1/post/<post_id>/comment/<comment_id>', method='DELETE',
                apply=[auth_check(required=True, api=True)])
def api_comment_deny(comment_id, post_id, login_data=False, ):
    return {"error": not bool(entries.deny_comment(post_id, comment_id))}


@blog_app.route('/api/v1/link', method='POST',
                apply=[auth_check(required=True, api=True)])
def api_link_create(login_data=False, ):
    return_data = {'error': False}
    if not links.create_link(request.json, login_data):
        return_data['error'] = links.get_last_error()
    return return_data


@blog_app.route('/api/v1/link/<link_id>', method='DELETE',
                apply=[auth_check(required=True, api=True)])
def api_link_delete(link_id, login_data=False, ):
    return_data = {'error': False}
    if not links.delete_link(link_id):
        return_data['error'] = links.get_last_error()
    return return_data


@blog_app.route('/api/v1/link/<link_id>', method='PUT',
                apply=[auth_check(required=True, api=True)])
def api_link_edit(link_id, login_data=False, ):
    return_data = {'error': False}
    if not links.edit_link(link_id, request.json):
        return_data['error'] = links.get_last_error()
    return return_data


@blog_app.route('/api/v1/user', method='POST',
                apply=[auth_check(required=True, api=True)])
def api_create_user(login_data=False, ):
    return_data = {'error': False}
    if not users.create_user(request.json):
        return_data['error'] = users.get_last_error()
    return return_data


@blog_app.route('/api/v1/changepassword/<username>', method='PUT',
                apply=[auth_check(required=True, api=True)])
def api_password_edit(login_data=False, ):
    return_data = {'error': False}
    #@TODO Implement
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
    page_variables, strace = {}, False
    if settings['debug'] and error.traceback:
        strace = error.traceback
    if '404' in response.status:
        page_variables = generate_pagevars(verify_auth(), 'Error')
    return template('error', page_variables, error=msg,
                    stacktrace=strace)

# Helper methods
def generate_pagevars(login_data=False, sub_title=False, keywords=False, ):
    nav_links = links.get_links()
    return_data = {
        'user_id': login_data, 'nav_links': nav_links, 'sub_title': sub_title
    }
    for key, val in settings.items():
        if 'site_' in key:
            return_data[key] = val
    if sub_title:
        return_data['site_description'] = sub_title
    if keywords:
        return_data['site_keywords'] = keywords
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
