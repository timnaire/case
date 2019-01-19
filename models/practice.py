from google.appengine.ext import ndb
from models.lawyer import Lawyer

class Practice(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    law_practice = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        practice_id = str(kwargs.get('id'))

        if practice_id and practice_id.isdigit():
            practice = cls.get_by_id(int(practice_id))
        else:
            practice = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            practice.lawyer = lawyer_key
        
        if kwargs.get('pract'):
            practice.law_practice = kwargs.get('pract')

        practice.put()
        return practice

    def to_dict(self):
        data = {}
        
        data['lawyer'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer'] = lawyer.to_dict()
        
        data['law_practice'] = self.law_practice
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'
        return data