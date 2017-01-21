import os
import re

import webapp2

# template jinja2
import jinja2

# google app engine datastore
from google.appengine.ext import db

#initializes jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
#basic handler
class Handler(webapp2.RequestHandler):
    def write(self,*a, **kw):
        self.response.out.write(*a,**kw)

    def render_str(self,template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))
#Main Handler
class MainPage(Handler):
    def get(self):
        self.write("Hello, My Blog!")
        #google procedual language for writing a query
        #look up all the posts
        posts=Post.all().order('-created')
        #posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render('front.html', posts = posts)


#blog stuff
#store things in google app engine datastore
#def blog_key(name = 'default'):
#    return db.Key.from_path('blogs', name)

#define post class
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        #replace new line with a break line in html
        self._render_text = self.content.replace('\n', '<br>')

        return render_str("post.html", p = self)
# main blog URL
#class BlogFront(Handler):

# a particular post page.
class PostPage(Handler):
    def get(self, post_id):
        #find the post with post_id, which get passed from the URL
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(subject = subject, content = content)
            p.put()
            self.redirect('/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/([0-9]+)', PostPage),
                               ('/newpost', NewPost),
                               ],
                              debug=True)
