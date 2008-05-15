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

import re

import libxyz

from libxyz.exceptions import PluginError
from libxyz.exceptions import KeyManagerError
from libxyz.exceptions import XYZValueError

class KeyManager(object):
    """
    Key bindings management class
    """

    CONTEXT_DEFAULT = u"DEFAULT"

    def __init__(self, xyz, confpath):
        self.xyz = xyz
        self.confpath = confpath
        self.keys = libxyz.ui.Keys()

        self._loaded_methods = {}
        self._bind_data = {}
        self._chain_keys = {}

        self._path_sel = libxyz.PathSelector()

        self._parse_config()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _parse_config(self):
        def _comment_cb(mo):
            return

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        def _load_cb(mo):
            try:
                self._load(mo.group("method"))
            except PluginError, e:
                raise XYZValueError(unicode(e))

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        def _bind_cb(mo):
            _force = False
            if mo.group("force") == "!":
                _force = True

            _method = mo.group("method")
            _shortcut = mo.group("shortcut")
            _context = mo.group("context")

            try:
                self._bind(_method, _shortcut, _context, _force)
            except KeyManagerError, e:
                raise XYZValueError(unicode(e))

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        def _chain_cb(mo):
            _chain = mo.group("shortcut")
            _context = mo.group("context")

            self._set_chain(_chain, _context)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        _comment_re = re.compile("^\s*#.*$")

        _load_re = re.compile("""
        ^                  # begin
        \s*                # leading spaces
        load               # keywoard load
        \s+                # one ore more spaces
        (?P<method>[\S:]+) # Full plugin path with method name
        \s*                # trailing spaces
        $                  # EOL
        """, re.VERBOSE)

        _bind_re = re.compile("""
        ^                   # begin
        \s*                 # leading spaces
        bind                # keywoard bind
        (?P<force>\!?)      # Optional ! (force) mark
        \s+                 # one ore more spaces
        (?P<method>[\w:]+)  # plugin ns-path and/or method name
        \s+                 # one ore more spaces
        to                  # keyword to
        \s+                 # one ore more spaces
        (?P<shortcut>\S+)   # shortcut
        (                   # optional context group begin
        \s+                 # one ore more spaces
        context             # keyword context
        \s+                 # one ore more spaces
        (?P<context>[\w_]+) # context name
        )?                  # context group end
        \s*                 # trailing spaces
        $                   # end
        """, re.VERBOSE)

        _chain_re = re.compile("""
        ^                   # begin
        \s*                 # leading spaces
        set                 # keywoard set
        \s+                 # one ore more spaces
        chain               # keywoard chain
        \s+                 # one ore more spaces
        key                 # keywoard key
        \s+                 # one ore more spaces
        (?P<shortcut>\S+)   # shortcut
        (                   # optional context group begin
        \s+                 # one ore more spaces
        context             # keyword context
        \s+                 # one ore more spaces
        (?P<context>[\w_]+) # context name
        )?                  # context group end
        \s*                 # trailing spaces
        $                   # end
        """, re.VERBOSE)

        _cbpool = {_comment_re: _comment_cb,
                   _load_re: _load_cb,
                   _bind_re: _bind_cb,
                   _chain_re: _chain_cb,
                  }

        _parser = libxyz.parser.RegexpParser(_cbpool)

        try:
            _file = open(self.confpath, "r")
        except IOError, e:
            raise XYZRuntimeError(_(u"Unable to open %s: %s" %
                                  (self.confpath, unicode(e))))

        try:
            _parser.parse(_file)
        finally:
            _file.close()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _load(self, method):
        """
        Load method
        """

        # Already loaded
        if method in self._loaded_methods:
            return

        _m = MethodName(method)

        # Wildcard
        if _m.method == _m.ALL:
            self._loaded_methods[method] = _m.ALL
        else:
            self._loaded_methods[method] = self.xyz.pm.from_load(_m.plugin,
                                                                 _m.method)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _bind(self, method, shortcut, context, force=False):
        """
        Bind a shortcut to a method
        @return: True on success, False otherwise, also raises exception
                 if method was not loaded
        """

        _shortcut = self.keys.make_shortcut(shortcut)

        if context is None:
            context = self.CONTEXT_DEFAULT

        if context not in self._bind_data:
            self._bind_data[context] = {}
        elif _shortcut in self._bind_data[context] and not force:
            # Already binded
            return

        _m = MethodName(method)
        _mobj = None

        # First check if methods were loaded by wildcard ALL
        if method not in self._loaded_methods:
            if "%s:%s" % (_m.plugin, _m.ALL) not in self._loaded_methods:
                raise KeyManagerError(_(u"Method %s not loaded" % method))

            # Else try to load specified method
            try:
                _mobj = self.xyz.pm.from_load(_m.plugin, _m.method)
            except PluginError, e:
                raise KeyManagerError(_(u"Load error: %s" % e))
        else:
            _mobj = self._loaded_methods[method]

        self._bind_data[context][_shortcut] = _mobj

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _set_chain(self, chain, context):
        """
        Set shortcut as chain key
        """

        _chain = self.keys.make_shortcut(chain)

        if context is None:
            context = self.CONTEXT_DEFAULT

        self._chain_keys[context] = _chain

#++++++++++++++++++++++++++++++++++++++++++++++++

class MethodName(object):
    """
    Abstract method name class
    """

    # Wildcard to load all public methods from plugin
    ALL = "*"

    def __init__(self, method):
        _split = method.split(":")

        self.full = method
        self.plugin = ":".join(_split[:-1])
        self.method = _split[-1]
