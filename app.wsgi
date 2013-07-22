#!/usr/bin/env python
import os
import sys
# Append lamp dir to path and then chdir to it
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append('%s/../' % current_path)
os.chdir(current_path)
# Import PySimpleBlog as Application
from pysimpleblog.blog import blog_app as application
# Run our app in debug if called by shell
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8081, reloader=True, debug=True)
