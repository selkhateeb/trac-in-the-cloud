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

from trac.config import *
from trac.core import Component, ComponentManager, implements, Interface, \
                      ExtensionPoint
from trac.web.href import Href

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

#TODO: Make sure tgat we do not need a plugin dir everything is going to be in the src tree
#    shared_plugins_dir = PathOption('inherit', 'plugins_dir', '',
#        """Path to the //shared plugins directory//.
#
#        Plugins in that directory are loaded in addition to those in the
#        directory of the environment `plugins`, with this one taking
#        precedence.
#
#        (''since 0.11'')""")

    base_url = Option('trac', 'base_url', '',
        """Reference URL for the Trac deployment.
        
        This is the base URL that will be used when producing documents that
        will be used outside of the web browsing context, like for example
        when inserting URLs pointing to Trac resources in notification
        e-mails.""")

    base_url_for_redirect = BoolOption('trac', 'use_base_url_for_redirect',
            False, 
        """Optionally use `[trac] base_url` for redirects.
        
        In some configurations, usually involving running Trac behind a HTTP
        proxy, Trac can't automatically reconstruct the URL that is used to
        access it. You may need to use this option to force Trac to use the
        `base_url` setting also for redirects. This introduces the obvious
        limitation that this environment will only be usable when accessible
        from that URL, as redirects are frequently used. ''(since 0.10.5)''""")

    secure_cookies = BoolOption('trac', 'secure_cookies', False,
        """Restrict cookies to HTTPS connections.
        
        When true, set the `secure` flag on all cookies so that they are
        only sent to the server on HTTPS connections. Use this if your Trac
        instance is only accessible through HTTPS. (''since 0.11.2'')""")

    project_name = Option('project', 'name', 'My Project',
        """Name of the project.""")

    project_description = Option('project', 'descr', 'My example project',
        """Short description of the project.""")

    project_url = Option('project', 'url', '',
        """URL of the main project web site, usually the website in which
        the `base_url` resides. This is used in notification e-mails.""")

    project_admin = Option('project', 'admin', '',
        """E-Mail address of the project's administrator.""")

    project_admin_trac_url = Option('project', 'admin_trac_url', '.',
        """Base URL of a Trac instance where errors in this Trac should be
        reported.
        
        This can be an absolute or relative URL, or '.' to reference this
        Trac instance. An empty value will disable the reporting buttons.
        (''since 0.11.3'')""")

    project_footer = Option('project', 'footer',
                            N_('Visit the Trac open source project at<br />'
                               '<a href="http://trac.edgewall.org/">'
                               'http://trac.edgewall.org/</a>'),
        """Page footer text (right-aligned).""")

    project_icon = Option('project', 'icon', 'common/trac.ico',
        """URL of the icon of the project.""")



    #TODO: Logging system must be changed to google logging
#    log_type = Option('logging', 'log_type', 'none',
#        """Logging facility to use.
#
#        Should be one of (`none`, `file`, `stderr`, `syslog`, `winlog`).""")
#
#    log_file = Option('logging', 'log_file', 'trac.log',
#        """If `log_type` is `file`, this should be a path to the log-file.""")
#
#    log_level = Option('logging', 'log_level', 'DEBUG',
#        """Level of verbosity in log.
#
#        Should be one of (`CRITICAL`, `ERROR`, `WARN`, `INFO`, `DEBUG`).""")
#
#    log_format = Option('logging', 'log_format', None,
#        """Custom logging format.
#
#        If nothing is set, the following will be used:
#
#        Trac[$(module)s] $(levelname)s: $(message)s
#
#        In addition to regular key names supported by the Python logger library
#        (see http://docs.python.org/library/logging.html), one could use:
#         - $(path)s     the path for the current environment
#         - $(basename)s the last path component of the current environment
#         - $(project)s  the project name
#
#        Note the usage of `$(...)s` instead of `%(...)s` as the latter form
#        would be interpreted by the ConfigParser itself.
#
#        Example:
#        `($(thread)d) Trac[$(basename)s:$(module)s] $(levelname)s: $(message)s`
#
#        ''(since 0.10.5)''""")

    def __init__(self, create=False, options=[]):
        """Initialize the Trac environment.
        
        @param create: if `True`, the environment is created and populated with
                       default data; otherwise, the environment is expected to
                       already exist.
        @param options: A list of `(section, name, value)` tuples that define
                        configuration options
        """
        ComponentManager.__init__(self)

        self.setup_config(load_defaults=create)
        self.setup_log()

        self.systeminfo = []
        from trac import core, __version__ as VERSION
        self.log.info('-' * 32 + ' environment startup [Trac %s] ' + '-' * 32,
                      get_pkginfo(core).get('version', VERSION))
        self._href = self._abs_href = None

        from trac.loader import load_components
#        plugins_dir = self.shared_plugins_dir

        #TODO: Clean up the load_comonents
        load_components(self, plugins_dir and (plugins_dir,))

        if create:
            self.create(options)
        else:
            self.verify()

    def get_systeminfo(self):
        """Return a list of `(name, version)` tuples describing the name and
        version information of external packages used by Trac and plugins.
        """
        info = self.systeminfo[:]
        for provider in self.system_info_providers:
            info.extend(provider.get_system_info() or [])
        info.sort(key=lambda (name, version): (name != 'Trac', name.lower()))
        return info

    # ISystemInfoProvider methods

    def get_system_info(self):
        from trac import core, __version__ as VERSION
        yield 'Trac', get_pkginfo(core).get('version', VERSION)
        yield 'Python', sys.version
        from trac.util.datefmt import pytz
        if pytz is not None:
            yield 'pytz', pytz.__version__
    
    def component_activated(self, component):
        """Initialize additional member variables for components.
        
        Every component activated through the `Environment` object gets three
        member variables: `env` (the environment object), `config` (the
        environment configuration) and `log` (a logger object)."""
        component.env = self
        component.config = self.config
        component.log = self.log

    def _component_name(self, name_or_class):
        name = name_or_class
        if not isinstance(name_or_class, basestring):
            name = name_or_class.__module__ + '.' + name_or_class.__name__
        return name.lower()

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
        
    def is_component_enabled(self, cls):
        """Implemented to only allow activation of components that are not
        disabled in the configuration.
        
        This is called by the `ComponentManager` base class when a component is
        about to be activated. If this method returns `False`, the component
        does not get activated. If it returns `None`, the component only gets
        activated if it is located in the `plugins` directory of the
        enironment.
        """
        component_name = self._component_name(cls)

        # Disable the pre-0.11 WebAdmin plugin
        # Please note that there's no recommendation to uninstall the
        # plugin because doing so would obviously break the backwards
        # compatibility that the new integration administration
        # interface tries to provide for old WebAdmin extensions
        if component_name.startswith('webadmin.'):
            self.log.info('The legacy TracWebAdmin plugin has been '
                          'automatically disabled, and the integrated '
                          'administration interface will be used '
                          'instead.')
            return False
        
        rules = self._component_rules
        cname = component_name
        while cname:
            enabled = rules.get(cname)
            if enabled is not None:
                return enabled
            idx = cname.rfind('.')
            if idx < 0:
                break
            cname = cname[:idx]

        # By default, all components in the trac package are enabled
        return component_name.startswith('trac.') or None

    def enable_component(self, cls):
        """Enable a component or module."""
        self._component_rules[self._component_name(cls)] = True

    def verify(self):
        """Verify that the provided path points to a valid Trac environment
        directory."""
        #TODO: get the version Model and verify
#        fd = open(os.path.join(self.path, 'VERSION'), 'r')
#        try:
#            assert fd.read(26) == 'Trac Environment Version 1'
#        finally:
#            fd.close()

    def create(self, options=[]):
        """Create the basic directory structure of the environment, initialize
        the database and populate the configuration file with default values.

        If options contains ('inherit', 'file'), default values will not be
        loaded; they are expected to be provided by that file or other options.
        """
        # Create the directory structure
#        if not os.path.exists(self.path):
#            os.mkdir(self.path)
#        os.mkdir(self.get_log_dir())
#        os.mkdir(self.get_htdocs_dir())
#        os.mkdir(os.path.join(self.path, 'plugins'))
#
#        # Create a few files
#        create_file(os.path.join(self.path, 'VERSION'),
#                    'Trac Environment Version 1\n')
#        create_file(os.path.join(self.path, 'README'),
#                    'This directory contains a Trac environment.\n'
#                    'Visit http://trac.edgewall.org/ for more information.\n')
#
#        # Setup the default configuration
#        os.mkdir(os.path.join(self.path, 'conf'))
#        create_file(os.path.join(self.path, 'conf', 'trac.ini'))
#        create_file(os.path.join(self.path, 'conf', 'trac.ini.sample'))
#        skip_defaults = any((section, option) == ('inherit', 'file')
#                            for section, option, value in options)
#        self.setup_config(load_defaults=not skip_defaults)
#        for section, name, value in options:
#            self.config.set(section, name, value)
#        self.config.save()
#        # Full reload to get 'inherit' working
#        self.config.parse_if_needed(force=True)
#        del self._rules
#
#        # Create the database
#        DatabaseManager(self).init_db()

    def setup_config(self, load_defaults=False):
        """Load the configuration file."""
        #TODO: AppEngine Model for the trac.ini
#        self.config = Configuration(os.path.join(self.path, 'conf',
#                                                 'trac.ini'))
#        if load_defaults:
#            for section, default_options in self.config.defaults(self).items():
#                for name, value in default_options.items():
#                    if any(parent[section].contains(name, defaults=False)
#                           for parent in self.config.parents):
#                        value = None
#                    self.config.set(section, name, value)

    def get_templates_dir(self):
        """Return absolute path to the templates directory."""
        return os.path.join(self.path, 'templates')

    def get_htdocs_dir(self):
        """Return absolute path to the htdocs directory."""
        return os.path.join(self.path, 'htdocs')

    def get_log_dir(self):
        """Return absolute path to the log directory."""
        return os.path.join(self.path, 'log')

    def setup_log(self):
        """Initialize the logging sub-system."""
        #TODO: use AppEngine logging
#        from trac.log import logger_handler_factory
#        logtype = self.log_type
#        logfile = self.log_file
#        if logtype == 'file' and not os.path.isabs(logfile):
#            logfile = os.path.join(self.get_log_dir(), logfile)
#        format = self.log_format
#        if format:
#            format = format.replace('$(', '%(') \
#                     .replace('%(path)s', self.path) \
#                     .replace('%(basename)s', os.path.basename(self.path)) \
#                     .replace('%(project)s', self.project_name)
#        self.log, self._log_handler = logger_handler_factory(
#            logtype, logfile, self.log_level, self.path, format=format)

    def get_known_users(self, cnx=None):
        """Generator that yields information about all known users, i.e. users
        that have logged in to this Trac environment and possibly set their name
        and email.

        This function generates one tuple for every user, of the form
        (username, name, email) ordered alpha-numerically by username.

        @param cnx: the database connection; if ommitted, a new connection is
                    retrieved
        """
        #TODO: Do something
#        if not cnx:
#            cnx = self.get_db_cnx()
#        cursor = cnx.cursor()
#        cursor.execute("SELECT DISTINCT s.sid, n.value, e.value "
#                       "FROM session AS s "
#                       " LEFT JOIN session_attribute AS n ON (n.sid=s.sid "
#                       "  and n.authenticated=1 AND n.name = 'name') "
#                       " LEFT JOIN session_attribute AS e ON (e.sid=s.sid "
#                       "  AND e.authenticated=1 AND e.name = 'email') "
#                       "WHERE s.authenticated=1 ORDER BY s.sid")
#        for username, name, email in cursor:
#            yield username, name, email

    def _get_href(self):
        if not self._href:
            self._href = Href(urlsplit(self.abs_href.base)[2])
        return self._href
    href = property(_get_href, 'The application root path')

    def _get_abs_href(self):
        if not self._abs_href:
            if not self.base_url:
                self.log.warn('base_url option not set in configuration, '
                              'generated links may be incorrect')
                self._abs_href = Href('')
            else:
                self._abs_href = Href(self.base_url)
        return self._abs_href
    abs_href = property(_get_abs_href, 'The application URL')


