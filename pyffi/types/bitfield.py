"""
Bitfield Types
==============

Implements common basic types in XML file format descriptions.


.. autoclass:: BitfieldBase
   :show-inheritance:
   :members:

.. autoclass:: BitfieldMember
   :show-inheritance:
   :members:
"""

# ------------------------------------------------------------------------
#  ***** BEGIN LICENSE BLOCK *****
#
#  Copyright © 2007-2019, Python File Format Interface.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * Neither the name of the Python File Format Interface
#       project nor the names of its contributors may be used to endorse
#       or promote products derived from this software without specific
#       prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
#  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#
#  ***** END LICENSE BLOCK *****
# ------------------------------------------------------------------------

import typing

from pyffi.abc import Duplex
from pyffi.context import Context
from pyffi.types.base import SimpleType


class BitfieldMember(object):
    """Field for bitfield members

    :var int _size: The bit width used by this member
    :var int _pos: The starting positing of this member
    """

    __slots__ = ('_size', '_pos', '_mask', '_default', '_value')

    def __init__(self, size, pos, mask, default=None):
        """

        :param int size: The bit width of the member
        :param int pos: The starting position of the member
        :param int mask: The value to isolate the bits for this member,
          before right-shifting it by its position to retrieve the value
        :param typing.Optional[Any] default: The default value
        """
        self._size = int(size)
        self._pos = int(pos)
        self._mask = int(mask)
        self._default = default
        self._value = default if default is not None else 0

    @property
    def default(self):
        return self._default

    def from_value(self, value):
        """Get the bitfield member value from the provided integer

        :param int value:
        :return: The value fetched from param
        :rtype: ``int``
        """
        self._value = (value & self._mask) >> self._pos
        return self._value

    def add_value(self, value):
        """Adds the bitfield member value to the provided integer

        :param int value:
        :return: The value with the bits inserted
        :rtype: ``int``
        """
        return (value & ~self._mask) | (self._value << self._pos)

    def get_value(self):
        """Gets the value of the bitfield member

        :rtype: `int`
        """
        return self._value

    def set_value(self, value):
        """Sets the bitfield member value

        :param int value: The value
        """
        self._value = value


class BitfieldBase(Duplex):
    """

    :var SimpleType _storage: The storage used for read and write
    :var typing.List[BitfieldMember] _attrs: The list of members
    """

    __slots__ = ('_storage', '_attrs')

    def __init__(self, storage, attrs):
        """

        :param storage: Anything that inherits ``BasicBase``,
          must also be able to convert to an integer
        :type storage: pyffi.types.base.SimpleType
        :param attrs: The bitfield members
        :type attrs: typing.List[BitfieldMember]
        """
        if not issubclass(storage, SimpleType):
            raise TypeError("storage must inherit SimpleType to work")

        self._storage = storage

        self._attrs = attrs

    def read(self, stream, context=Context()):
        self._storage.read(stream, context)

        val = self._storage.value
        for attr in self._attrs:
            attr.from_value(val)

    def write(self, stream, context=Context()):
        self._storage.write(stream, context)
