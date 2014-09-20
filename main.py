#!/usr/bin/env python

import webapp2
import jinja2
import json
import os
import urllib2

from google.appengine.ext import ndb
from google.appengine.api import urlfetch


jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


def render_str(template, **params):
    t = jinja_environment.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class MainHandler(BaseHandler):
    def get(self):
        self.response.write('Hello world!')


class UserHandler(BaseHandler):
    def post(self):
        fb_id = self.request.get('fb_id')

        # create new user
        new_user = User(id=fb_id, full_name='Michael B')

        new_user.put()

    def get(self, id):
        user_key = ndb.Key(User, id)
        user = user_key.get()

        self.write(user)



class User(ndb.Model):
    # key = fb user id
    full_name = ndb.StringProperty(required=True)
    friends = ndb.StringProperty(repeated=True)
    # serialize JSON here
    # format:
    # Array with Objects with service string and codes array
    services = ndb.TextProperty(default='[]')


app = webapp2.WSGIApplication([
    ('/?', MainHandler),
    ('/user/?', UserHandler),
    ('/user/([0-9]+)/?', UserHandler)
], debug=True)
