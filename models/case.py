from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class Case(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    case_title = ndb.StringProperty()
    client = ndb.KeyProperty(kind=Client)
    case_description = ndb.StringProperty()
    case_status = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        case_id = str(kwargs.get('id'))

        if case_id and case_id.isdigit():
            case = cls.get_by_id(int(case_id))
        else:
            case = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            case.lawyer = lawyer_key
        
        client_id = str(kwargs.get('client_id'))
        if client_id.isdigit():
            client_key = ndb.Key('Client', int(client_id))
            case.client = client_key 
        
        if kwargs.get('case_title'):
            case.case_title = kwargs.get('case_title')
        if kwargs.get('case_description'):
            case.case_description = kwargs.get('case_description')
        if kwargs.get('case_status'):
            case.case_status = kwargs.get('case_status')

        case.put()
        return case

    @classmethod
    def my_case(cls,lawyer_id):
        number_of_case = 0
        if lawyer_id:
            lawyer = Lawyer.get_by_id(int(lawyer_id))
            cases = cls.query(cls.lawyer == lawyer.key).fetch()
            for case in cases:
                number_of_case = number_of_case + 1
        
        if not number_of_case:
            number_of_case = None

        return number_of_case

    @classmethod
    def get_all_cases(cls,*args,**kwargs):
        case = None

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            if lawyer_key:
                case = cls.query(cls.lawyer == lawyer_key).order(cls.created).fetch()
        
        client_id = str(kwargs.get('client'))
        if client_id.isdigit():
            client_key = ndb.Key('Client',int(client_id))
            if client_key:
                case = cls.query(cls.client == client_key).order(cls.created).fetch()
        
        if not case:
            case = None

        return case

    
    @classmethod
    def lawyers_client(cls, *args, **kwargs):
        list_clients = []
        case = None

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            if lawyer_key:
                case = cls.query(cls.lawyer == lawyer_key).order(cls.created).fetch()
                if case:
                    for c in case:
                        list_clients.append(c.get_clients())
        
        if not list_clients:
            list_clients = None
        
        return list_clients
    
    @classmethod
    def clients_lawyer(cls, *args, **kwargs):
        list_lawyer = []
        case = None

        client_id = str(kwargs.get('client'))
        if client_id.isdigit():
            client_key = ndb.Key('Client',int(client_id))
            if client_key:
                case = cls.query(cls.client == client_key).order(cls.created).fetch()
                if case:
                    for c in case:
                        list_lawyer.append(c.get_lawyers())
        
        if not list_lawyer:
            list_lawyer = None
        
        return list_lawyer

    def delete(self,case_id):
        deleted = None

        if case_id:
            deleted = ndb.Key("Case", int(case_id)).delete()
            
        if not deleted:
            deleted = None
            
        return True

    def get_clients(self):
        data = {}
        data['client'] = None
        if self.client:
            client = self.client.get()
            data['client'] = client.dict_nodate()
        return data

    def get_lawyers(self):
        data = {}
        data['lawyer'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer'] = lawyer.dict_nodate()
        return data

    def to_dict(self):
        data = {}
        data['client_id'] = self.key.id()
        data['lawyer'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer'] = lawyer.to_dict()

        data['client'] = None
        if self.client:
            client = self.client.get()
            data['client'] = client.to_dict()
        
        data['case_title'] = self.case_title
        data['case_description'] = self.case_title
        data['case_status'] = self.case_status
        data['created'] = self.created.isoformat()
        data['updated'] = self.updated.isoformat()
        return data
