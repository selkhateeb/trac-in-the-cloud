
from app.models import Event
from tic.core import Component, implements
from tic.rpc.api import ICommandHandler


class LoginCommand():
    """
    now this is cool
    """
    def __init__(self):
        """Documentation"""
        

class LoginCommandResult():

    def __init__(self, what, fromDateTime):
        self.what = what
        self.fromDateTime = fromDateTime


# a simple Login example
class LoginHandler(Component):
    implements(ICommandHandler)

    command = LoginCommand

    def execute(self, command):
        event = Event()
        event.magic(command)
        event.put()
        return LoginCommandResult(event.what, event.fromDateTime)





