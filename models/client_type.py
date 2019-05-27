import logging
from google.appengine.ext import ndb

class ClientType(ndb.Model):
    client_type = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        ct_id = str(kwargs.get('id'))

        if ct_id and ct_id.isdigit():
            ct = cls.get_by_id(int(ct_id))
        else:
            ct = cls()

        if kwargs.get('client_type'):
            ct.client_type = kwargs.get('client_type')

        ct.put()
        return ct

    @classmethod
    def list_of_cts(cls):
        list_of_ct = {}

        cts = cls.query().fetch()

        if cts:
            for ct in cts:
                list_of_ct[""+ct.client_type+""] = ct.client_type
        
        if not list_of_ct:
            list_of_ct = None

        return list_of_ct

    @classmethod
    def list_client_type(cls):
        list_of_ct = []

        cts = cls.query().fetch()

        if cts:
            for ct in cts:
                list_of_ct.append(ct.to_dict())
        
        if not list_of_ct:
            list_of_ct = None

        return list_of_ct

    def to_dict(self):
        data = {}

        data['clien_type'] = self.client_type

        return data