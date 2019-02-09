from google.appengine.ext import ndb
from passlib.hash import pbkdf2_sha256
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import SECRET_KEY

class Client(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    address = ndb.StringProperty()
    password = ndb.StringProperty()
    profile_pic = ndb.StringProperty()
    fcm_token = ndb.StringProperty()
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
        if kwargs.get('profile_pic'):
            client.profile_pic = kwargs.get('profile_pic')
        if kwargs.get('password'):
            client.password = pbkdf2_sha256.hash(kwargs.get('password'))
        if kwargs.get('fcm_token'):
            client.fcm_token = kwargs.get('fcm_token')

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
    def change_email(cls, *args, **kwargs):
        client_id = str(kwargs.get('id'))

        if client_id and client_id.isdigit():
            client = cls.get_by_id(int(client_id))
            if client and pbkdf2_sha256.verify(kwargs.get('password'), client.password):
                client.email = kwargs.get('newemail')
                client.put()
        else:
            client = None
            
        return client

    @classmethod
    def change_pass(cls, *args, **kwargs):
        client_id = str(kwargs.get('id'))

        if client_id and client_id.isdigit():
            client = cls.get_by_id(int(client_id))
            if client and pbkdf2_sha256.verify(kwargs.get('password'), client.password):
                client.password = pbkdf2_sha256.hash(kwargs.get('newpass'))
                client.put()
                return client
            else:
                return None

        return client

    @classmethod
    def check_pass(cls, *args, **kwargs):
        client_id = str(kwargs.get('id'))

        if client_id and client_id.isdigit():
            client = cls.get_by_id(int(client_id))
            if client and pbkdf2_sha256.verify(kwargs.get('password'), client.password):
                return client
            else:
                return None

        return client
    
    @classmethod
    def get_client(cls, client_id):
        client = None

        if client_id:
            client = cls.get_by_id(int(client_id))
        
        if not client:
            client = None

        return client

    @classmethod
    def email_exist(cls,newemail):
        client = None

        if newemail:
            client = cls.query(cls.email == newemail).get()
        
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
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(SECRET_KEY)
        return s.dumps({'client_id': self.key.id()})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(SECRET_KEY)
        try:
            client_id = s.loads(token)['client_id']
        except:
            return None
        return Client.get_by_id(int(client_id))

    def dict_nodate(self):
        data = {}

        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['email'] = self.email
        data['phone'] = self.phone
        data['address'] = self.address
        data['profile_pic'] = self.profile_pic

        return data

    def to_dict(self):
        data = {}

        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['email'] = self.email
        data['phone'] = self.phone
        data['address'] = self.address
        data['profile_pic'] = self.profile_pic
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data
