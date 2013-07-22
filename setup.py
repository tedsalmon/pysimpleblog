#!/usr/bin/python
# -*- coding: utf-8 -*-
from getpass import getpass
from core.models import Users

user = Users()
if not user.get_users():
    print 'It appears there are no users setup - Please setup a user'
    username = False
    while not username:
        username = input('Username: ')
    display_name = False
    while not display_name:
        display_name = input('Display Name: ')
    password = getpass()
    password_again = getpass(prompt='Confirm Password: ')
    if password != password_again:
        print 'Passwords must match! Aborting!'
        exit(1)
    user.create_user(username, password, display_name)
        


