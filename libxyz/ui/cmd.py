#-*- coding: utf8 -*
#
# Max E. Kuznecov ~syhpoon <syhpoon@syhpoon.name> 2008
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

import copy
import traceback
import re

import libxyz.core

from libxyz.ui import lowui
from libxyz.ui import Prompt
from libxyz.ui import XYZListBox
from libxyz.ui import NumEntry
from libxyz.ui import Keys
from libxyz.ui.utils import refresh
from libxyz.core.utils import ustring, bstring, is_func

class Cmd(lowui.FlowWidget):
    """
    Command line widget
    """

    resolution = (u"cmd",)

    LEFT = u"left"
    RIGHT = u"right"
    END = u"end"
    UNDER = u"under"

    def __init__(self, xyz):
        """
        @param xyz: XYZData instance

        Resources used: text, prompt
        """

        super(Cmd, self).__init__()

        self.xyz = xyz
        self._attr = lambda x: xyz.skin.attr(self.resolution, x)

        self._keys = Keys()

        self._text_attr = self._attr(u"text")
        self._data = []
        # Internal cursor index. Value is in range(0,len(self._data))
        self._index = 0
        # Virtual cursor index. Value is in range(0,maxcol)
        self._vindex = 0
        self._hindex = 0

        self.context = None
        self._panel = self.xyz.pm.load(":sys:panel")

        self._plugin = self._init_plugin()
        
        _conf = self._plugin.conf
        self.prompt = Prompt(_conf[u"prompt"], self._attr(u"prompt"))
        self._undo = libxyz.core.Queue(_conf[u"undo_depth"])
        self._history = libxyz.core.Queue(_conf[u"history_depth"])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _init_plugin(self):
        """
        Init virtual plugin
        """

        _cmd_plugin = libxyz.core.plugins.VirtualPlugin(self.xyz, u"cmd")
        _cmd_plugin.AUTHOR = u"Max E. Kuznecov <syhpoon@syhpoon.name>"
        _cmd_plugin.VERSION = u"0.1"
        _cmd_plugin.BRIEF_DESCRIPTION = u"Command line plugin"
        _cmd_plugin.FULL_DESCRIPTION = u"Command line plugin. "\
                                       u"It allows to enter, edit and "\
                                       u"execute commands."
        _cmd_plugin.DOC = u"Configuration variables:\n"\
                          u"undo_depth - Specifies how many undo levels to "\
                          u"keep. Default - 10\n"\
                          u"history_depth - Specifies how man entered "\
                          u"commands to keep. Default - 50\n"\
                          u"prompt - Command line prompt. Default - '$ '"

        _cmd_plugin.export(self.del_char)
        _cmd_plugin.export(self.del_char_left)
        _cmd_plugin.export(self.del_word_left)
        _cmd_plugin.export(self.del_word_right)
        _cmd_plugin.export(self.clear)
        _cmd_plugin.export(self.clear_left)
        _cmd_plugin.export(self.clear_right)
        _cmd_plugin.export(self.cursor_begin)
        _cmd_plugin.export(self.cursor_end)
        _cmd_plugin.export(self.cursor_left)
        _cmd_plugin.export(self.cursor_right)
        _cmd_plugin.export(self.cursor_word_left)
        _cmd_plugin.export(self.cursor_word_right)
        _cmd_plugin.export(self.is_empty)
        _cmd_plugin.export(self.undo)
        _cmd_plugin.export(self.undo_clear)
        _cmd_plugin.export(self.execute)
        _cmd_plugin.export(self.history_prev)
        _cmd_plugin.export(self.history_next)
        _cmd_plugin.export(self.history_clear)
        _cmd_plugin.export(self.show_history)
        _cmd_plugin.export(self.put_active_object)
        _cmd_plugin.export(self.put_active_object_path)
        _cmd_plugin.export(self.put_inactive_object)
        _cmd_plugin.export(self.put_inactive_object_path)
        _cmd_plugin.export(self.put_active_cwd)
        _cmd_plugin.export(self.put_inactive_cwd)
        _cmd_plugin.export(self.escape)
        _cmd_plugin.export(self.replace_aliases)

        self.xyz.pm.register(_cmd_plugin)

        self.context = _cmd_plugin.ns.pfull

        return _cmd_plugin

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def selectable(self):
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def rows(self, (maxcol,), focus=False):
        """
        Return the number of lines that will be rendered
        """

        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def render(self, (maxcol,), focus=False):
        """
        Render the command line
        """

        if self.prompt is not None:
            _canv_prompt = self.prompt.render((maxcol,))
        else:
            _canv_prompt = lowui.Text(u"").render((maxcol,))

        _data = [bstring(x) for x in self._get_visible(maxcol)]
        _text_len = abs(maxcol - self.prompt.length())

        _canv_text = lowui.AttrWrap(lowui.Text("".join(_data)),
                                    self._text_attr).render((maxcol,))
            
        _canvases = []
        
        if self.prompt.length() > 0:
            _canvases.append((_canv_prompt, None, False, self.prompt.length()))

        _canvases.append((_canv_text, 0, True, _text_len))

        canv = lowui.CanvasJoin(_canvases)
        canv.cursor = self.get_cursor_coords((maxcol,))

        return canv

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_visible(self, maxcol):
        """
        Calculate and return currently visible piece of cmd data
        """

        maxcol -= 1

        _plen = self.prompt.length()
        _dlen = len(self._data)
        _xindex = _plen + self._index

        if self._vindex >= maxcol:
            self._vindex = maxcol - 1

        if _plen + _dlen >= maxcol:
            _off = _xindex - maxcol
            _to = _xindex

            if _off < 0:
                _off = 0
                _to = maxcol - _plen + 1

            _data = self._data[_off:_to]
        else:
            _data = self._data

        return _data

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def get_cursor_coords(self, (maxcol,)):
        """
        Return the (x,y) coordinates of cursor within widget.
        """

        return self.prompt.length() + self._vindex, 0

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _put_object(self, char):
        self._data.insert(self._index, char)
        self._index += 1
        self._vindex += 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def keypress(self, size, key):
        """
        Process pressed key
        """
        
        _meth = self.xyz.km.process(key)

        if _meth is not None:
            return _meth()
        else:
            _good = [x for x in key if len(x) == 1]

            if _good:
                try:
                    map(lambda x: self._put_object(x), _good)
                except Exception, e:
                    xyzlog.error(_(ustring(str(e))))
                    xyzlog.debug(ustring(traceback.format_exc()))
                else:
                    self._invalidate()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _save_undo(self):
        """
        Save undo data
        """

        self._undo.push((self._index, copy.copy(self._data)))

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _restore_undo(self):
        """
        Restore one undo level
        """

        if self._undo:
            self._index, self._data = self._undo.pop()
            self._vindex = self._index

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _save_history(self):
        """
        Save typed command history
        """

        # Prevent duplicating entries
        if not self._history.tail() == self._data:
            self._history.push(copy.copy(self._data))

        self._hindex = len(self._history)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _clear_cmd(self):
        """
        Internal clear
        """

        self._data = []
        self._index = 0
        self._vindex = 0

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _move_cursor(self, direction, chars=None, topred=None):
        """
        Generic cursor moving procedure
        @param direction: LEFT or RIGHT
        @param chars: Number of character to move or END to move to the end
                      in corresponding direction
        @param topred: Predicate function which must return True if char
                       under the cursor is endpoint in move
        """

        _newindex = None

        # Using predicate
        if callable(topred):
            if direction == self.LEFT:
                _range = range(self._index - 1, 0, -1)
            else:
                _range = range(self._index + 1, len(self._data))

            for i in _range:
                if topred(self._data[i]):
                    _newindex = i
                    break

            if _newindex is None:
                # To start or end, depending on direction
                return self._move_cursor(direction, chars=self.END)

        elif direction == self.LEFT:
            if chars == self.END:
                _newindex = 0
            elif chars is not None and self._index >= chars:
                _newindex = self._index - chars

        elif direction == self.RIGHT:
            if chars == self.END:
                _newindex = len(self._data)

            elif (self._index + chars) <= len(self._data):
                _newindex = self._index + chars

        if _newindex is not None:
            self._index = _newindex
            self._vindex = _newindex
            self._invalidate()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @refresh
    def _delete(self, direction, chars=None, topred=None):
        """
        Generic delete procedure
        @param direction: LEFT, RIGHT or UNDER
        @param chars: Number of characters to delete
        @param topred: Predicate function which must return True if char
                       under the cursor is endpoint in delete
        """

        _newindex = None
        _delindex = None
        _newdata = None

        if callable(topred):
            if direction == self.LEFT:
                _range = range(self._index - 1, 0, -1)
            else:
                _range = range(self._index + 1, len(self._data))

            _found = False

            for i in _range:
                if topred(self._data[i]):
                    _found = True
                    if direction == self.LEFT:
                        _newindex = i
                        _newdata = self._data[:_newindex] + \
                                   self._data[self._index:]
                    else:
                        _newdata = self._data[:self._index] + self._data[i:]

                    self._save_undo()
                    break

            if not _found:
                return self._delete(direction, chars=self.END)

        elif direction == self.UNDER:
            if self._index >= 0 and self._index < len(self._data):
                _delindex = self._index

        elif direction == self.LEFT:
            if chars == self.END:
                self._save_undo()
                _newdata = self._data[self._index:]
                _newindex = 0
            elif chars is not None and self._index >= chars:
                _newindex = self._index - chars
                _delindex = _newindex

        elif direction == self.RIGHT:
            if chars == self.END:
                self._save_undo()
                _newdata = self._data[:self._index]

        if _newindex is not None:
            self._index = _newindex
            self._vindex = _newindex
        if _newdata is not None:
            self._data = _newdata
        if _delindex is not None:
            del(self._data[_delindex])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Public methods

    def del_char_left(self):
        """
        Delete single character left to the cursor
        """

        self._delete(self.LEFT, chars=1)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def del_char(self):
        """
        Delete single character under the cursor
        """

        return self._delete(self.UNDER)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def del_word_left(self):
        """
        Delete a word left to the cursor
        """

        return self._delete(self.LEFT, topred=lambda x: x.isspace())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def del_word_right(self):
        """
        Delete a word right to the cursor
        """

        return self._delete(self.RIGHT, topred=lambda x: x.isspace())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear(self):
        """
        Clear the whole cmd line
        """

        self._save_undo()
        self._clear_cmd()
        self._invalidate()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear_left(self):
        """
        Clear the cmd line from the cursor to the left
        """

        self._delete(self.LEFT, chars=self.END)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear_right(self):
        """
        Clear the cmd line from the cursor to the right
        """

        return self._delete(self.RIGHT, chars=self.END)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def cursor_begin(self):
        """
        Move cursor to the beginning of the command line
        """

        self._move_cursor(self.LEFT, chars=self.END)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def cursor_end(self):
        """
        Move cursor to the end of the command line
        """

        self._move_cursor(self.RIGHT, chars=self.END)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def cursor_left(self):
        """
        Move cursor left
        """

        self._move_cursor(self.LEFT, chars=1)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def cursor_right(self):
        """
        Move cursor right
        """

        self._move_cursor(self.RIGHT, chars=1)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def cursor_word_left(self):
        """
        Move cursor one word left
        """

        self._move_cursor(self.LEFT, topred=lambda x: x.isspace())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def cursor_word_right(self):
        """
        Move cursor one word right
        """

        self._move_cursor(self.RIGHT, topred=lambda x: x.isspace())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def execute(self):
        """
        Execute cmd contents
        """

        if not self._data:
            return

        self._save_history()

        _data = self.replace_aliases("".join(self._data))

        _cmd, _rest = split_cmd(_data)

        # Do not run shell, execute internal command
        if _cmd in self.xyz.conf["commands"]:
            try:
                self.xyz.conf["commands"][_cmd](
                    _rest if _rest is None else bstring(_rest))
            except Exception, e:
                xyzlog.error(_("Error executing internal command %s: %s") %
                             (_cmd, ustring(str(e))))
        else:
            if not hasattr(self, "_execf"):
                self._execf = self.xyz.pm.from_load(":core:shell", "execute")

            if not hasattr(self, "_reloadf"):
                self._reloadf =self.xyz.pm.from_load(":sys:panel",
                                                     "reload_all")
                
            self._execf(_data)
            self._reloadf()
        
        self._clear_cmd()
        self._invalidate()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def replace_aliases(self, data):
        """
        Check if first word of the command line (which is supposed to be a
        command to execute) is in our aliases table, if it is, replace it.

        @param data: String
        """

        cmd, _ = split_cmd(data)

        try:
            raw_alias = self.xyz.conf["aliases"][cmd]

            if isinstance(raw_alias, basestring):
                alias = raw_alias
            elif is_func(raw_alias):
                alias = raw_alias()
            else:
                xyzlog.error(_(u"Invalid alias type: %s") %
                             ustring(str(type(raw_alias))))
                return data
                

            return re.sub(r"^%s" % cmd, alias, data)
        except KeyError:
            return data
        except Exception, e:
            xyzlog.error(_(u"Unable to replace an alias %s: %s") %
                         (ustring(cmd), ustring(str(e))))
            return data
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    

    def is_empty(self):
        """
        Return True if cmd is empty, i.e. has no contents
        """

        return self._data == []

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def undo(self):
        """
        Restore one level from undo buffer
        """

        self._restore_undo()
        self._invalidate()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def undo_clear(self):
        """
        Clear undo buffer
        """

        self._undo.clear()
        self._invalidate()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def history_prev(self):
        """
        Scroll through list of saved commands backward
        """

        if self._hindex > 0:
            self._hindex -= 1
            self._data = copy.copy(self._history[self._hindex])
            self.cursor_end()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def history_next(self):
        """
        Scroll through list of saved commands forward
        """

        if self._hindex < len(self._history) - 1:
            self._hindex += 1
            self._data = copy.copy(self._history[self._hindex])
            self.cursor_end()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def history_clear(self):
        """
        Clear commands history
        """

        self._history.clear()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def show_history(self):
        """
        Show commands history list
        """

        def _enter_cb(num):
            if num >= len(self._history):
                return

            self._data = copy.copy(self._history[num])
            self.cursor_end()

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        _sel_attr = self.xyz.skin.attr(XYZListBox.resolution, u"selected")

        _wdata = []

        for i in range(len(self._history)):
            _wdata.append(NumEntry(u"".join([ustring(x) for x in
                                             self._history[i]]),
                                   _sel_attr, i,
                                   enter_cb=_enter_cb))

        _walker = lowui.SimpleListWalker(_wdata)
        _walker.focus = len(_walker) - 1

        _dim = tuple([x - 2 for x in self.xyz.screen.get_cols_rows()])

        _ek = [self._keys.ENTER]

        XYZListBox(self.xyz, self.xyz.top, _walker, _(u"History"),
                   _dim).show(exit_keys=_ek)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def put_active_object(self):
        """
        Put currently selected VFS object name in panel to cmd line
        """

        return self._put_engine(self._panel.get_selected().name)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def put_active_object_path(self):
        """
        Put currently selected VFS object full path in panel to cmd line
        """

        return self._put_engine(self._panel.get_selected().path)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def put_inactive_object(self):
        """
        Put selected VFS object name in inactive panel to cmd line
        """

        return self._put_engine(self._panel.get_selected_inactive().name)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def put_inactive_object_path(self):
        """
        Put selected VFS object full path in inactive panel to cmd line
        """

        return self._put_engine(self._panel.get_selected_inactive().path)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def put_active_cwd(self):
        """
        Put current working directory of active panel to cmd line
        """

        return self._put_engine(self._panel.cwd())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def put_inactive_cwd(self):
        """
        Put current working directory of inactive panel to cmd line
        """

        return self._put_engine(self._panel.cwd_inactive())
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _put_engine(self, obj):
        """
        Put list content to cmd
        """
        
        map(lambda x: self._put_object(x), 
            self.escape([bstring(x) for x in ustring(obj)]) + [" "])
        self._invalidate()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def escape(self, obj, join=False):
        """
        Escape filename
        @param obj: String to escape
        @param join: If False return list otherwise return joined string
        """
        
        result = []
        toescape = [" ", "'", '"', "*", "?", "\\", "&",
                    "(", ")",
                    "[", "]",
                    "{", "}",
                    ]

        for x in obj:
            if x in toescape:
                result.extend(["\\", x])
            else:
                result.append(x)

        return "".join(result) if join else result

#++++++++++++++++++++++++++++++++++++++++++++++++

def split_cmd(cmdline):
    """
    Return command name and the rest of the command line
    """

    _r =  cmdline.split(" ", 1)

    if len(_r) == 1:
        return _r[0], None
    else:
        return _r[0], _r[1]
