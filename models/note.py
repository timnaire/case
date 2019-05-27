from google.appengine.ext import ndb
from models.case import Case
from models.lawyer import Lawyer

class Note(ndb.Model):
    case = ndb.KeyProperty(kind=Case)
    uploaded_by = ndb.KeyProperty()
    title = ndb.StringProperty()
    note = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def save(cls,*args,**kwargs):
        note_id = str(kwargs.get('id'))

        if note_id and note_id.isdigit():
            note = cls.get_by_id(int(note_id))
        else:
            note = cls()

        case_id = str(kwargs.get('case'))
        if case_id.isdigit():
            case_key = ndb.Key('Case',int(case_id))
            note.case = case_key
        
        if kwargs.get('uploaded_by'):
            note.uploaded_by = kwargs.get('uploaded_by')

        if kwargs.get('title'):
            note.title = kwargs.get('title')

        if kwargs.get('note'):
            note.note = kwargs.get('note')

        note.put()
        return note

    @classmethod
    def list_of_notes(cls,*args,**kwargs):
        listNotes = []
        case = Case.get_by_id(int(kwargs.get("case")))
        notes = cls.query(cls.case == case.key).fetch()

        if notes:
            for note in notes:
                listNotes.append(note.to_dict())

        if not listNotes:
            listNotes = None
        return listNotes

    def to_dict(self):
        data = {}
        
        data['note_id'] = self.key.id()
        data['uploaded_by'] = None
        if self.uploaded_by:
            uploaded_by = self.uploaded_by.get()
            data['uploaded_by'] = uploaded_by.to_dict()
        data['case'] = None
        if self.case:
            case = self.case.get()
            data['case'] = case.to_dict()
        data['note'] = self.note
        data['title'] = self.title

        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'

        return data