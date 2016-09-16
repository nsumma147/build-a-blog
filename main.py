#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),"templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                            autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainHandler(Handler):

    def get(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost "
                            "ORDER BY created DESC LIMIT 5 ")
        self.render("Front.html", posts = posts)

class NewPage(Handler):
    def render_new_post(self, title="", body="", error=""):

        self.render("NewPost.html", title=title,body=body,error=error)

    def get(self):
        self.render_new_post()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = BlogPost(title = title, body = body)
            b.put()

            self.redirect("/blog")
        else:
            error = "We need both a title AND art!"
            self.render_new_post(title, body, error)

class Permalink(Handler):
    def get(self, id):
        post = BlogPost.get_by_id(int(id))

        if post:
            self.render("Permalink.html", post = post)
        else:
            error = "Blog post does not exist."
            self.render("Permalink.html", error = error, post = post)

app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/blog/newpost', NewPage),
    webapp2.Route('/blog/<id:\d+>', Permalink)
], debug=True)
