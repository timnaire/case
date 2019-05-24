import logging
from google.appengine.ext import ndb

class Court(ndb.Model):
    court = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        court_id = str(kwargs.get('id'))

        if court_id and court_id.isdigit():
            court = cls.get_by_id(int(court_id))
        else:
            court = cls()

        if kwargs.get('court'):
            court.court = kwargs.get('court')

        court.put()
        return court

    @classmethod
    def list_of_courts(cls):
        list_of_courts = {}

        courts = cls.query().fetch()

        if courts:
            for court in courts:
                list_of_courts[""+court.court+""] = court.court
        
        if not list_of_courts:
            list_of_courts = None

        return list_of_courts