from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class Notification(ndb.Model):
    notif_from = ndb.KeyProperty()
    notif_to = ndb.KeyProperty()
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

        if kwargs.get('notif_from'):
            notify.notif_from = kwargs.get('notif_from')
        if kwargs.get('notif_to'):
            notify.notif_to = kwargs.get('notif_to')
        if kwargs.get('received'):
            notify.received = kwargs.get('received')
        if kwargs.get('sent'):
            notify.sent = kwargs.get('sent')

        case.put()
        return case

    def to_dict(self):
        data = {}
        data['notif_from'] = self.notif_from
        data['notif_to'] = self.notif_to
        data['received'] = self.received
        data['sent'] = self.sent
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data