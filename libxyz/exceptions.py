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
All exceptions
"""

class XYZError(Exception):
    """
    Base exception
    """

    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class XYZRuntimeError(XYZError):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class XYZValueError(XYZError):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class ParseError(XYZError):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class LexerError(XYZError):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class PluginError(XYZError):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class SkinError(XYZError):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class VFSError(XYZError):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class UIError(XYZError):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class KeyManagerError(XYZError):
    pass
#++++++++++++++++++++++++++++++++++++++++++++++++

class FSRuleError(XYZError):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++

class DSLError(XYZError):
    pass
