import os.path

import fnmatch
import os
from tic.utils.importlib import import_module

__all__ = ['load_components']

def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


def _get_module_name(path):
    """takes an absolute path of a module and returns the fully
    qualified name of the module

    >>> _get_module_name("/Users/selkhateeb/Development/Projects/trac-in-the-cloud/src/tic/conf/global_settings.py")
    returns >> tic.conf.global_settings
    """
    relative_path = path.replace(os.path.abspath(os.curdir), '')
    # remove __init__.py .. (invalid module name)
#    relative_path = relative_path.replace("__init__.py", '')
    return relative_path[1:-3].replace("/", ".")

    

def load_py_files():
    """Loader that look for Python source files in the plugins directories,
    which simply get imported, thereby registering them with the component
    manager if they define any components.
    """
    def _load_py_files(env, search_path, auto_enable=None):
        for path in search_path:
            plugin_files = locate("*.py", path)
            for plugin_file in plugin_files:
                try:
                    plugin_name = os.path.basename(plugin_file[:-3])
                    module_name = _get_module_name(plugin_file)
                    import_module(module_name)
                    _enable_plugin(env, plugin_name)
                except NotImplementedError, e:
                    #print "Cant Implement This"
                    pass


    return _load_py_files



def get_plugins_dir(env):
    """Return the path to the `plugins` directory of the environment."""
    plugins_dir = os.path.realpath(".")
    return os.path.normcase(plugins_dir)

def _enable_plugin(env, module):
    """Enable the given plugin module if it wasn't disabled explicitly."""
    if env.is_component_enabled(module) is None:
        env.enable_component(module)

def load_components(env, extra_path=None, loaders=(load_py_files(),)):
    """Load all plugin components found on the given search path."""
    plugins_dir = get_plugins_dir(env)
    search_path = [plugins_dir]
    if extra_path:
        search_path += list(extra_path)

    for loadfunc in loaders:
        loadfunc(env, search_path, auto_enable=plugins_dir)

