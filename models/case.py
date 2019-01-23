from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class Case(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    case_name = ndb.StringProperty()
    client = ndb.KeyProperty(kind=Client)
    case_description = ndb.StringProperty()
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
        
        if kwargs.get('case_name'):
            case.case_name = kwargs.get('case_name')
        if kwargs.get('case_description'):
            case.case_description = kwargs.get('case_description')

        case.put()
        return case

    @classmethod
    def get_all_cases(cls,*args,**kwargs):
        case = None

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            if lawyer_key:
                case = cls.query(cls.lawyer == lawyer_key).order(cls.created).fetch()
        
        if not case:
            case = None

        return case
        
    def to_dict(self):
        data = {}

        data['lawyer'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer'] = lawyer.to_dict()
        
        data['case_name'] = self.case_name
        return data
