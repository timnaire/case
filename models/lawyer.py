from google.appengine.ext import ndb
from passlib.hash import pbkdf2_sha256
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import SECRET_KEY
# from models.client import Client

class Lawyer(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()    
    cityOrMunicipality = ndb.StringProperty()
    office = ndb.StringProperty()
    aboutme = ndb.StringProperty()
    profile_pic = ndb.StringProperty()
    password = ndb.StringProperty()
    rollno = ndb.StringProperty()
    status = ndb.StringProperty()
    firm = ndb.StringProperty()
    fcm_token = ndb.StringProperty()
    sex = ndb.StringProperty()
    limit_case = ndb.StringProperty()
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
        if kwargs.get('cityOrMunicipality'):
            lawyer.cityOrMunicipality = kwargs.get('cityOrMunicipality')
        if kwargs.get('office'):
            lawyer.office = kwargs.get('office')
        if kwargs.get('aboutme'):
            lawyer.aboutme = kwargs.get('aboutme')
        if kwargs.get('profile_pic'):
            lawyer.profile_pic = kwargs.get('profile_pic')
        if kwargs.get('password'):
            lawyer.password = pbkdf2_sha256.hash(kwargs.get('password'))
        if kwargs.get('rollno'):
            lawyer.rollno = kwargs.get('rollno')
        if kwargs.get('status'):
            lawyer.status = kwargs.get('status')
        if kwargs.get('firm'):
            lawyer.firm = kwargs.get('firm')
        if kwargs.get('fcm_token'):
            lawyer.fcm_token = kwargs.get('fcm_token')
        if kwargs.get('sex'):
            lawyer.sex = kwargs.get('sex')
        if kwargs.get('limit_case'):
            lawyer.limit_case = kwargs.get('limit_case')

        lawyer.put()
        return lawyer
    
    @classmethod
    def find_city(cls, cityOrMunicipality):
        lawyers = None
        if cityOrMunicipality:
            lawyers = cls.query(cls.cityOrMunicipality == cityOrMunicipality, cls.password != None, cls.status == "activated").fetch()
        
        if not lawyers:
            lawyers = None
        return lawyers
    
    # @classmethod
    # def deactivate(cls, lawyer):
    #     lawyers = None
    #     if lawyer_id:
    #         Lawyer.save()
    #     if not lawyers:
    #         lawyers = None
    #     return lawyers
    
    @classmethod
    def sign_in(cls, email, password):
        lawyer = None
        if email and password:
            lawyer = cls.query(cls.email == email, cls.password != None, cls.status == "activated").get()

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
    def rollno_exist(cls,rollno):
        lawyer = None
        if rollno:
            lawyer = cls.query(cls.rollno == rollno).get()
        
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
    def add_password(cls,email,password):
        lawyer = None
        if email and password:
            lawyer = cls.query(cls.email == email, cls.password == None).get()
            lawyer.password = pbkdf2_sha256.hash(password)
            lawyer.put()
        
        return lawyer
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(SECRET_KEY)
        return s.dumps({'lawyer_id': self.key.id()})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(SECRET_KEY)
        try:
            lawyer_id = s.loads(token)['lawyer_id']
        except:
            return None
        return Lawyer.get_by_id(int(lawyer_id))

    def dict_nodate(self):
        data = {}

        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['email'] = self.email
        data['phone'] = self.phone
        data['office'] = self.office
        data['profile_pic'] = self.profile_pic
        return data
    
    def event_dict(self):
        data = {}

        data['profile_pic'] = self.profile_pic
        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['manager'] = 'lawyer'
        return data

    def to_dict(self):
        data = {}
        data['lawyer_id'] = self.key.id()
        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['email'] = self.email
        data['phone'] = self.phone
        data['cityOrMunicipality'] = self.cityOrMunicipality
        data['office'] = self.office
        data['aboutme'] = self.aboutme
        data['profile_pic'] = self.profile_pic
        data['rollno'] = self.rollno
        data['sex'] = self.sex
        data['status'] = self.status
        data['firm'] = self.firm
        data['limit_case'] = self.limit_case
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data