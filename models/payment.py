from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class Payment(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    client = ndb.KeyProperty(kind=Client)
    payment_method = ndb.StringProperty()
    payment_date = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        payment_id = str(kwargs.get('id'))

        if payment_id and payment_id.isdigit():
            payment = cls.get_by_id(int(payment_id))
        else:
            payment = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            payment.lawyer = lawyer_key
        
        client_id = str(kwargs.get('client_id'))
        if client_id.isdigit():
            client_key = ndb.Key('Client', int(client_id))
            payment.client = client_key 
        
        if kwargs.get('payment_method'):
            payment.payment_method = kwargs.get('payment_method')
        if kwargs.get('payment_date'):
            payment.payment_date = kwargs.get('payment_date')

        payment.put()
        return payment

    @classmethod
    def lawyer_subscribed(cls,lawyer_id):
        lawyer = None
        if lawyer_id:
            lawyer_key = Lawyer.get_by_id(int(lawyer_id))
            lawyer = cls.query(cls.lawyer == lawyer_key).get()
        
        if not lawyer:
            lawyer = None
        
        return lawyer

    def to_dict(self):
        data = {}
        data['payment_method'] = self.payment_method
        data['payment_date'] = self.payment_date
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data