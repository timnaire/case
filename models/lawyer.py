from google.appengine.ext import ndb
from passlib.hash import pbkdf2_sha256

class Lawyer(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()    
    city = ndb.StringProperty()
    office = ndb.StringProperty()
    law_practice = ndb.StringProperty()
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
        if kwargs.get('province'):
            lawyer.province = kwargs.get('province')
        if kwargs.get('office'):
            lawyer.office = kwargs.get('office')
        if kwargs.get('law_practice'):
            lawyer.law_practice = kwargs.get('law_practice')
        if kwargs.get('bar_number'):
            lawyer.bar_number = kwargs.get('bar_number')
        if kwargs.get('password'):
            lawyer.password = pbkdf2_sha256.hash(kwargs.get('password'))

        lawyer.put()
        return lawyer
    
    @classmethod
    def login(cls, email, password):
        lawyer = None
        if email and password:
            lawyer = cls.query(cls.email == email).get()

        if lawyer and not pbkdf2_sha256.verify(password, lawyer.password):
            lawyer = None

        return lawyer
    
    @classmethod
    def check_email(cls,email):
        lawyer = None
        if email:
            lawyer = cls.query(cls.email == email).get()
        
        if not lawyer:
            lawyer = None
        
        return lawyer

    @classmethod
    def f_reset_password(cls,email,password):
        lawyer = None
        if email and password:
            lawyer = cls.query(cls.email == email, cls.password == None).get()
            lawyer.password = pbkdf2_sha256.hash(password)
            lawyer.put()
        
        return lawyer

    # def to_dict(self):
    #     data = {}

    #     data['first_name'] = self.first_name
    #     data['last_name'] = self.last_name
    #     data['email'] = self.email
    #     data['phone'] = self.phone
    #     data['office'] = self.office
    #     data['law_practice'] = self.law_practice
    #     data['bar_number'] = self.bar_number
    #     data['created'] = self.created.isoformat() + 'Z'
    #     data['updated'] = self.updated.isoformat() + 'Z'

    #     return data