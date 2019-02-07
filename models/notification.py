from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.clients import Client

class Notification(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    client = ndb.KeyProperty(kind=Client)
    notif_from = ndb.StringProperty()
    notif_to = ndb.StringProperty()
    received = ndb.StringProperty()
    sent = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        data = {}
        data['notif_from'] = self.notif_from
        data['notif_to'] = self.notif_to
        data['received'] = self.received
        data['sent'] = self.sent
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data