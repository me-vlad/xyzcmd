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

from libxyz.exceptions import XYZValueError

class Queue(list):
    """
    Fixed-sized list
    """

    def __init__(self, maxsize):
        super(Queue, self).__init__()

        try:
            self.maxsize = int(maxsize)
        except ValueError:
            raise XYZValueError(_(u"Max-size must be of integer type"))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def push(self, item):
        """
        Push a new item to queue. If queue already contains maxsize elements
        replace the oldest one.
        """

        if self.maxsize <= 0:
            return
        elif len(self) == self.maxsize:
            del(self[0])

        self.append(item)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def pop(self):
        """
        Pop item from the beginning of the queue
        Raise IndexError if queue is empty
        """

        return super(Queue,self).pop(0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear(self):
        """
        Clear queue
        """

        del self[:]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def tail(self):
        """
        Return tail element
        """

        _len = len(self)

        if _len:
            return self[_len - 1]
        else:
            return None
