import logging
from google.appengine.ext import ndb
from models.case import Case
from models.client import Client
from models.lawyer import Lawyer

class UploadFile(ndb.Model):
    case = ndb.KeyProperty(kind=Case)
    case_file = ndb.StringProperty()
    file_name = ndb.StringProperty()
    file_privacy = ndb.StringProperty()
    file_type= ndb.StringProperty()
    uploaded_by = ndb.KeyProperty()
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
        if kwargs.get('file_name'):
            uploadfile.file_name = kwargs.get('file_name')
        if kwargs.get('file_privacy'):
            uploadfile.file_privacy = kwargs.get('file_privacy')
        if kwargs.get('file_type'):
            uploadfile.file_type = kwargs.get('file_type')
        
        if kwargs.get('uploaded_by'):
            uploadfile.uploaded_by = kwargs.get('uploaded_by')
            

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
                    list_files.append(f.file_dict())
        
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
                files = cls.query(cls.case == case_key, cls.file_type=="Public Document").order(cls.created).fetch()
                for f in files:
                    list_files.append(f.file_dict())
        
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
    def deleteFilesClient(cls,f,client_id):
        deleted = False

        if client_id:
            fe = UploadFile.get_by_id(int(f))
            ce = Client.get_by_id(int(client_id))
            if ce:
                ff = cls.query(cls.key == fe.key, cls.uploaded_by == ce.key)
                ff.key.delete()
                deleted = True
        return deleted

    @classmethod
    def deleteFilesLawyer(cls,f,lawyer_id):
        deleted = False

        if lawyer_id:
            fe = UploadFile.get_by_id(int(f))
            le = Lawyer.get_by_id(int(lawyer_id))
            if le:
                ff = cls.query(cls.key == fe.key, cls.uploaded_by == le.key)
                ff.key.delete()
                deleted = True
        return deleted

    def file_dict(self):
        data = {}
        data["file_id"] = self.key.id()
        data["case_file"] = self.case_file
        data['file_name'] = self.file_name
        data['file_privacy'] = self.file_privacy
        data['file_type'] = self.file_type

        if self.uploaded_by:
            uploadid = self.uploaded_by.get()
            data['uploaded_by'] = uploadid.key.id()

        return data
        
    def to_dict(self):
        data = {}
        
        data['case'] = None
        if self.case:
            case = self.case.get()
            data['case'] = case.to_dict()

        data['file_id'] = self.key.id()
        data['file_name'] = self.file_name
        data['case_file'] = self.case_file
        data['file_privacy'] = self.file_privacy
        data['file_type'] = self.file_type

        if self.uploaded_by:
            uploadid = self.uploaded_by.get()
            data['uploaded_by'] = uploadid.key.id()
            
        return data
