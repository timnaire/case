from google.appengine.ext import ndb
from models.case import Case

class Feature(ndb.Model):
    case = ndb.KeyProperty(kind=Case)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        feature_id = str(kwargs.get('id'))

        if feature_id and feature_id.isdigit():
            feature = cls.get_by_id(int(feature_id))
        else:
            feature = cls()

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Lawyer',int(case_id))
            feature.case = case_key

        feature.put()
        return feature

    def to_dict(self):
        data = {}
        data['case'] = None
        if self.case:
            case = self.case.get()
            data['case'] = case.to_dict()
    
        return data

