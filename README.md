pysimpleblog
============

A Simple blogging framework written in Python with the help of Bottle and MongoDB as a backend.

Why?
===

I started this project because I didn't want to use WordPress and also so that I could get more exposure to MongoDB and Bottle.py.

Features
========

* Simple, easy to use interface.
* RESTful API! (Docoumentation comming)


Roadmap
=======

Currently, not all features that I would like have been implemented. Here's a list of features waiting to be implemented by order of urgency.

* User Management
* Image uploads
* More comprehensive setup via setup.py

Requirements
============

* Python 2.6+
* Jinja2
* Bottle 0.11+
* PyMongo
* Python Creole

* MongoDB 2.2.0+

Setup
=====

1. Clone the repo wherever you would like

2. Edit settings.json with your settings

3. Run `python setup.py` to create an account and the `run python app.wsgi` to start the web app in the Python debug server. The app.wsgi file is already mod_wsgi compatible.
