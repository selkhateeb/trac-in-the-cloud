from tic.core import Interface

class ICommandHandler(Interface):
    """
    handles the execution of a Command

    This lives in the server and its not serializable
    """

    command = None
    request = None
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
