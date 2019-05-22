import logging
from google.appengine.ext import ndb

class PracticeList(ndb.Model):
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

        if kwargs.get('practice'):
            practice.law_practice = kwargs.get('practice')

        practice.put()
        return practice

    @classmethod
    def list_of_practices(cls):
        list_practices = {}

        practices = cls.query().fetch()

        if practices:
            for practice in practices:
                list_practices[""+practice.law_practice+""] = practice.law_practice
        
        if not list_practices:
            list_practices = None

        return list_practices

    def practice(self):
        data = {}
        data['law_practice'] = self.law_practice
        return data