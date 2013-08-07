#!/usr/bin/env python
# -*- coding: utf-8 -*-
from creole import Parser
from creole.html_emitter import HtmlEmitter
from datetime import datetime
from hashlib import sha256, sha512
from jinja2 import utils
from pymongo import MongoClient, errors as pymongoerrors
from random import randint
from pysimpleblog.core.functions import b36encode, Settings, UTCDate

_s = Settings()
DB_SETTINGS = _s['database']
DB_CONN = MongoClient(DB_SETTINGS['address'])


def Validate(data, fields, require_all=True, ):
    return_data = {}
    if not data:
        return False
    for field, settings in fields.items():
        if field in data:
            val = data[field]
            if settings['escape']:
                val = str(utils.escape(val))
            if 'type' in settings:
                val = settings['type'](val)
            return_data[field] = val
        else:
            if require_all and settings['required']:
                return False
    return return_data


class Blog(object):
    
    POST_NS = 0
    PAGE_NS = 1
    
    COMMENT_FIELDS = {
        'name': {'reqired': 1, 'escape': 1},
        'email': {'reqired': 1, 'escape': 1},
        'body': {'reqired': 1, 'escape': 1},
    }
    ENTRY_FIELDS = {
        'title': {'reqired': 1, 'escape': 1},
        'body': {'reqired': 1, 'escape': 0},
        'tags': {'reqired': 0, 'escape': 1},
        'status': {'reqired': 1, 'escape': 1, 'type': int},
        'type': {'reqired': 1, 'escape': 1, 'type': int}
    }
    
    def __init__(self, db_conn=False, ):
        self._client = db_conn if db_conn else DB_CONN
        self._db_handle = self._client[DB_SETTINGS['name']]
        self.blog_db = self._db_handle.entries
        self.users_db = self._db_handle.users
        self.error = False
    
    def _create_id(self, ):
        time = int(UTCDate().strftime('%s'))
        return b36encode(time+randint(0,9001)).lower()
    
    
    def _create_urlslug(self, title, maxl=8, ):
        title = title.strip().split(' ')
        if len(title) > 1:
            title = [s for s in title if s.isalpha() or s.isdigit()]
        else:
            temp = []
            for char in title[0]:
                if char.isalpha() or char.isdigit():
                    temp.append(char)
            title = [''.join(temp)]
        return '-'.join(title[0:(maxl-1)]).lower()
    

    def approve_comment(self, post_id, comment_id, ):
        res = self.blog_db.update({'_id': post_id, 'comments':
                                   {'$elemMatch': {'id': comment_id}}},
                                   {'$set': {'comments.$.approval': 1}})
        if not res['n']:
            self.error = 'Invalid comment ID'
        return res['n']
    
    
    def create_comment(self, post_id, form_data, ):
        comment_data = Validate(form_data, self.COMMENT_FIELDS)
        if not comment_data:
            self.error = 'Parent post not found.'
            return False
        comment_data['id'] = self._create_id()
        comment_data['date'] = UTCDate()
        comment_data['approval'] = 0
        res = self.blog_db.update({'_id': post_id},
                            {'$push': {'comments': comment_data}})
        if not res['n']:
            self.error = 'Error inserting comment'
        return res['n']
    

    def create_post(self, data, author, url_slug=None, ):
        entry_data = Validate(data, self.ENTRY_FIELDS)
        if not entry_data:
            self.error = 'Missing/Invalid parameters'
            return False
        if not url_slug:
            url_slug = self._create_urlslug(entry_data['title'])
        now, post_id = UTCDate(), self._create_id()
        post_data = {
            '_id': post_id,
            'title': entry_data['title'],
            'author': author,
            'body': entry_data['body'],
            'url': url_slug,
            'date': now,
            'type': int(bool(entry_data['type'])),
            'tags': [tag.strip() for tag in entry_data['tags'].split(',')],
            'status': int(bool(entry_data['status'])),
            'comments': []}
        if self.blog_db.insert(post_data):
            return self.get_uri(post_id, post_data)
        self.error = 'Error creating post'
        return False
    
    
    def delete_post(self, post_id, ):
        res = self.blog_db.remove({'_id': post_id})
        if not res['n']:
            self.error = 'Invalid post ID'
        return res['n']
    
    
    def deny_comment(self, post_id, comment_id, ):
        res = self.blog_db.update({'_id': post_id, 'comments':
                                   {'$elemMatch': {'id': comment_id}}},
                                   {'$set': {'comments.$.approval': -1}})
        if not res['n']:
            self.error = 'Invalid comment ID'
        return res['n']
    
    def edit_post(self, post_id, data, ):
        updates = {'$set': {}}
        entry_data = Validate(data, self.ENTRY_FIELDS, require_all=False)
        if not entry_data:
            self.error = 'Missing/invalid parameters'
            return False
        if 'tags' in entry_data:
            if type(entry_data['tags']) != list:
                entry_data['tags'] = [tag.strip() for tag in
                                      entry_data['tags'].split(',')]
        for key, value in entry_data.items():
            updates['$set'][key] = value
        if 'title' in entry_data:
            updates['$set']['url'] = self._create_urlslug(entry_data['title'])
        res = self.blog_db.update({'_id': post_id}, updates)
        if not res['n']:
            self.error = 'Error updating post'
        return res['n']
    
    
    def get_archive(self, ):
        return_data = {}
        posts = self.blog_db.find({'type': self.POST_NS,
                                   'status': 1}).sort('date', -1)
        for post in posts:
            year = post['date'].strftime('%Y')
            if year not in return_data:
                return_data[year] = []
            return_data[year].append(post)
        return return_data
    
    
    def get_by_tags(self, tags, ):
        posts = []
        tags_q = {'tags': {'$in': tags}, 'type': self.POST_NS, 'status': 1}
        posts_found = self.blog_db.find(tags_q).sort('date', -1).limit(10)
        for post in posts_found:
            approved_comments = []
            for comment in post['comments']:
                if comment['approval'] == 1:
                    approved_comments.append(comment)
            author = self.users_db.find_one({'_id': post['author']})
            post['author'] = author['display_name']
            post['body'] = HtmlEmitter(Parser(post['body']).parse()).emit()
            post['comment_count'] = len(approved_comments)
            posts.append(post)
        if not posts:
            self.error = 'Posts not found'
        return posts
    
    
    def get_last_error(self, ):
        error = self.error
        self.error = False
        return error


    def get_post(self, url, year=None, auth=False, ):
        query = {}
        if year:
            query = {'url': url,
                     'date': {'$gte': datetime(year,1,1),
                              '$lte': datetime(year,12,31)},
                     'status': 1, 'type': self.POST_NS
                    }
        else:
            query = {'$or': [{'_id': url}, {'url': url}],
                     'status': 1, 'type': self.POST_NS}
        if auth:
            del query['status']
        post = self.blog_db.find_one(query)
        if post:
            comments = []
            for comment in post['comments']:
                if comment['approval']:
                    comments.append(comment)
            post['comments'] = comments
            author = self.users_db.find_one({'_id': post['author']})
            post['author'] = author['display_name']
            post['body'] = HtmlEmitter(Parser(post['body']).parse()).emit()
        else:
            self.error = 'Post not found'
        return post
    
    
    def get_posts(self, page_num, all_posts=False, ):
        skip = 0 if page_num == 1 else 10 * (page_num-1)
        if all_posts:
            found = self.blog_db.find().sort('date', -1).limit(10).skip(skip)
        else:
            qry = {'type': self.POST_NS, 'status': 1}
            found = self.blog_db.find(qry).sort('date', -1).limit(10).skip(skip)
        posts = []
        for post in found:
            approved_comments = []
            for comment in post['comments']:
                if comment['approval'] == 1:
                    approved_comments.append(comment)
            author = self.users_db.find_one({'_id': post['author']})
            post['author'] = author['display_name']
            post['body'] = HtmlEmitter(Parser(post['body']).parse()).emit()
            post['comment_count'] = len(approved_comments)
            posts.append(post)
        if not posts:
            self.error = 'Posts not found'
        return posts
    
    
    def get_post_internal(self, url, ):
        post = self.blog_db.find_one({'$or': [{'_id': url}, {'url': url}]})
        return post
    
    
    def get_post_clean(self, url, year=None,):
        post = self.get_post(url, year)
        if post:
            post['date'] = post['date'].strftime('%Y-%m-%d %H:%M:%S')
            for comment in post['comments']:
                comment = post['comments'][j]
                comment['date'] = comment['date'].strftime('%Y-%m-%d %H:%M:%S')
        return post
    
    
    def get_post_list(self, page_num, ):
        posts = self.get_posts(page_num)
        for post in posts:
            post['date'] = post['date'].strftime('%Y-%m-%d %H:%M:%S')
            del post['comments']
            del post['body']
        return posts
    
    
    def get_recent(self, ):
        q = self.blog_db.find({'type': self.POST_NS, 'status': 1},
                                 fields=['url', 'title', 'date']
                                 ).sort('date', -1).limit(10)
        recent_posts = []
        for post in q:
            recent_posts.append(post)
        if not recent_posts:
            self.error = 'Posts not found'
        return recent_posts

    
    def get_page(self, name, ):
        post = self.blog_db.find_one({'url': name, 'type': self.PAGE_NS})
        if post:
            post['body'] = HtmlEmitter(Parser(post['body']).parse()).emit()
        return post
    
    
    def get_uri(self, post_id, post=None, ):
        if not post:
            post = self.blog_db.find_one({'_id': post_id})
        if post:
            if post['type'] == self.POST_NS:
                return '%s/%s' % (post['date'].strftime('%Y'), post['url'])
            else:
                return 'special/%s' % post['url']
        self.error = 'Post not found'
        return False
    
    
    def get_unapproved_comments(self, ):
        comments = []
        pending_comments = self.blog_db.find({'comments.approval': 0},
                                    fields=['comments']
                                    ).sort('date', -1)
        for post in pending_comments:
            for comment in post['comments']:
                if comment['approval'] == 0:
                    comment['post_id'] = post['_id']
                    comments.append(comment)
        return comments


class Links(object):
    
    LINK = {
        'url': {'required': 1, 'escape': 1},
        'title': {'required': 1, 'escape': 1},
    }
    
    def __init__(self, db_conn=False, ):
        self._client = db_conn if db_conn else DB_CONN
        self._db_handle = self._client[DB_SETTINGS['name']]
        self.users = self._db_handle.users
        self.links = self._db_handle.links
        self.error = False

    
    def _create_id(self, ):
        time = int(UTCDate().strftime('%s'))
        return b36encode(time+randint(0,9001)).lower()

    
    def create_link(self, link_data, author, ):
        link_id = self._create_id()
        link_data = Validate(link_data, self.LINK)
        if not link_data:
            self.error = 'Missing/Invalid Parameters'
            return False
        self.links.insert({'_id': link_id,
                           'url': link_data['url'],
                           'title': link_data['title'],
                           'author': author})
        return link_id

    
    def delete_link(self, link_id, ):
        res = self.links.remove({'_id': link_id})
        if not res['n']:
            self.error = 'Link ID not found'
        return res['n']

    
    def edit_link(self, link_id, link_data, ):
        updates = {'$set': {}}
        link_data = Validate(link_data, self.LINK, require_all=False)
        if not link_data:
            self.error = 'Missing/Invalid Parameters'
            return False
        for key, value in link_data.items():
            updates['$set'][key] = value
        res = self.links.update({'_id': link_id}, updates)
        if not res['n']:
            self.error = 'Link ID not found'
        return res['n']
    
    
    def get_last_error(self, ):
        error = self.error
        self.error = False
        return error
    
    
    def get_link(self, link_id, ):
        return self.links.find_one({'_id': link_id})
    
    def get_links(self, cannonical_author=False, ):
        links = []
        for link in self.links.find():
            if cannonical_author:
                author = self.users.find_one({'_id': link['author']})
                link['author'] = author['display_name']
            links.append(link)
        return links
    

class Sessions(object):
    
    def __init__(self, db_conn=False, ):
        self._client = db_conn if db_conn else DB_CONN
        self._db_handle = self._client[DB_SETTINGS['name']]
        self.session_db = self._db_handle.sessions

    
    def _clean_up(self, ):
        query = {'$or': [{'expiry': {'$lte': UTCDate()}}, {'expiry': None}]}
        return self.session_db.remove(query)
    
    
    def create_session(self, user_id, session_lifespan=False, ):
        self._clean_up()
        s_id = sha256('%s%s' % (UTCDate(), randint(0, 9000))).hexdigest()
        if session_lifespan:
            s_len = UTCDate(session_lifespan)
        else:
            s_len = UTCDate(-86400)
        user_session = {'user_id': user_id, 'session_id': s_id, 'expiry': s_len}
        self.session_db.insert(user_session)
        return user_session
    
    
    def expire_session(self, s_id):
        self._clean_up()
        res = self.session_db.remove({'session_id': s_id})
        return res['n']
    
    
    def verify_session(self, session_id):
        self._clean_up()
        session = self.session_db.find_one({'session_id': session_id})
        if session:
            return session['user_id']
        return session
    
    
class Users(object):
    
    LOGIN = {
        'username': {'reqired': 1, 'escape': 0},
        'password': {'reqired': 1, 'escape': 0},
    }
    
    USER = {
        'username': {'reqired': 1, 'escape': 1},
        'password': {'reqired': 1, 'escape': 0},
        'display_name': {'reqired': 1, 'escape': 1},
        'email_address': {'reqired': 1, 'escape': 1}
    }
    
    def __init__(self, db_conn=False, ):
        self._client = db_conn if db_conn else DB_CONN
        self._db_handle = self._client[DB_SETTINGS['name']]
        self.db = self._db_handle.users
        self.error = ''
        
    
    def _make_hash(self, salt, password, ):
        return sha512('%s%s' % (password, salt)).hexdigest()
    
    
    def _make_salt(self, ):
        random_num = randint(0, 900000)
        time_now = UTCDate().strftime('%s')
        full_salt = sha512('%s%s' % (random_num, time_now)).hexdigest()
        salt = '%s%s' % (full_salt[:5], full_salt[-5:])
        return salt
    
    
    def create_user(self, user_data, ):
        user_data = Validate(user_data, self.USER)
        if not user_data:
            self.error = 'Missing/Invalid Paramters'
            return False
        salt = self._make_salt()
        new_user = {
            '_id': user_data['username'],
            'password': self._make_hash(salt, user_data['password']),
            'salt': salt,
            'create_date': UTCDate(),
            'email_address': user_data['email_address'],
            'display_name': user_data['display_name']
        }
        try:
            self.db.insert(new_user)
        except pymongoerrors.DuplicateKeyError:
            self.error = 'User already exists'
            return False
        return True
    
    
    def delete_user(self, username, ):
        res = self.db.remove({'_id': username})
        if not res['n']:
            self.error = 'User not found'
        return res['n']
    
    
    def edit_user(self, username, user_data, ):
        updates = {'$set': {}}
        user_data = Validate(user_data, self.USER, require_all=False)
        if not user_data:
            self.error = 'Missing/Invalid Parameters'
            return False
        for key, value in user_data.items():
            updates['$set'][key] = value
        res = self.db.update({'_id': username}, updates)
        if not res['n']:
            self.error = 'User not found'
        return res['n']
    
    
    def edit_password(self, username, password_data, ):
        if not self.verify_login(username, password_data['password']):
            self.error = 'Invalid Password'
            return False
        salt = self._make_salt()
        new_hash = self._make_hash(salt, password_data['new_password'])
        res = self.db.update({'_id': username},
                             {'$set': {'password': new_hash},
                              '$set': {'salt': salt}})
        if not res['n']:
            self.error = 'User not found'
        return res['n']
    
    
    def get_last_error(self, ):
        error = self.error
        self.error = False
        return error


    def get_user(self, username, ):
        return self.db.find_one({'_id': username})
    
    
    def get_users(self, ):
        users = []
        fields = ['username', 'display_name', 'email_address']
        for user in self.db.find(fields=fields):
            users.append(user)
        return users


    def verify_login(self, login_data, ):
        login_data = Validate(login_data, self.LOGIN)
        if not login_data:
            self.error = 'Invalid login. Please try again.'
            return False
        user_data = self.db.find_one({'_id': login_data['username']})
        if not user_data:
            self.error = 'Invalid login. Please try again.'
            return False
        given_pw_hash = self._make_hash(user_data['salt'], login_data['password'])
        if given_pw_hash != user_data['password']:
            self.error = 'Invalid login. Please try again.'
            return False
        return user_data