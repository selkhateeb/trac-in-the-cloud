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
from tic.core import Component, ExtensionPoint, TracError, implements
from tic.env import Environment
from tic.exceptions import ImproperlyConfigured
from tic.utils.importlib import import_module
from tic.web.api import HTTPNotFound, IAuthenticator, IRequestHandler, Request, RequestDone


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
        return False

    def process_request(self, req):
        print "yaaaay"

class RequestDispatcher(Component):
    """Web request dispatcher.

    This component dispatches incoming requests to registered handlers.
    """
    required = True

    authenticators = ExtensionPoint(IAuthenticator)
    handlers = ExtensionPoint(IRequestHandler)

    # Public API

    def authenticate(self, req):
        for authenticator in self.authenticators:
            authname = authenticator.authenticate(req)
            if authname:
                return authname
        else:
            return 'anonymous'

    def dispatch(self, req):

        # Setup request callbacks for lazily-evaluated properties
        req.callbacks.update({
            'authname': self.authenticate,
            'session': self._get_session,
#            'locale': self._get_locale,
#            'tz': self._get_timezone,
#            'form_token': self._get_form_token
        })
        
        # select handler
        chosen_handler = None
        try:
            for handler in self.handlers:
                if handler.match_request(req):
                    chosen_handler = handler
                    handler.process_request(req)
                    break

            # choose the default one if no handler found
            if not chosen_handler:
                if not req.path_info or req.path_info == '/':
                    chosen_handler = self._load_default_handler()
        except TracError, e:
            raise HTTPInternalError(e)

        
        if not chosen_handler:
            if req.path_info.endswith('/'):
                # Strip trailing / and redirect
                target = req.path_info.rstrip('/').encode('utf-8')
                if req.query_string:
                    target += '?' + req.query_string
                req.redirect(req.href + target, permanent=True)
            raise HTTPNotFound('No handler matched request to %s',
                               req.path_info)

        # pre-process any incoming request, whether a handler
        # was found or not
        chosen_handler = self._pre_process_request(req, chosen_handler)
        

        # process request
        chosen_handler.process_request(req)

        # TODO: post-process request


    # Private methods
    def _load_default_handler(self):
        """loads the default handler"""
        module, attr = settings.DEFAULT_HANDLER.rsplit('.', 1)
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

    def _pre_process_request(self, req, chosen_handler):
        for filter_ in settings.REQUEST_FILTERS:
            chosen_handler = filter_.pre_process_request(req, chosen_handler)
        return chosen_handler
    
    def _get_session(self, req):
        #TODO: implement a session
        from tic.web.sessions import Session
        return Session()
        pass





    