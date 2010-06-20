#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
from tic.conf import settings
from tic.core import Component, ExtensionPoint, implements
from tic.env import Environment
from tic.exceptions import ImproperlyConfigured
from tic.utils.importlib import import_module
from tic.web.api import IAuthenticator, IRequestHandler, Request, RequestDone

os.environ['TRAC_SETTINGS_MODULE'] = 'settings'

def dispatch_request(environ, start_response):
    """Main entry point for the Trac web interface.

    @param environ: the WSGI environment dict
    @param start_response: the WSGI callback for starting the response
    """

    env = Environment()
    req = Request(environ, start_response)

    try:
        dispatcher = RequestDispatcher(env)
        dispatcher.dispatch(req)
    except RequestDone:
        pass
    resp = req._response or []
    return resp

class DefaultHandler(Component):
    implements(IRequestHandler)

    def match_request(self, req):
        return True

    def process_request(self, req):
        print "yay"

class RequestDispatcher(Component):
    """Web request dispatcher.

    This component dispatches incoming requests to registered handlers.
    """
    required = True

    authenticators = ExtensionPoint(IAuthenticator)
    handlers = ExtensionPoint(IRequestHandler)

    filters = settings.REQUEST_FILTERS
    
#    filters = OrderedExtensionsOption('trac', 'request_filters',
#                                      IRequestFilter,
#                                      doc="""Ordered list of filters to apply to all requests
#            (''since 0.10'').""")
#
    default_handler = settings.DEFAULT_HANDLER
#    default_handler = ExtensionOption('trac', 'default_handler',
#                                      IRequestHandler, 'WikiModule',
#                                      """Name of the component that handles requests to the base URL.
#
#        Options include `TimelineModule`, `RoadmapModule`, `BrowserModule`,
#        `QueryModule`, `ReportModule`, `TicketModule` and `WikiModule`. The
#        default is `WikiModule`. (''since 0.9'')""")
#
#    default_timezone = Option('trac', 'default_timezone', '',
#                              """The default timezone to use""")
#
    # Public API

    def authenticate(self, req):
        for authenticator in self.authenticators:
            authname = authenticator.authenticate(req)
            if authname:
                return authname
        else:
            return 'anonymous'

    def dispatch(self, req):
        print "now we are starting"

        chosen_handler = None
        for handler in self.handlers:
            if handler.match_request(req):
                chosen_handler = handler
                handler.process_request(req)
                break
        a = self._load_default_handler()
        
        a.process_request(req)


    def _load_default_handler(self):
        """loads the default handler"""
        module, attr = self.default_handler.rsplit('.', 1)
        try:
            mod = import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing default handler module %s: "%s"' % (module, e))
        except ValueError, e:
            raise ImproperlyConfigured('Error importing default handler module. Is DEFAULT_HANDLER a correctly defined class')
        try:
            cls = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "%s" default handler backend' % (module, attr))
        return cls(self.compmgr)



    