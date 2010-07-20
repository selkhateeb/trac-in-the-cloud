
from google.appengine.ext import db



class Event(db.Model):
    """
    """
    fromDateTime = db.DateTimeProperty()
    toDateTime = db.DateTimeProperty()

    what = db.StringProperty()

    
            
