from google.appengine.ext import ndb
from passlib.hash import pbkdf2_sha256

class Client(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    address = ndb.StringProperty()
    password = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        client_id = str(kwargs.get('id'))

        if client_id and client_id.isdigit():
            client = cls.get_by_id(int(client_id))
        else:
            client = cls()
        
        if kwargs.get('first_name'):
            client.first_name = kwargs.get('first_name')
        if kwargs.get('last_name'):
            client.last_name = kwargs.get('last_name')
        if kwargs.get('email'):
            client.email = kwargs.get('email')
        if kwargs.get('phone'):
            client.phone = kwargs.get('phone')
        if kwargs.get('address'):
            client.address = kwargs.get('address')
        if kwargs.get('password'):
            client.password = pbkdf2_sha256.hash(kwargs.get('password'))

        client.put()
        return client
    
    @classmethod
    def check_email(cls,email):
        client = None

        if email:
            client = cls.query(cls.email == email).get()
        
        if not client:
            client = None

        return client
    
    @classmethod
    def sign_in(cls, email, password):
        client = None
        if email and password:
            client = cls.query(cls.email == email, cls.password != None).get()

        if client and not pbkdf2_sha256.verify(password, client.password):
            client = None

        return client

    def to_dict():
        data = {}

        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['email'] = self.email
        data['phone'] = self.phone
        data['address'] = self.address
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'
