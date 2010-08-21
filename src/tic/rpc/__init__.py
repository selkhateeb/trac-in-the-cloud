

from tic.core import Component, implements
from tic.rpc.api import IJsonRpcService
from tic.rpc.serviceHandler import ServiceHandler
from tic.utils.importlib import import_module
from tic.web.api import IRequestHandler
from tic.web.dojo import to_dojo

class JsonRpcDispatcher(Component):
    implements(IRequestHandler)

    def match_request(self, req):
        """Return whether the handler wants to process the given request."""
        return req.path_info == "/rpc"

    def process_request(self, req):
        """
        handles all rpc calls and route all JSON Rpc Requests to its right
        method call
            
        """
        json = req.read()
        service = ServiceHandler(self.compmgr)
        data = service.handle_request(json, req)
        req.send(data, "application/json")
        



    