from google.appengine.ext import ndb
from models.case import Case

class UploadFile(ndb.Model):
    case = ndb.KeyProperty(kind=Case)
    case_file = ndb.StringProperty()
    file_privacy = ndb.StringProperty()
    file_type= ndb.StringProperty()
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
            uploadfile.case_file = kwargs.get('case_file')
        if kwargs.get('file_privacy'):
            uploadfile.file_privacy = kwargs.get('file_privacy')
        if kwargs.get('file_type'):
            uploadfile.file_type = kwargs.get('file_type')

        uploadfile.put()
        return uploadfile
    
    @classmethod
    def get_research(cls,*args,**kwargs):
        list_files = []

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Case',int(case_id))
            if case_key:
                files = cls.query(cls.case == case_key, cls.file_type=="Research").order(cls.created).fetch()
                for f in files:
                    list_files.append(f.to_dict())
        
        if not list_files:
            list_files = None

        return list_files

    @classmethod
    def get_public_docs(cls,*args,**kwargs):
        list_files = []

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Case',int(case_id))
            if case_key:
                files = cls.query(cls.case == case_key, cls.file_type=="Public Documents").order(cls.created).fetch()
                for f in files:
                    list_files.append(f.to_dict())
        
        if not list_files:
            list_files = None

        return list_files

    @classmethod
    def get_all_files(cls,*args,**kwargs):
        list_files = []

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Case',int(case_id))
            if case_key:
                files = cls.query(cls.case == case_key).order(cls.created).fetch()
                for f in files:
                    list_files.append(f.file_dict())
        
        if not list_files:
            list_files = None

        return list_files
    
    @classmethod
    def research(cls,*args,**kwargs):
        list_files = []

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Case',int(case_id))
            if case_key:
                files = cls.query(cls.case == case_key, cls.file_type == "Research").order(cls.created).fetch()
                for f in files:
                    list_files.append(f.file_dict())
        
        if not list_files:
            list_files = None

        return list_files

    @classmethod
    def research(cls,*args,**kwargs):
        list_files = []

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Case',int(case_id))
            if case_key:
                files = cls.query(cls.case == case_key, cls.file_type == "Research").order(cls.created).fetch()
                for f in files:
                    list_files.append(f.file_dict())
        
        if not list_files:
            list_files = None

        return list_files

    def file_dict(self):
        data = {}

        data["file"] = self.case_file
        data['file_privacy'] = self.file_privacy
        data['file_type'] = self.file_type
        data['created'] = self.created
        data['updated'] = self.updated

        return data
        
    def to_dict(self):
        data = {}

        data['case'] = None
        if self.case:
            case = self.case.get()
            data['case'] = case.to_dict()
        
        data['case_file'] = self.case_file
        data['file_privacy'] = self.file_privacy
        data['file_type'] = self.file_type
        return data
