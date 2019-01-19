from google.appengine.ext import ndb
from passlib.hash import pbkdf2_sha256

class Lawyer(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()    
    province = ndb.StringProperty()
    office = ndb.StringProperty()
    # law_practice = ndb.StringProperty()
    profile_pic = ndb.StringProperty()
    password = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls, *args, **kwargs):
        lawyer_id = str(kwargs.get('id'))

        if lawyer_id and lawyer_id.isdigit():
            lawyer = cls.get_by_id(int(lawyer_id))
        else:
            lawyer = cls()
        
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
        # if kwargs.get('law_practice'):
        #     lawyer.law_practice = kwargs.get('law_practice')
        if kwargs.get('profile_pic'):
            lawyer.profile_pic = kwargs.get('profile_pic')
        if kwargs.get('password'):
            lawyer.password = pbkdf2_sha256.hash(kwargs.get('password'))

        lawyer.put()
        return lawyer
    
    @classmethod
    def login(cls, email, password):
        lawyer = None
        if email and password:
            lawyer = cls.query(cls.email == email, cls.password != None).get()

        if lawyer and not pbkdf2_sha256.verify(password, lawyer.password):
            lawyer = None

        return lawyer
    
    @classmethod
    def check_email(cls,email):
        lawyer = None
        if email:
            lawyer = cls.query(cls.email == email, cls.password==None).get()
        
        if not lawyer:
            lawyer = None
        
        return lawyer
    
    @classmethod
    def change_email(cls, *args, **kwargs):
        lawyer_id = str(kwargs.get('id'))

        if lawyer_id and lawyer_id.isdigit():
            lawyer = cls.get_by_id(int(lawyer_id))
            if lawyer and pbkdf2_sha256.verify(kwargs.get('password'), lawyer.password):
                lawyer.email = kwargs.get('newemail')
                lawyer.put()
        else:
            lawyer = None
            
        return lawyer

    @classmethod
    def email_exist(cls,newemail):
        lawyer = None
        if newemail:
            lawyer = cls.query(cls.email == newemail).get()
        
        if not lawyer:
            lawyer = None

        return lawyer
    
    @classmethod
    def change_pass(cls, *args, **kwargs):
        lawyer_id = str(kwargs.get('id'))

        if lawyer_id and lawyer_id.isdigit():
            lawyer = cls.get_by_id(int(lawyer_id))
            if lawyer and pbkdf2_sha256.verify(kwargs.get('password'), lawyer.password):
                lawyer.password = pbkdf2_sha256.hash(kwargs.get('newpass'))
                lawyer.put()
                return lawyer
            else:
                return None

        return lawyer

    @classmethod
    def check_pass(cls, *args, **kwargs):
        lawyer_id = str(kwargs.get('id'))

        if lawyer_id and lawyer_id.isdigit():
            lawyer = cls.get_by_id(int(lawyer_id))
            if lawyer and pbkdf2_sha256.verify(kwargs.get('password'), lawyer.password):
                return lawyer
            else:
                return None

        return lawyer

    @classmethod
    def f_reset_password(cls,email,password):
        lawyer = None
        if email and password:
            lawyer = cls.query(cls.email == email, cls.password == None).get()
            lawyer.password = pbkdf2_sha256.hash(password)
            lawyer.put()
        
        return lawyer

    def to_dict(self):
        data = {}

        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['email'] = self.email
        data['phone'] = self.phone
        data['province'] = self.province
        data['office'] = self.office
        # data['law_practice'] = self.law_practice
        data['profile_pic'] = self.profile_pic
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data