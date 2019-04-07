import logging
from google.appengine.ext import ndb
from models.lawyer import Lawyer

class Subpractice(ndb.Model):
    practice = ndb.KeyProperty(kind=Practice)
    subpractice = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        subpractice_id = str(kwargs.get('id'))

        if subpractice_id and subpractice_id.isdigit():
            subpractice = cls.get_by_id(int(subpractice_id))
        else:
            subpractice = cls()

        practice_id = str(kwargs.get('practice'))
        if practice_id.isdigit():
            practice_key = ndb.Key('Practice',int(practice_id))
            subpractice.practice = practice_key
        
        if kwargs.get('subpractice'):
            subpractice.subpractice = kwargs.get('subpractice')

        subpractice.put()
        return subpractice


    def to_dict(self):
        data = {}
        data['lawyer'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            data['lawyer'] = lawyer.to_dict()
            practices = self.query().fetch()
            lawyer_pract = []
            for p in practices:
                if p.lawyer == lawyer.key:
                    lawyer_pract.append(p.law_practice)
            
            data['law_practice'] = lawyer_pract
        
        return data
