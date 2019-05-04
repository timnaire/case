import logging
from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.subcategory import Subcategory

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

    @classmethod
    def find_practice(cls, law_practice,cityOrMunicipality):
        found_lawyers = []
        lawyers = Lawyer.find_city(cityOrMunicipality=cityOrMunicipality)
        if law_practice and cityOrMunicipality:
            if lawyers:
                for lawyer in lawyers:
                    practice = cls.query(cls.law_practice == law_practice, cls.lawyer == lawyer.key).get()
                    if practice:
                        found_lawyers.append(practice.to_dict())

        if not found_lawyers:
            found_lawyers = None

        return found_lawyers

    @classmethod
    def all_lawyers(cls,lawyers):
        found_lawyers = []

        lawyers = lawyers
        if lawyers:
            for lawyer in lawyers:
                practice = cls.query(cls.lawyer == lawyer.key).get()
                if practice:
                    found_lawyers.append(practice.to_dict())

        if not found_lawyers:
            found_lawyers = None
        
        return found_lawyers


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

        data['subcategory'] = None
        if self.lawyer:
            lawyer = self.lawyer.get()
            subcategory = Subcategory.query().fetch()
            lawyer_sub = []
            for s in subcategory:
                if s.lawyer == lawyer.key:
                    lawyer_sub.append(s.subcategory)
            
            data['subcategory'] = lawyer_sub
        
        return data

    def practice(self):
        data = {}
        data['law_practice'] = self.law_practice
        return data