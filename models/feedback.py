from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.client import Client

class Feedback(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    client = ndb.KeyProperty(kind=Client)
    rating = ndb.StringProperty()
    feedback = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        feedback_id = str(kwargs.get('id'))

        if feedback_id and feedback_id.isdigit():
            feedback = cls.get_by_id(int(feedback_id))
        else:
            feedback = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            feedback.lawyer = lawyer_key

        client_id = str(kwargs.get('client'))
        if client_id.isdigit():
            client_key = ndb.Key('Client',int(client_id))
            feedback.client = client_key

        if kwargs.get('rating'):
            feedback.rating = kwargs.get('rating')
        if kwargs.get('feedback'):
            feedback.feedback = kwargs.get('feedback')

        feedback.put()
        return feedback

    @classmethod
    def getAllFeedbacks(cls,client_id):
        list_of_feedbacks = []

        if client_id:
            client_key = ndb.Key('Client',int(client_id))
            if client_key:
                feedbacks = cls.query(cls.client == client_key).fetch()

                for f in feedbacks:
                    list_of_feedbacks.append(f.to_dict())
        
        return list_of_feedbacks

    def solo_dict(self):
        data = {}
        data['feedback_id'] = self.key.id()
        data['rating'] = self.rating
        data['feedback'] = self.feedback
            
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'
        return data

    def to_dict(self):
        data = {}
        
        data['feedback_id'] = self.key.id()
        data['lawyer'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer'] = lawyer.to_dict()

        data['client'] = None
        if self.client:
            client = self.client.get()
            data['client'] = client.to_dict()

        data['rating'] = self.rating
        data['feedback'] = self.feedback
            
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data