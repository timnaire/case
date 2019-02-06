from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class Event(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    client = ndb.KeyProperty(kind=Client)
    event_title = ndb.StringProperty()
    event_location = ndb.StringProperty()
    event_details = ndb.StringProperty()
    event_duration = ndb.StringProperty()
    event_type = ndb.StringProperty()
    date = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls, *args, **kwargs):
        event_id = str(kwargs.get('id'))

        if event_id and event_id.isdigit():
            event = cls.get_by_id(int(event_id))
        else:
            event = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            event.lawyer = lawyer_key
        
        client_id = str(kwargs.get('client'))
        if client_id.isdigit():
            client_key = ndb.Key('Client', int(client_id))
            event.client = client_key 
        
        if kwargs.get('event_title'):
            event.event_content = kwargs.get('event_title')
        if kwargs.get('event_location'):
            event.event_content = kwargs.get('event_location')
        if kwargs.get('event_details'):
            event.event_content = kwargs.get('event_details')
        if kwargs.get('event_type'):
            event.event_type = kwargs.get('event_type')
        if kwargs.get('event_duration'):
            event.event_duration = kwargs.get('event_duration')
        if kwargs.get('date'):
            event.date = kwargs.get('date')

        event.put()
        return event
        
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
        
        data['event_duration'] = self.event_duration
        data['event_title'] = self.event_title
        data['event_details'] = self.event_details
        data['event_location'] = self.event_location
        data['date'] = self.date
        
        return data
