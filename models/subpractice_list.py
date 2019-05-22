import logging
from google.appengine.ext import ndb
from models.practice_list import PracticeList

class SubPracticeList(ndb.Model):
    law_practice = ndb.KeyProperty(kind=PracticeList)
    subpractice = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        subpractice_id = str(kwargs.get('id'))

        if subpractice_id and subpractice_id.isdigit():
            s = cls.get_by_id(int(subpractice_id))
        else:
            s = cls()

        practice_id = str(kwargs.get('practice'))
        if practice_id.isdigit():
            practice_key = ndb.Key('PracticeList',int(practice_id))
            s.law_practice = practice_key

        if kwargs.get('spractice'):
            s.subpractice = kwargs.get('spractice')
            
        s.put()
        return s

    @classmethod
    def list_of_subpractices(cls):
        list_of_all = {}
        practices = PracticeList.query().fetch()

        if practices:
            for practice in practices:
                list_subpractices = set()
                practice_key = ndb.Key('PracticeList',int(practice.key.id()))
                subpractices = cls.query(cls.law_practice == practice_key).fetch()
                if subpractices:
                    for s in subpractices:
                        list_subpractices.add(""+str(s.subpractice)+"")

                    list_of_all[""+practice.law_practice+""] = list_subpractices

        # logging.info(list_of_all)
        if not list_of_all:
            list_of_all = None

        return list_of_all