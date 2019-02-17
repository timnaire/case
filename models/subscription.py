from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.payment import Payment

class Subscription(ndb.Model):
    payment = ndb.KeyProperty(kind=Payment)
    status = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        subscription_id = str(kwargs.get('id'))

        if subscription_id and subscription_id.isdigit():
            subscription = cls.get_by_id(int(subscription_id))
        else:
            subscription = cls()

        payment_id = str(kwargs.get('payment'))
        if payment_id.isdigit():
            payment_key = ndb.Key('Payment',int(payment_id))
            subscription.payment = payment_key

        if kwargs.get('status'):
            payment.status = kwargs.get('status')

        subscription.put()
        return subscription

    def to_dict(self):
        data = {}

        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data