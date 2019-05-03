import logging
from google.appengine.ext import ndb
from models.practice import Practice

class Subcategory(ndb.Model):
    practice = ndb.KeyProperty(kind=Practice)
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

        practice_id = str(kwargs.get('practice'))
        if practice_id.isdigit():
            practice_key = ndb.Key('Practice',int(practice_id))
            subcategory.practice = practice_key
        
        if kwargs.get('subcategory'):
            subcategory.subcategory = kwargs.get('subcategory')

        subcategory.put()
        return subcategory

