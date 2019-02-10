from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class Notification(ndb.Model):
    notif_from = ndb.KeyProperty()
    notif_to = ndb.KeyProperty()
    msg = ndb.StringProperty()
    received = ndb.StringProperty()
    sent = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    
    @classmethod
    def save(cls,*args,**kwargs):
        notify_id = str(kwargs.get('id'))

        if notify_id and notify_id.isdigit():
            notify = cls.get_by_id(int(notify_id))
        else:
            notify = cls()

        # notif_from = str(kwargs.get('notif_from'))
        # if notif_from.isdigit():
        #     notif_from_key = ndb.Key('Client',int(notif_from))
        #     notify.notif_from = notif_from_key
        
        # notif_to = str(kwargs.get('notif_to'))
        # if notif_to.isdigit():
        #     notif_to_key = ndb.Key('Lawyer', int(notif_to))
        #     notify.notif_to = notif_to_key 

        if kwargs.get('notif_from'):
            notify.notif_from = kwargs.get('notif_from')
        if kwargs.get('notif_to'):
            notify.notif_to = kwargs.get('notif_to')
        if kwargs.get('msg'):
            notify.msg = kwargs.get('msg')
        if kwargs.get('received'):
            notify.received = kwargs.get('received')
        if kwargs.get('sent'):
            notify.sent = kwargs.get('sent')

        notify.put()
        return notify

    def to_dict(self):
        data = {}
        data['received'] = self.received
        data['sent'] = self.sent
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data