#-*- coding: utf8 -*
#
# Max E. Kuznecov ~syhpoon <mek@mek.uz.ua> 2008
#
# This file is part of XYZCommander.
# XYZCommander is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# XYZCommander is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser Public License for more details.
# You should have received a copy of the GNU Lesser Public License
# along with XYZCommander. If not, see <http://www.gnu.org/licenses/>.

import sys
import re
import os
import os.path

from libxyz.exceptions import PluginError, XYZValueError
from libxyz.parser import FlatParser

ABS_NS_PREFIX = u"xyz:plugins:"

def normalize_ns_path(path):
    """
    Normalize plugin namespace path
    """

    _path = path

    if _path.startswith(ABS_NS_PREFIX):
        _path = _path.replace(ABS_NS_PREFIX, u"")
    elif _path.startswith(u":"):
        _path = _path[1:]

    # Else suppose it is already normalized

    _path = _path.replace(u":", u".")

    return _path

#++++++++++++++++++++++++++++++++++++++++++++++++

def dec_normalize(method):
    """
    Normalize decorator
    """

    def _norm(instance, *args, **kwargs):
        _path, _rest = args[0], args[1:]
        _path = normalize_ns_path(_path)

        return method(instance, _path, *_rest, **kwargs)

    return _norm

#++++++++++++++++++++++++++++++++++++++++++++++++

class PluginManager(object):
    """
    Plugin manager class
    It is supposed to provide easy access to plugin data
    """

    PLUGIN_CLASS = u"XYZPlugin"

    def __init__(self, xyz, dirs):
        """
        @param xyz: XYZ data
        @param dirs: Plugin directories list
        @type dirs: list
        """

        if not isinstance(dirs, list):
            raise XYZValueError(_(u"Invalid argument type %s. List expected" %
                                  type(dirs)))
        else:
            sys.path.extend(dirs)

        self.xyz = xyz

        self.enabled = self._enabled_list()
        # Do not load all the enabled plugin at once
        # Do it on demand
        self._loaded = {}

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @dec_normalize
    def load(self, plugin, *initargs, **initkwargs):
        """
        Load and initiate required plugin
        @param plugin: Absoulute or relative plugin namespace path
        @param initargs: Necessary arguments to initiate plugin
        @param initkwargs: Necessary kw arguments to initiate plugin
        """

        if plugin not in self.enabled:
            raise PluginError(_(u"Plugin %s is disabled or does not exists" %
                                plugin))

        if self.is_loaded(plugin):
            return self.get_loaded(plugin)

        _path = u".".join((plugin, u"main"))

        # Import plugin
        # Plugin entry-point is XYZPlugin class in a main.py file
        try:
            _loaded = __import__(_path, globals(), locals(),[self.PLUGIN_CLASS])
        except ImportError, e:
            raise PluginError(_(u"Unable to load plugin %s: %s" % (plugin, e)))

        try:
            _loaded = getattr(_loaded, self.PLUGIN_CLASS)
        except AttributeError, e:
            raise PluginError(_(u"Unable to find required %s class" % \
                              self.PLUGIN_CLASS))

        # Initiate plugin
        _obj = _loaded(self.xyz, *initargs, **initkwargs)

        # Run prepare (constructor)
        _obj.prepare()

        self.set_loaded(plugin, _obj)

        return _obj

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @dec_normalize
    def reload(self, plugin, *initargs, **initkwargs):
        """
        Force load plugin if it's already in cache.
        """

        if self.is_loaded(plugin):
            self.del_loaded(plugin)

        return self.load(plugin, *initargs, **initkwargs)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @dec_normalize
    def from_load(self, plugin, method):
        """
        Load method from plugin.
        If plugin was not loaded before, load and initiate it first.

        @param plugin: Absoulute or relative plugin namespace path
        @param method: Public method name
        """

        if not self.is_loaded(plugin):
            _obj = self.load(plugin)
        else:
            _obj = self.get_loaded(plugin)

        if method not in _obj.public:
            raise PluginError(_(u"%s plugin instance does not export "\
                                u"%s method" % (plugin, method)))
        else:
            return _obj.public[method]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @dec_normalize
    def is_loaded(self, plugin):
        """
        Check if plugin already loaded
        @param plugin: Absoulute or relative plugin namespace path
        """

        return plugin in self._loaded

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @dec_normalize
    def get_loaded(self, plugin):
        """
        Return loaded and initiated inistance of plugin
        @param plugin: Absoulute or relative plugin namespace path
        """

        return self._loaded[plugin]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @dec_normalize
    def set_loaded(self, plugin, inst):
        """
        Set loaded and initiated inistance of plugin
        @param plugin: Absoulute or relative plugin namespace path
        @param inst: Plugin instance
        """

        self._loaded[plugin] = inst

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @dec_normalize
    def del_loaded(self, plugin):
        """
        Delete loaded instance from cache
        @param plugin: Absoulute or relative plugin namespace path
        """

        try:
            del(self._loaded[plugin])
        except KeyError:
            pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def shutdown(self):
        """
        Run destructors on all loaded plugins
        """

        for plugin_name in self._loaded:
            try:
                self._loaded[plugin_name].finalize()
            except StandardError:
                pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _enabled_list(self):
        """
        Make list of enabled plugins
        """

        _data = self.xyz.conf[u"xyz"][u"plugins"]
        return [normalize_ns_path(_pname) for _pname in _data if _data[_pname]]