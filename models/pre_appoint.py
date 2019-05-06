from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class PreAppoint(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    client = ndb.KeyProperty(kind=Client)
    status = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    
    @classmethod
    def save(cls,*args,**kwargs):
        preappoint_id = str(kwargs.get('id'))

        if preappoint_id and preappoint_id.isdigit():
            preappoint = cls.get_by_id(int(preappoint_id))
        else:
            preappoint = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            preappoint.lawyer = lawyer_key
        
        client_id = str(kwargs.get('client'))
        if client_id.isdigit():
            client_key = ndb.Key('Client', int(client_id))
            preappoint.client = client_key 

        if kwargs.get('status'):
            preappoint.status = kwargs.get('status')
        
        preappoint.put()
        return preappoint

    @classmethod
    def isAppointed(cls,*args,**kwargs):
        preappoint = None

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
        
        client_id = str(kwargs.get('client'))
        if client_id.isdigit():
            client_key = ndb.Key('Client', int(client_id))

        if client_id and lawyer_id:
            preappoint = cls.query(cls.lawyer == lawyer_key, cls.client == client_key).get()

        if not preappoint:
            preappoint = None

        return preappoint

    @classmethod
    def allPreAppointment(cls,*args,**kwargs):
        preappoint = None 

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            if lawyer_key:
                preappoint = cls.query(cls.lawyer == lawyer_key).fetch()
        
        if not preappoint:
            preappoint = None

        return preappoint

    def to_dict(self):
        data = {}
        
        data['lawyer'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer'] = lawyer.to_dict()

        data['client'] = None
        if self.client:
            client = self.client.get()            
            data['client'] = client.to_dict()
        
        data['status'] = self.status
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data