#!/usr/bin/env python

import db
import itertools as it
import jinja2
import json
import os
import random
import string
import urllib2
import webapp2

from google.appengine.ext import ndb


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
        companies = ['airbnb', 'uber', 'dropbox', 'lyft', 'venmo']
        self.render('homepage.html', companies=companies)


class UserPage(BaseHandler):
    def get(self):
        self.render('topsite.html')


class CompanyPage(BaseHandler):
    def get(self, company):
        code1 = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
        code2 = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
        self.render('company_page.html', company=company.lower(),
            code1=code1, code2=code2)


app = webapp2.WSGIApplication([
    ('/?', MainHandler),
    ('/home?', HomepageHandler),
    ('/([a-zA-Z0-9_]+)/?', UserPage),
    ('/c/([a-zA-Z0-9_]+)/?', CompanyPage),
], debug=True)
