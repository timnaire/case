from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client
from models.feedback import Feedback

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

    # for mobile
    @classmethod
    def allPreAppointmentApi(cls,*args,**kwargs):
        preappoint = None 

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            if lawyer_key:
                preappoint = cls.query(cls.lawyer == lawyer_key, cls.status == None).fetch()
        
        if not preappoint:
            preappoint = None

        return preappoint
    
    @classmethod
    def allPendingClientApi(cls,*args,**kwargs):
        preappoint = None 

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            if lawyer_key:
                preappoint = cls.query(cls.lawyer == lawyer_key, cls.status == "accept").fetch()
        
        if not preappoint:
            preappoint = None

        return preappoint

    @classmethod
    def my_clients(cls,lawyer_id):
        list_of_clients = []
        
        if lawyer_id:
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            # and status="accepted"
            clients = cls.query(cls.lawyer == lawyer_key , cls.status == "client").fetch()
            if clients:
                for client in clients:
                    list_of_clients.append(client.dict_client())
        
        if not list_of_clients:
            list_of_clients = None
        
        return list_of_clients
    
    @classmethod
    def my_lawyers(cls,client_id):
        list_of_lawyers = []
        
        if client_id:
            client_key = ndb.Key('Client',int(client_id))
            # and status="accepted"
            lawyers = cls.query(cls.client == client_key , cls.status == "client").fetch()
            if lawyers:
                for lawyer in lawyers:
                    list_of_lawyers.append(lawyer.dict_lawyer())
        
        if not list_of_lawyers:
            list_of_lawyers = None
        
        return list_of_lawyers

    @classmethod
    def accept_client(cls,lawyer_id):
        list_of_clients = []
        
        if lawyer_id:
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            # and status="accepted"
            clients = cls.query(cls.lawyer == lawyer_key , cls.status == "accept").fetch()
            if clients:
                for client in clients:
                    list_of_clients.append(client.dict_client())
        
        if not list_of_clients:
            list_of_clients = None
        
        return list_of_clients

    def to_dict(self):
        data = {}
        data['id'] = self.key.id() 
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

    def dict_client(self):
        data = {}
        data['id'] = self.key.id()
        data['case_id'] = self.key.id()
        data['client'] = None
        if self.client:
            client = self.client.get()
            data['client_id'] = client.key.id()
            data['client'] = client.dict_nodate()
            
        data['feedback'] = None
        feedback = Feedback.query(Feedback.client == self.client).get()
        if feedback:
            data['feedback'] = feedback.solo_dict()
        return data
    
    def dict_lawyer(self):
        data = {}
        data['id'] = self.key.id()
        data['case_id'] = self.key.id()
        data['lawyer'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer_id'] = lawyer.key.id()
            data['lawyer'] = lawyer.dict_nodate()

        data['feedback'] = None
        feedback = Feedback.query(Feedback.lawyer == self.lawyer).get()
        if feedback:
            data['feedback'] = feedback.solo_dict()
        return data