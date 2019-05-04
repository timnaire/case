import logging
from google.appengine.ext import ndb
from models.lawyer import Lawyer

class Subcategory(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    subcategory = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        subcategory_id = str(kwargs.get('id'))

        if subcategory_id and subcategory_id.isdigit():
            subcategory = cls.get_by_id(int(subcategory_id))
        else:
            subcategory = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            subcategory.lawyer = lawyer_key
        
        if kwargs.get('subcategory'):
            subcategory.subcategory = kwargs.get('subcategory')

        subcategory.put()
        return subcategory

    def subpract(self):
        data = {}
        data['subcategory'] = self.subcategory
        return data
