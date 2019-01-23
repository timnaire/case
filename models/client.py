from google.appengine.ext import ndb

class Client(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    address = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        case_id = str(kwargs.get('id'))

        if case_id and case_id.isdigit():
            case = cls.get_by_id(int(case_id))
        else:
            case = cls()
        
        if kwargs.get('first_name'):
            case.first_name = kwargs.get('first_name')
        if kwargs.get('last_name'):
            case.last_name = kwargs.get('last_name')
        if kwargs.get('email'):
            case.email = kwargs.get('email')
        if kwargs.get('phone'):
            case.phone = kwargs.get('phone')
        if kwargs.get('address'):
            case.address = kwargs.get('address')

        case.put()
        return case

    def to_dict():
        data = {}

        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['email'] = self.email
        data['phone'] = self.phone
        data['address'] = self.address
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'
