from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client
from models.pre_appoint import PreAppoint

class IncomingClient(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    client = ndb.KeyProperty(kind=Client)
    pre_appoint = ndb.KeyProperty(kind=PreAppoint)
    status = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    
    @classmethod
    def save(cls,*args,**kwargs):
        relationship_id = str(kwargs.get('id'))

        if relationship_id and relationship_id.isdigit():
            relationship = cls.get_by_id(int(relationship_id))
        else:
            relationship = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            relationship.lawyer = lawyer_key
        
        client_id = str(kwargs.get('client'))
        if client_id.isdigit():
            client_key = ndb.Key('Client', int(client_id))
            relationship.client = client_key 

        if kwargs.get('status'):
            relationship.status = kwargs.get('status')
        
        return relationship.put()