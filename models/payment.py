from google.appengine.ext import ndb
from models.lawyer import Lawyer

class Payment(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    payment_method = ndb.StringProperty()
    payment_date = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        data = {}

        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data