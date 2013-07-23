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

def auth_check(func):
    def wrapper(*args, **kwargs):
        login_data=False
        session_id = request.get_cookie('session_id')
        if not session_id:
            return func(login_data, *args, **kwargs)
        login_data = sessions.check(session_id)
        if not login_data:
            return func(login_data, *args, **kwargs)
        return func(login_data, *args, **kwargs)
    return wrapper

@auth_check
@blog_app.route('/')
@blog_app.route('/page/<page_id>')
def show_listing(login_data=False, page_id=None,):
    page_id = 1 if not page_id else int(page_id)
    posts = entries.get_posts(page_id)
    if not posts:
        abort(404, "Not Found")
    recent = entries.get_recent()
    return template('main', settings, page_id=page_id,
                    user_login=login_data,posts=posts, recent_posts=recent)

@auth_check
@blog_app.route('/<url:re:[a-z0-9]{6}>')
@blog_app.route('/<year:int>/<url>')
def show_post(url, login_data=False, year=False,):
    post_data = entries.get_post(url, year=year)
    if not post_data:
        abort(404, "Not Found")
    return template('post', settings, sub_title=post_data['title'],
                    post=post_data, user_login=login_data)

@blog_app.route('/archive')
def show_archives():
    login_data = check_login()
    return template('archive', settings, sub_title='Archives',
                    user_login=login_data, special=entries.get_archive())

@blog_app.route('/special/<page_name>')
def show_special(page_name, ):
    login_data = check_login()
    page = entries.get_page(page_name)
    if not page:
        abort(404, "Not Found")
    return template('special', settings, sub_title=page['title'],
                    user_login=login_data, page=page)

@blog_app.route('/tags/<tag_name>')
def show_tags(tag_name, ):
    login_data = check_login()
    tag_name = tag_name.replace('-',' ')
    post_by_tags = entries.get_by_tags([tag_name])
    return template('tags', settings, sub_title='Posts Tagged %s' % tag_name,
                    tag=tag_name, posts=post_by_tags, user_login=login_data)


@blog_app.route('/logout')
def logout():
    login_data = check_login()
    if login_data:
        s_id = request.get_cookie('session_id')
        sessions.expire(s_id)
        response.delete_cookie(s_id)
    redirect('/')

# Admin functions
@blog_app.route('/admin')
def show_admin():
    login_data = check_login(abort_on_fail=True)
    return template('admin/main', settings, user_login=login_data)

@blog_app.route('/admin/new-post')
def show_new_post():
    login_data = check_login(abort_on_fail=True)
    return template('admin/post_editor', settings, user_login=login_data)

@blog_app.route('/admin/comment-approver')
def show_pending_comments():
    login_data = check_login(abort_on_fail=True)
    comments = entries.get_unapproved_comments()
    return template('admin/comments', settings, user_login=login_data,
                    comments=comments, )

@blog_app.route('/admin/post-editor/<post_id:re:[a-z0-9]{6}>')
def show_post_editor(post_id, ):
    login_data = check_login(abort_on_fail=True)
    post = entries.get_post(post_id, output_html=False, )
    if not post:
        abort(404, "Not Found")
    return template('admin/post_editor', settings, user_login=login_data,
                    post_data=post, )

@blog_app.route('/admin/view-profile')
def show_profile():
    login_data = check_login(abort_on_fail=True)
    profile_data = users.get_user(login_data)
    if not profile_data:
        abort("404", "Not Found")
    return template("admin/profile_editor", settings, user_login=login_data,
                    profile_data=profile_data, )

# API
@blog_app.route('/api/comment', method='POST')
def create_comment():
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
    return_data['msg'] = "Comment submitted for approval, Thank you."
    return return_data

@blog_app.route('/api/login', method='POST')
def login():
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
    session = sessions.new(user['_id'])
    response.set_cookie('session_id', session['session_id'],
                        expires=session['expiry'], path='/', )
    return return_data

@blog_app.route('/api/post', method='GET')
@blog_app.route('/api/post/<page_num:int>', method='GET')
def get_posts(page_num=1, ):
    return_data = {'posts': []}
    return_data['posts'] = entries.get_posts(page_num)
    for i in xrange(0, len(return_data['posts'])):
        post = return_data['posts'][i]
        post['date'] = str(post['date'])
        del post['comments']
        del post['body']
    return return_data

@blog_app.route('/api/post/<post_id>', method='GET')
def get_post(post_id, ):
    post_data = {'post': {}}
    post = entries.get_post(post_id)
    if post:
        post['date'] = str(post['date'])
        for j in xrange(0, len(post['comments'])):
            comment = post['comments'][j]
            comment['date'] = str(comment['date'])
        post_data['post'] = post
    return post_data

# Admin API - Auth required
@blog_app.route('/api/comment/<comment_id>', method='PUT')
def comment_approve(comment_id, ):
    login_data = check_login(abort_on_fail=True)
    entries.approve_comment(comment_id)
    return {}

@blog_app.route('/api/comment/<comment_id>', method='DELETE')
def comment_deny(comment_id, ):
    login_data = check_login(abort_on_fail=True)
    entries.deny_comment(comment_id)
    return {}
    

@blog_app.route('/api/admin/post', method='POST')
def create_post():
    login_data = check_login(abort_on_fail=True)
    return_data = {'error': False}
    fields = ['title', 'body', 'tags', 'public']
    req_data = sterilize(request.json, fields)
    if not req_data:
        return_data['error'] = 'Missing Parameters'
        return return_data
    post_data = dict((key, value) for (key, value) in req_data.items())
    post_data['tags'] = [tag.strip() for tag in post_data['tags'].split(',')]
    new_post = entries.create_post(post_data, login_data, entries.POST_NS)
    if not new_post:
        return_data['error'] = 'Failed to create post!'
        return return_data
    return_data['location'] = new_post
    return return_data


@blog_app.route('/api/admin/post/<post_id>', method='DELETE')
def delete_post(post_id, ):
    login_data = check_login(abort_on_fail=True)
    return_data = {'error': False}
    if not entries.delete_post(post_id):
        return_data['error'] = 'Invalid Post ID'
        return return_data
    return return_data


@blog_app.route('/api/admin/post/<post_id>', method='PUT')
def edit_post(post_id, ):
    login_data = check_login(abort_on_fail=True)
    return_data = {'error': False}
    req_data = request.json
    post = entries.get_post(post_id, output_html=False, show_name=False)
    if not post:
        return_data['error'] = 'Invalid Post ID'
        return return_data
    post_data = dict((key, post[key]) for key in post)
    for key in post_data:
        if key in req_data:
            post_data[key] = req_data[key]
    url = entries.edit_post(post_id, post_data)
    if not url:
        return_data['error'] = 'Error Updating post'
    return_data['location'] = url
    return return_data


@blog_app.route('/api/admin/profile/changepassword', method='PUT')
def change_password():
    login_data = check_login(abort_on_fail=True)
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
@blog_app.error(404)
@blog_app.error(405)
@blog_app.error(500)
def error_handler(error, ):
    err_msgs = {'500 Internal Server Error':
                'We encountered a server error while processing your request.',
                '401 Unauthorized': 'You are not authorized to be here.',
                '404 Not Found': 'The page you are looking for can\'t be found.',
                '405 Method Not Allowed': 'You can\'t do that!',
                }
    err_msg = 'Something really bad happened!'
    try:
        err_msg = err_msgs[response.status]
    except KeyError:
        pass
    if settings['debug'] and error.traceback:
        err_msg = '<pre>%s</pre>' % error.traceback
    return template('error', settings, error=err_msg,)

def check_login(abort_on_fail=False):
    session_id = request.get_cookie('session_id')
    if not session_id:
        if abort_on_fail:
            redirect('/')
        else:
            return False
    session_user = sessions.check(session_id)
    if not session_user:
        if abort_on_fail:
            redirect('/')
        else:
            return False
    return session_user

def sterilize(data, required_fields, ):
    return_data = {}
    for key in required_fields:
        if key not in data:
            return False
        return_data[key] = data[key]#str(utils.escape(data[key]))
            
    return return_data
