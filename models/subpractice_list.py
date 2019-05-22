import logging
from google.appengine.ext import ndb

class SubPracticeList(ndb.Model):
    law_practice = ndb.KindProperty(kind=SubPracticeList)
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
            practice_key = ndb.Key('PracticeList',int(practice_id))
            subpractice.law_practice = practice_key
        

        if kwargs.get('subpractice'):
            subpractice.law_practice = kwargs.get('subpractice')

        subpractice.put()
        return subpractice

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