from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class Relationship(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    client = ndb.KeyProperty(kind=Client)
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
    
    @classmethod
    def client_exist(cls,client_id):
        relation = None

        if client_id:
            client_key = ndb.Key('Client',int(client_id))
            relation = cls.query(cls.client == client_key).get()
        
        if not relation:
            relation = None

        return relation
    
    @classmethod
    def undecided(cls, lawyer_id):
        list_undecided = []
        
        if lawyer_id:
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            relations = cls.query(cls.lawyer == lawyer_key , cls.status == None).fetch()
            if relations:
                for relation in relations:
                    list_undecided.append(relation.notify)
        
        if not list_undecided:
            list_undecided = None
        
        return list_undecided

    @classmethod
    def my_clients(cls, lawyer_id):
        list_of_clients = []
        
        if lawyer_id:
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            # and status="accepted"
            clients = cls.query(cls.lawyer == lawyer_key , cls.status == "accepted").fetch()
            if clients:
                for client in clients:
                    list_of_clients.append(client.dict_client())
        
        if not list_of_clients:
            list_of_clients = None
        
        return list_of_clients
    @classmethod
    def pa_unaccepted_request(cls, lawyer_id):
        list_of_requests = []

        if lawyer_id:
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            requests = cls.query(cls.lawyer == lawyer_key, cls.status == None).fetch()
            if requests:
                for req in requests:
                    if req.status == None:
                        list_of_requests.append(req.dict_client())
        if not list_of_requests:
            list_of_requests = None
        
        return list_of_requests
            

    @classmethod
    def my_lawyers(cls, client_id):
        list_of_lawyers = []
        
        if client_id:
            client_key = ndb.Key('Client',int(client_id))
            lawyers = cls.query(cls.client == client_key , cls.status == "Accepted").fetch()
            if lawyers:
                for lawyer in lawyers:
                    list_of_lawyers.append(lawyer.dict_lawyer())
        
        if not list_of_lawyers:
            list_of_lawyers = None
        
        return list_of_lawyers

    def dict_lawyer(self):
        data = {}
        data['case_id'] = self.key.id()
        data['lawyer'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer_id'] = lawyer.key.id()
            data['lawyer'] = lawyer.dict_nodate()
        return data

    def dict_client(self):
        data = {}
        data['relation_id'] = self.key.id()
        data['case_id'] = self.key.id()
        data['client'] = None
        if self.client:
            client = self.client.get()
            data['client_id'] = client.key.id()
            data['client'] = client.dict_nodate()
        return data

    def notify(self):
        data = {}
        data['client_id'] = None
        if self.client:
            client = self.client.get()
            data['client_id'] = client.key.id()

        data['lawyer_id'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer_id'] = lawyer.key.id()
        
        data['relation_id'] = self.key.id()

        return data

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