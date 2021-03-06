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

"""
Module contains user interface widgets

"""

__all__ = (
    'lowui',
    'display',
    'align',
    'colors',
    'utils',
    'Separator',
    'Size',
    'Keys',
    'Border',
    'XYZButton',
    'Box',
    'ButtonBox',
    'MessageBox',
    'YesNoBox',
    'InputBox',
    'ErrorBox',
    'Prompt',
    'XYZListBox',
    'ListEntry',
    'NumEntry',
    'BlockEntries',
    'Shortcut',
    'Cmd',
    'Panel',
)

import urwid as lowui

import display
import align
import colors
import utils

from size import Size
from separator import Separator

from keys import Keys
from border import Border
from xyzbutton import XYZButton
from box import Box
from box_button import ButtonBox
from box_message import MessageBox
from box_yesno import YesNoBox
from box_input import InputBox
from box_error import ErrorBox
from prompt import Prompt
from xyzlistbox import XYZListBox
from entry import ListEntry
from entry import NumEntry
from entry import BlockEntries
from shortcut import Shortcut
from cmd import Cmd
from panel import Panel
