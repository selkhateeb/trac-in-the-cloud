

from tic.core import Component, implements
from tic.rpc.serviceHandler import ServiceHandler, ServiceMethod
from tic.web.api import IRequestHandler

class MyService(object):
    @ServiceMethod
    def sayHi(self, msg):
        return msg


class JsonRpcDispatcher(Component):
    implements(IRequestHandler)

    def match_request(self, req):
        """Return whether the handler wants to process the given request."""
        if(req.path_info == "/rpc"):
            return True
        return False

    def process_request(self, req):
        """
        handles all rpc calls and route all JSON Rpc Requests to its right
        method call

        Since we are only intrested in the "Command Design Pattern"
        this class is only going to handle that method
        
        JsonRPC v2
        
        {
            version: 2.0,
            method: execute,
            params: command
        }

        Life cycle of the Command Design Pattern
        ========

        - dojo sends RPC call with a command:
            RpcService.execute(CommandX())

        - JsonRpcDispatcher:
            - Finds the execute method
            - Deserialize the Command
            - Call the method
            - Returns CommandResult
            
        """
        json = req.read()
        ms = MyService()
        service = ServiceHandler(ms)
        data = service.handleRequest(json)
        req.send(data, "application/json")

#        cd = CommandDispatcher(self.compmgr)
#        cmd = LoginCommand()
#        cd.dispatch(cmd)

class DojoClassDispatcher(Component):
    implements(IRequestHandler)

    def match_request(self, req):
        """Return whether the handler wants to process the given request."""
        if(req.path_info == "/dojo"):
            return True
        return False

    def process_request(self, req):
        """
        this class maps "serializable" python classes to a dojo class to be
        able to use it in the Rpc request
        """

        print "this is a dojo class mapper that is coming very soon"


    