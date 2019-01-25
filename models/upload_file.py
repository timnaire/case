from google.appengine.ext import ndb
from models.case import Case

class UploadFile(ndb.Model):
    case = ndb.KeyProperty(kind=Case)
    case_file = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        uploadfile_id = str(kwargs.get('id'))

        if uploadfile_id and uploadfile_id.isdigit():
            uploadfile = cls.get_by_id(int(uploadfile_id))
        else:
            uploadfile = cls()

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Case',int(case_id))
            uploadfile.case = case_key
        
        if kwargs.get('case_file'):
            uploadfile.case_name = kwargs.get('case_file')

        uploadfile.put()
        return uploadfile

    @classmethod
    def get_all_files(cls,*args,**kwargs):
        case = None

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Case',int(case_id))
            if case_key:
                case = cls.query(cls.case == case_key).order(cls.created).fetch()
        
        if not case:
            case = None

        return case
        
    def to_dict(self):
        data = {}

        data['case'] = None
        if self.case:
            case = self.case.get()
            data['case'] = case.to_dict()
        
        data['case_file'] = self.case_file
        return data