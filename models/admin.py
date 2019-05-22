from google.appengine.ext import ndb
from passlib.hash import pbkdf2_sha256

class Admin(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        admin_id = str(kwargs.get('id'))

        if admin_id and admin_id.isdigit():
            admin = cls.get_by_id(int(admin_id))
        else:
            admin = cls()
        
        if kwargs.get('username'):
            admin.username = kwargs.get('username')
        if kwargs.get('password'):
            admin.password = pbkdf2_sha256.hash(kwargs.get('password'))

        admin.put()
        return admin
    
    @classmethod
    def sign_in(cls, username, password):
        admin = None
        if username and password:
            admin = cls.query(cls.username == username, cls.password != None).get()

        if admin and not pbkdf2_sha256.verify(password, admin.password):
            admin = None

        return admin

