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
        preappoin_id = str(kwargs.get('id'))

        if preappoin_id and preappoin_id.isdigit():
            preappoint = cls.get_by_id(int(preappoin_id))
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
        
        return preappoint.put()