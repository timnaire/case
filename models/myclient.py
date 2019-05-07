from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class MyClient(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    client = ndb.KeyProperty(kind=Client)
    status = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    
    @classmethod
    def save(cls,*args,**kwargs):
        myclient_id = str(kwargs.get('id'))

        if myclient_id and myclient_id.isdigit():
            myclient = cls.get_by_id(int(myclient_id))
        else:
            myclient = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            myclient.lawyer = lawyer_key
        
        client_id = str(kwargs.get('client'))
        if client_id.isdigit():
            client_key = ndb.Key('Client', int(client_id))
            myclient.client = client_key 

        if kwargs.get('status'):
            myclient.status = kwargs.get('status')
        
        return myclient.put()
        
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