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
from tic.core import Component
from tic.core import ComponentManager
from tic.core import ExtensionPoint
from tic.core import implements
from tic.web.api import IAuthenticator
from tic.web.api import IRequestFilter
from tic.web.api import IRequestHandler
from tic.web.api import Request
from tic.web.api import RequestDone


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

def dispatch_request(environ, start_response):
    """Main entry point for the Trac web interface.

    @param environ: the WSGI environment dict
    @param start_response: the WSGI callback for starting the response
    """

    env = Enviornment()
    req = Request(environ, start_response)

    try:
        dispatcher = RequestDispatcher(env)
        dispatcher.dispatch(req)
    except RequestDone:
        pass
    resp = req._response or []
    return resp

class Enviornment(Component, ComponentManager):
    pass

class RequestDispatcher(Component):
    """Web request dispatcher.

    This component dispatches incoming requests to registered handlers.
    """
    required = True

    authenticators = ExtensionPoint(IAuthenticator)
    handlers = ExtensionPoint(IRequestHandler)

    filters = ExtensionPoint(IRequestFilter)
    
#    filters = OrderedExtensionsOption('trac', 'request_filters',
#                                      IRequestFilter,
#                                      doc="""Ordered list of filters to apply to all requests
#            (''since 0.10'').""")
#
#    default_handler = MyBestHandler()
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
#    # Public API
#
#    def authenticate(self, req):
#        for authenticator in self.authenticators:
#            authname = authenticator.authenticate(req)
#            if authname:
#                return authname
#        else:
#            return 'anonymous'

    def dispatch(self, req):
        print "now we are starting"
        a = MyBestHandler(self.compmgr)
        a.process_request(req);
#        self.default_handler.process_request()
#        """Find a registered handler that matches the request and let it process
#        it.
#
#        In addition, this method initializes the HDF data set and adds the web
#        site chrome.
#        """
#        self.log.debug('Dispatching %r', req)
#        chrome = Chrome(self.env)
#
#        # Setup request callbacks for lazily-evaluated properties
#        req.callbacks.update({
#                             'authname': self.authenticate,
#                             'chrome': chrome.prepare_request,
#                             'hdf': self._get_hdf,
#                             'perm': self._get_perm,
#                             'session': self._get_session,
#                             'locale': self._get_locale,
#                             'tz': self._get_timezone,
#                             'form_token': self._get_form_token
#                             })
#
#        try:
#            try:
#                # Select the component that should handle the request
#                chosen_handler = None
#                try:
#                    for handler in self.handlers:
#                        if handler.match_request(req):
#                            chosen_handler = handler
#                            break
#                    if not chosen_handler:
#                        if not req.path_info or req.path_info == '/':
#                            chosen_handler = self.default_handler
#                    # pre-process any incoming request, whether a handler
#                    # was found or not
#                    chosen_handler = self._pre_process_request(req,
#                                                               chosen_handler)
#                except TracError, e:
#                    raise HTTPInternalError(e)
#                if not chosen_handler:
#                    if req.path_info.endswith('/'):
#                        # Strip trailing / and redirect
#                        target = req.path_info.rstrip('/').encode('utf-8')
#                        if req.query_string:
#                            target += '?' + req.query_string
#                        req.redirect(req.href + target, permanent=True)
#                    raise HTTPNotFound('No handler matched request to %s',
#                                       req.path_info)
#
#                req.callbacks['chrome'] = partial(chrome.prepare_request,
#                                                  handler=chosen_handler)
#
#                # Protect against CSRF attacks: we validate the form token
#                # for all POST requests with a content-type corresponding
#                # to form submissions
#                if req.method == 'POST':
#                    ctype = req.get_header('Content-Type')
#                    if ctype:
#                        ctype, options = cgi.parse_header(ctype)
#                    if ctype in ('application/x-www-form-urlencoded',
#                                 'multipart/form-data') and \
#                        req.args.get('__FORM_TOKEN') != req.form_token:
#                    if self.env.secure_cookies and req.scheme == 'http':
#                        msg = _('Secure cookies are enabled, you must '
#                                'use https to submit forms.')
#                    else:
#                        msg = _('Do you have cookies enabled?')
#                    raise HTTPBadRequest(_('Missing or invalid form token.'
#                                         ' %(msg)s', msg=msg))
#
#                # Process the request and render the template
#                resp = chosen_handler.process_request(req)
#                if resp:
#                    if len(resp) == 2: # Clearsilver
#                        chrome.populate_hdf(req)
#                        template, content_type = \
#                            self._post_process_request(req, * resp)
#                        # Give the session a chance to persist changes
#                        req.session.save()
#                        req.display(template, content_type or 'text/html')
#                    else: # Genshi
#                        template, data, content_type = \
#                            self._post_process_request(req, * resp)
#                        if 'hdfdump' in req.args:
#                            req.perm.require('TRAC_ADMIN')
#                            # debugging helper - no need to render first
#                            out = StringIO()
#                            pprint(data, out)
#                            req.send(out.getvalue(), 'text/plain')
#                        else:
#                            output = chrome.render_template(req, template,
#                                                            data,
#                                                            content_type)
#                            # Give the session a chance to persist changes
#                            req.session.save()
#                            req.send(output, content_type or 'text/html')
#                else:
#                    self._post_process_request(req)
#            except RequestDone:
#                raise
#            except:
#                # post-process the request in case of errors
#                err = sys.exc_info()
#                try:
#                    self._post_process_request(req)
#                except RequestDone:
#                    raise
#                except Exception, e:
#                    self.log.error("Exception caught while post-processing"
#                                   " request: %s",
#                                   exception_to_unicode(e, traceback=True))
#                raise err[0], err[1], err[2]
#        except PermissionError, e:
#            raise HTTPForbidden(to_unicode(e))
#        except ResourceNotFound, e:
#            raise HTTPNotFound(e)
#        except TracError, e:
#            raise HTTPInternalError(e)

class MyBestHandler(Component):
    implements(IRequestHandler)
    
    def match_request(self, req):
        return True

    def process_request(self, req):
        print "yay"




    