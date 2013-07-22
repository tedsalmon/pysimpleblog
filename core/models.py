#!/usr/bin/env python
# -*- coding: utf-8 -*-
from creole import Parser
from creole.html_emitter import HtmlEmitter
from datetime import datetime
from hashlib import sha256, sha512
from pymongo import MongoClient, errors as pymongoerrors
from random import randint
from pysimpleblog.core.functions import b36encode
from pysimpleblog.core.functions import UTCDate

DB_CONN = MongoClient('localhost')

class Blog(object):
    
    POST_NS = 0
    PAGE_NS = 1

    def __init__(self, db_conn=False, ):
        self._client = db_conn if db_conn else DB_CONN
        self._db_handle = self._client.blog
        self.blog_db = self._db_handle.entries
        self.users_db = self._db_handle.users
    
    
    def _create_id(self, ):
        time = int(UTCDate().strftime("%s"))
        return b36encode(time+randint(0,9001)).lower()
    
    
    def approve_comment(self, comment_id, ):
        return self.blog_db.update({"comments.id": comment_id},
                                   {"$set": {"comments.approval": 1}})
    
    
    def create_comment(self, comment_data, post_id, post_data=None, ):
        if not post_data:
            post_data = self.get_post(post_id)
            if not post_data:
                return False
        comment_data['id'] = self._create_id()
        comment_data['date'] = UTCDate()
        comment_data['approval'] = 0
        return self.blog_db.update({"_id": post_data['_id']},
                            {"$push": {"comments": comment_data}})
    

    def create_post(self, data, author, data_ns, ):
        s_title = data['title'].split(' ')
        if len(s_title) > 1:
            s_title = [s for s in s_title if s.isalpha() or s.isdigit()]
        else:
            s_title = [''.join([s for s in s_title[0] if s.isalpha() or s.isdigit()])]
        url_name = '-'.join(s_title[0:5 if len(s_title) >= 6
                                    else len(s_title)]).lower()
        post_id = self._create_id()
        now = UTCDate()
        post_data = {
            "_id": post_id,
            "title": data['title'],
            "author": author,
            "body": data['body'],
            "url": url_name,
            "date": now,
            "type": data_ns,
            "tags": data['tags'],
            "public": int(bool(data['public'])),
            "comments": []}
        self.blog_db.insert(post_data)
        return url_name
    
    
    def delete_post(self, post_id, ):
        return self.blog_db.remove({"_id": post_id})
    
    def edit_post(self, post_data, ):
        if type(post_data['tags']) != list:
            post_data['tags'] = [tag.strip() for tag in
                                 post_data['tags'].split(',')]
        return self.blog_db.update({"_id": post_data['_id']}, post_data)
    
    def get_archive(self, ):
        return_data = {}
        posts = self.blog_db.find({'type': self.POST_NS}).sort('date', -1)
        for post in posts:
            year = post['date'].strftime('%Y')
            if year not in return_data:
                return_data[year] = []
            return_data[year].append(post)
        return return_data
    
    
    def get_by_tags(self, tags, ):
        posts = []
        tags_q = {'tags': {'$in': tags}, 'type': self.POST_NS}
        posts_found = self.blog_db.find(tags_q).sort("date", -1).limit(10)
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
        return posts


    def get_post(self, url, year=None, output_html=True, show_name=True, ):
        query = {}
        if year:
            query = {'url': url,
                     'date': {'$gte': datetime(year,1,1),
                               '$lte':datetime(year,12,31)},
                     'public': 1, 'type': self.POST_NS
                    }
        else:
            query = {'_id': url, 'public': 1, 'type': self.POST_NS}
        post = self.blog_db.find_one(query)
        if post:
            comments = []
            for comment in post['comments']:
                if comment['approval']:
                    comments.append(comment)
            post['comments'] = comments
            author = self.users_db.find_one({"_id": post['author']})
            post['author'] = author['display_name'] if show_name else author['_id']
            if output_html:
                post['body'] = HtmlEmitter(Parser(post['body']).parse()).emit()
        return post
    
    
    def get_posts(self, page_num, ):
        skip = 0 if page_num == 1 else 10 * (page_num-1)
        posts = []
        for post in self.blog_db.find({'type': self.POST_NS, 'public': 1}
                                     ).sort('date', -1).limit(10).skip(skip):
            approved_comments = []
            for comment in post['comments']:
                if comment['approval'] == 1:
                    approved_comments.append(comment)
            author = self.users_db.find_one({"_id": post['author']})
            post['author'] = author['display_name']
            post['body'] = HtmlEmitter(Parser(post['body']).parse()).emit()
            post['comment_count'] = len(approved_comments)
            posts.append(post)
        return posts
    
    
    def get_recent(self, ):
        return self.blog_db.find({'type': self.POST_NS, 'public': 1},
                                 fields=['url', 'title']
                                 ).sort('date', -1).limit(10)
    
    def get_page(self, name, ):
        post = self.blog_db.find_one({'url': name, 'type': self.PAGE_NS})
        if post:
            post['body'] = HtmlEmitter(Parser(post['body']).parse()).emit()
        return post
    
    
    def get_unapproved_comments(self, ):
        comments = []
        pending_comments = self.blog_db.find({"comments.approval": 0},
                                    fields=['comments']
                                    ).sort("date", -1)
        for post in pending_comments:
            for comment in post['comments']:
                if comment['approval'] == 0:
                    comments.append(comment)
        return comments

class Links(object):
    
    def __init__(self, db_conn=False, ):
        self._client = db_conn if db_conn else DB_CONN
        self._db_handle = self._client.blog
        self.links = self._db_handle.links
    
    def add_link(self, url, name, ):
        return self.links.insert({'url': url, 'title': name,})
    
    def delete_link(self, link_id, ):
        return self.links.remove({"_id": link_id})
    
    def edit_link(self, link_data, ):
        return self.links.update(link_data)
    
    def get_list(self, ):
        links = []
        for link in self.links.find():
            links.append(link)
        return links
    

class Sessions(object):
    
    def __init__(self, db_conn=False, ):
        self._client = db_conn if db_conn else DB_CONN
        self._db_handle = self._client.blog
        self.session_db = self._db_handle.sessions
        self.user_db = self._db_handle.users
    
    def _clean_up(self, ):
        return self.session_db.remove({"expiry": {"$lte": UTCDate()}})
        
    def check(self, session_id):
        self._clean_up()
        session = self.session_db.find_one({"session_id": session_id})
        if session:
            return session['user_id']
        return False
    
    def expire(self, s_id):
        return self.session_db.remove({"session_id": s_id})    
    
    def new(self, user_data, ):
        self._clean_up()
        expiry = UTCDate(-86400)
        user_session = {"user_id": user_data['_id'],
                        "session_id":
                            sha256("%s%s" % (expiry.strftime("%s"),
                                             randint(0, 9000))).hexdigest(),
                        "expiry": expiry,
                        }
        self.session_db.insert(user_session)
        return user_session
    
    
class Users(object):
    
    def __init__(self, db_conn=False, ):
        self._client = db_conn if db_conn else DB_CONN
        self._db_handle = self._client.blog
        self.db = self._db_handle.users
        self.error = ""
        
    
    def _make_hash(self, salt, password, ):
        return sha512("%s%s" % (password, salt)).hexdigest()
    
    
    def _make_salt(self, ):
        random_num = randint(0, 900000)
        time_now = UTCDate().strftime("%s")
        full_salt = sha512("%s%s" % (random_num, time_now)).hexdigest()
        salt = "%s%s" % (full_salt[:5], full_salt[-5:])
        return salt
    
    
    def create_user(self, username, password, display_name=None):
        if not display_name:
            display_name = username
        salt = self._make_salt()
        pw_hash = self._make_hash(salt, password)
        new_user = {"_id": username, "password": pw_hash,
                    "salt": salt, "create_date": UTCDate(),
                    "display_name": display_name}
        try:
            self.db.insert(new_user)
        except pymongoerrors.DuplicateKeyError:
            self.error = "User already exists"
            return False
        return True
    
    
    def delete_user(self, username, ):
        return self.db.remove({"_id": username})
    
    
    def edit_user(self, username, user_data, ):
        user_data['_id'] = username
        return self.db.update(user_data)
    
    
    def edit_password(self, username, password, new_password, ):
        if not self.verify_login(username, password):
            self.error = "Invalid Password"
            return False
        salt = self._make_salt()
        new_hash = self._make_hash(salt, new_password)
        return self.db.update({"_id": username},
                        {"$set": {"password": new_hash},
                         "$set": {"salt": salt}})


    def get_user(self, username, ):
        return self.db.find_one({"_id": username})
    
    
    def get_users(self, ):
        users = []
        for user in self.db.find(fields=['username', 'display_name']):
            users.append(user)
        return users

    
    def verify_login(self, username, password, ):
        user_data = self.db.find_one({"_id": username})
        if not user_data:
            self.error = "Invalid Login"
            return False
        given_pw_hash = self._make_hash(user_data['salt'], password)
        if given_pw_hash != user_data['password']:
            self.error = "Invalid Username/Password"
            return False
        return user_data