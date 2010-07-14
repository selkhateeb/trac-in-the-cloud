from tic.core import Component, ExtensionPoint, Interface, implements

##
## Implementation of the Command Design Pattern
##

class ICommand(Interface):
    """
    Command Deisgn pattern interface

    This object is shared between the client and the server
    and must be serializable
    """
    

class ICommandResult(Interface):
    """
    Command Result

    This object is shared between the client and the server
    and must be serializable
    """

class ICommandHandler(Interface):
    """
    handles the execution of a Command

    This lives in the server and its not serializable
    """

    def execute(command):
        """
        Executes the Command

        this must return an ICommandResult or throws CommandHandlerException
        """

    def roll_back(command):
        """
        Useful for doing undo stuff
        """

    def commnad():
        """
        Required method

        returns the command class
        """

class CommandDispatcher(Component):
    """
    Handles the execution of an incoming command and returns the Command Result
    """
    commands = ExtensionPoint(ICommand)

    command_handlers = ExtensionPoint(ICommandHandler)

    def dispatch(self, command):
        """Documentation"""

        for command_handler in self.command_handlers:
            if(isinstance(command, command_handler.command)):
                result = command_handler.execute(command)
                print result.hi


# a simple Login example
class LoginHandler(Component):
    implements(ICommandHandler)

    def __init__(self):
        """Documentation"""
        self.command = LoginCommand
    
    def execute(self, command):
        return LoginCommandResult(command.sayHi())

#    def command(self):
#        """ """
#        return LoginCommand


class LoginCommand():

    def sayHi(self):
        """Documentation"""
        return "hello"


class LoginCommandResult():

    def __init__(self, string):
        self.hi = string


##
## JSON RPC
##
class IJsonRpcService(Interface):
    """
    Marker interface for all json rpc services
    """