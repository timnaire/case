from google.appengine.ext import ndb
from passlib.hash import pbkdf2_sha256

class Lawyer(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    phone = ndb.StringProperty()
    email = ndb.StringProperty()
    specialized = ndb.StringProperty()
    password = ndb.StringProperty()
    bar_number = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)