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
        user_dict['full_name'] = user.full_name
        user_dict['friends'] = user.friends
        user_dict['services'] = json.loads(user.services)

        self.write(json.dumps(user_dict))


class FriendHandler(BaseHandler):
    def get(self, fb_id):
        user = ndb.Key(User, fb_id).get()
        if not user:
            self.error(404)
            return

        self.write(json.dumps(user.friends))

    def post(self, fb_id):
        user = ndb.Key(User, fb_id).get()
        if not user:
            self.error(404)
            return

        input_list = [f.strip() for f in
            json.loads(self.request.get('input_list'))]
        friend_list = []

        for friend_id in input_list:
            if friend_id == fb_id:
                continue
            friend = ndb.Key(User, friend_id).get()
            if not friend:
                continue
            friend_list.append(friend_id)

        user.friends = friend_list
        user.put()


class AllUserServicesHandler(BaseHandler):
    def get(self, fb_id):
        user = ndb.Key(User, fb_id).get()
        if not user:
            self.error(404)
            return

        self.write(user.services)


def sanitize(s):
    s = s.replace('/', '')
    s = s.replace('{', '')
    s = s.replace('}', '')
    s = s.replace('[', '')
    s = s.replace(']', '')
    s = s.replace('"', '')
    s = s.replace(',', '')
    return s


class UserServiceHandler(BaseHandler):
    def get(self, fb_id, service_id):
        user = ndb.Key(User, fb_id).get()
        if not user:
            self.error(404)
            return
        services_dict = json.loads(user.services)

        codes = services_dict.get(service_id, [])
        self.write(json.dumps(codes))

    def post(self, fb_id, service_id):
        user = ndb.Key(User, fb_id).get()
        if not user:
            self.error(404)
            return

        services_dict = json.loads(user.services)
        code = sanitize(self.request.get('code'))
        if not code:
            return
        if service_id in services_dict:
            codes = services_dict[service_id]
            codes.append(code)
            services_dict[service_id] = list(set(codes))
        else:
            services_dict[service_id] = [code]
        user.services = json.dumps(services_dict)
        user.put()

        service = ndb.Key(Service, service_id).get()
        if not service:
            service = Service(id=service_id, codes=json.dumps([code]))
        else:
            codes = json.loads(service.codes)
            codes.append(code)
            service.codes = json.dumps(list(set(codes)))
            service.put()
        service.put()


class ServiceHandler(BaseHandler):
    def get(self, service_id):
        service = ndb.Key(Service, service_id).get()
        if not service:
            self.error(404)
            return

        self.write(service.codes)


class User(ndb.Model):
    # key = fb user id
    full_name = ndb.StringProperty(default='User')
    friends = ndb.StringProperty(repeated=True)
    # serialize JSON here, format:
    # Array with Objects with service string and codes array
    services = ndb.TextProperty(default='{}')


class Service(ndb.Model):
    codes = ndb.TextProperty(default='[]')


app = webapp2.WSGIApplication([
    ('/users/([0-9]+)/?', UserHandler),
    ('/users/([0-9]+)/friends/?', FriendHandler),
    ('/users/([0-9]+)/services/?', AllUserServicesHandler),
    ('/users/([0-9]+)/services/([a-zA-Z0-9!_-]+)/?', UserServiceHandler),
    ('/services/([a-zA-Z0-9!_-]+)/?', ServiceHandler)
], debug=True)