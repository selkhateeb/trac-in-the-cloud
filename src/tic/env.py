# -*- coding: utf-8 -*-
#
# Copyright (C) 2003-2009 Edgewall Software
# Copyright (C) 2003-2007 Jonas Borgström <jonas@edgewall.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.org/wiki/TracLicense.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#

from tic.core import Component, ComponentManager, ExtensionPoint, Interface, implements

__all__ = ['Environment']


class ISystemInfoProvider(Interface):
    """Provider of system information, displayed in the "About Trac" page and
    in internal error reports.
    """
    def get_system_info():
        """Yield a sequence of `(name, version)` tuples describing the name and
        version information of external packages used by a component.
        """

class Environment(Component, ComponentManager):
    """Trac environment manager.

    Trac stores project information in a Trac environment. It consists of a
    directory structure containing among other things:
     * a configuration file
     * an SQLite database (stores tickets, wiki pages...)
     * project-specific templates and plugins
     * wiki and ticket attachments
    """
    implements(ISystemInfoProvider)

    required = True
    
    system_info_providers = ExtensionPoint(ISystemInfoProvider)


    def __init__(self, options=[]):
        """Initialize the Trac environment.

        @param path:   the absolute path to the Trac environment
        @param create: if `True`, the environment is created and populated with
                       default data; otherwise, the environment is expected to
                       already exist.
        @param options: A list of `(section, name, value)` tuples that define
                        configuration options
        """
        ComponentManager.__init__(self)

        self.systeminfo = []

        self._href = self._abs_href = None


        from tic.loader import load_components
        load_components(self)

    def enable_component(self, cls):
        """Enable a component or module."""
        self._component_rules[self._component_name(cls)] = True

    @property
    def _component_rules(self):
        try:
            return self._rules
        except AttributeError:
            self._rules = {}
            for name, value in self.config.options('components'):
                if name.endswith('.*'):
                    name = name[:-2]
                self._rules[name.lower()] = value.lower() in ('enabled', 'on')
            return self._rules
        