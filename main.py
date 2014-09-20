#!/usr/bin/env python

import db
import jinja2
import json
import os
import urllib2
import webapp2

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
        self.render('index.html')


class HomepageHandler(BaseHandler):
    def get(self):
        self.render('homepage.html')


class UserPage(BaseHandler):
    def get(self, username):
        self.render('topsite.html')

class CompanyPage(BaseHandler):
    def get(self, username):
        self.render('company_page.html')


app = webapp2.WSGIApplication([
    ('/?', MainHandler),
    ('/home?', HomepageHandler),
    ('/([a-zA-Z0-9_]+)/?', UserPage),
    ('/c/([a-zA-Z0-9_]+)/?', CompanyPage),
], debug=True)
