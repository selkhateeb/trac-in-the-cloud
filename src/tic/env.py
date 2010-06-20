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

