from google.appengine.ext import ndb
from models.lawyer import Lawyer
from models.case import Case

class Feature(ndb.Model):
    lawyer = ndb.KeyProperty(kind=Lawyer)
    case = ndb.KeyProperty(kind=Case)
    info = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        feature_id = str(kwargs.get('id'))

        if feature_id and feature_id.isdigit():
            feature = cls.get_by_id(int(feature_id))
        else:
            feature = cls()

        lawyer_id = str(kwargs.get('lawyer'))
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            feature.lawyer = lawyer_key

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Case',int(case_id))
            feature.case = case_key

        if kwargs.get('info'):
            feature.info = kwargs.get('info')

        feature.put()
        return feature
        lawyer/find/lawyer-details

    @classmethod
    def allFeatureCase(cls,lawyer):
        feature_list = []

        lawyer_id = str(lawyer)
        if lawyer_id.isdigit():
            lawyer_key = ndb.Key('Lawyer',int(lawyer_id))
            
            features = cls.query(cls.lawyer == lawyer_key).fetch()

            for feature in features:
                feature_list.append(feature.to_dict())
                
        if not feature_list:
            feature_list = None

        return feature_list
    
    @classmethod
    def get_all_feature(cls,lawyer_id):
        list_of_features = []
        
        if lawyer_id:
            lawyer = Lawyer.get_by_id(int(lawyer_id))
            features = cls.query(cls.lawyer == lawyer.key).fetch()
            if features:
                for feature in features:
                    list_of_features.append(feature.to_dict())
        
        if not list_of_features:
            list_of_features = None
        
        return list_of_features

    def to_dict(self):
        data = {}
        data['info'] = self.info
        data['case'] = None
        if self.case:
            case = self.case.get()
            data['case'] = case.to_dict()
    
        return data

