from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.payment import Payment

class Subscription(ndb.Model):
    payment = ndb.KeyProperty(kind=Payment)
    date_started = ndb.DateTimeProperty()
    date_ended = ndb.DateTimeProperty()
    status = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        data = {}

        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data