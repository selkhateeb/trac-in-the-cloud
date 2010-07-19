
from google.appengine.ext import db

class MagicMapper():
    def magic(self, obj):
        arr = [x for x in dir(obj) if not x.startswith("__")]
        for attr in arr:
            val = getattr(obj, attr)
            setattr(self, attr, val)
            

class Event(db.Model, MagicMapper):
    """
    """
    fromDateTime = db.DateTimeProperty()
    toDateTime = db.DateTimeProperty()

    what = db.StringProperty()

    
            
