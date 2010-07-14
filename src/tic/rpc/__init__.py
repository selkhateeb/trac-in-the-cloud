

from tic.core import Component, implements
from tic.rpc.api import IJsonRpcService
from tic.rpc.serviceHandler import ServiceHandler
from tic.utils.importlib import import_module
from tic.web.api import IRequestHandler
from tic.web.dojo import to_dojo

#class MyService(object):
#    @ServiceMethod
#    def sayHi(self, msg):
#        return msg

class Fun(Component):
    implements(IJsonRpcService)

    def hi(self, msg):
        """returns msg"""
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
#        ms = MyService()
        service = ServiceHandler(self.compmgr)
        data = service.handleRequest(json)
        req.send(data, "application/json")
        

#        cd = CommandDispatcher(self.compmgr)
#        cmd = LoginCommand()
#        cd.dispatch(cmd)

class DojoClassDispatcher(Component):
    implements(IRequestHandler)

    def match_request(self, req):
        """Return whether the handler wants to process the given request."""
        if req.path_info.startswith("/dojo"):
            return True
        return False

    def process_request(self, req):
        """
        this class maps "serializable" python classes to a dojo class to be
        able to use it in the Rpc request
        """

        fully_qualified_class_name = req.path_info.split("/", 2)[2].replace("/", ".").replace(".xd.js", "")

        module, attr = fully_qualified_class_name.rsplit('.', 1)
        mod = import_module(module)
        cls = getattr(mod, attr)

        a = to_dojo(cls())
        req.send(a, "application/json")


    