#!/usr/bin/env python

import jinja2
import json
import os
import urllib2
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import urlfetch


class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class UserHandler(BaseHandler):
    def post(self, fb_id):
        # check if user already cretead
        user = ndb.Key(User, fb_id).get()
        if user:
            self.error(500)
            return

        # create new user
        full_name = self.request.get('full_name')
        new_user = User(id=fb_id, full_name=full_name)

        new_user.put()

    def get(self, fb_id):
        user_key = ndb.Key(User, fb_id)
        user = user_key.get()

        if not user:
            self.error(404)
            return

        user_dict = {}
        user_dict['fb_id'] = user.key.id()
        user_dict['friends'] = user.friends
        user_dict['services'] = user.services

        self.write(json.dumps(user_dict))


class AllServicesHandler(BaseHandler):
    def get(self, fb_id):
        user = ndb.Key(User, fb_id).get()
        if not user:
            self.error(404)
            return

        self.write(user.services)


class ServiceHandler(BaseHandler):
    def get(self, fb_id, service):
        user = ndb.Key(User, fb_id).get()
        if not user:
            self.error(404)
            return
        services_dict = json.loads(user.services)

        codes = services_dict.get(service, '[]')
        self.write(json.dumps(codes))

    def post(self, fb_id, service):
        user = ndb.Key(User, fb_id).get()
        if not user:
            self.error(404)
            return

        services_dict = json.loads(user.services)
        if service in services_dict:
            services_dict[service].append(code)
        else:
            services_dict[service] = [self.request.get('code')]
        user.services = json.dumps(services_dict)
        user.put()



class User(ndb.Model):
    # key = fb user id
    full_name = ndb.StringProperty(default='User')
    friends = ndb.StringProperty(repeated=True)
    # serialize JSON here, format:
    # Array with Objects with service string and codes array
    services = ndb.TextProperty(default='{}')


app = webapp2.WSGIApplication([
    ('/users/([0-9]+)/?', UserHandler),
    ('/users/([0-9]+)/services/?', AllServicesHandler),
    ('/users/([0-9]+)/services/([a-zA-Z0-9!_-]+)/?', ServiceHandler)
], debug=True)