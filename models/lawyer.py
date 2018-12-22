from google.appengine.ext import ndb
from passlib.hash import pbkdf2_sha256

class Lawyer(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.TextProperty()
    phone = ndb.StringProperty()
    specialize = ndb.StringProperty()
    bar_number = ndb.StringProperty()
    password = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls, *args, **kwargs):
        uid = kwargs.get('id')
        lawyer = cls.get_by_id(int(uid)) if uid else cls()

        if kwargs.get('first_name'):
            lawyer.first_name = kwargs.get('first_name')
        if kwargs.get('last_name'):
            lawyer.last_name = kwargs.get('last_name')
        if kwargs.get('email'):
            lawyer.email = kwargs.get('email')
        if kwargs.get('phone'):
            lawyer.phone = kwargs.get('phone')
        if kwargs.get('specialize'):
            lawyer.specialize = kwargs.get('specialize')
        if kwargs.get('bar_number'):
            lawyer.bar_number = kwargs.get('bar_number')
        if kwargs.get('password'):
            lawyer.password = pbkdf2_sha256.hash(kwargs.get('password'))

        lawyer.put()
        return lawyer