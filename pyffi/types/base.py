"""
Base Types
==========

These are abstract classes to be used by all types
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


import abc
import struct

import pyffi.utils.graph
from pyffi.abc import Duplex, DerivedMeta
from pyffi.context import Context
from pyffi.types.editable import EditableBase
from pyffi.types.editable import EditableSpinBox

_b = "".encode("ascii")  # py3k's b""
_b00 = "\x00".encode("ascii")  # py3k's b"\x00"


def _as_bytes(value):
    """Helper function which converts a string to bytes (this is useful for
    set_value in all string classes, which use bytes for representation).

    :return: The bytes representing the value.
    :rtype: C{bytes}

    >>> # following doctest fails on py3k, hence disabled
    >>> _as_bytes(u"\\u00e9defa") == u"\\u00e9defa".encode("utf-8") # doctest: +SKIP
    True

    >>> _as_bytes(123) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: ...
    """
    if isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        return value.encode("utf-8", "replace")
    else:
        raise TypeError("expected %s or %s" % (bytes.__name__, str.__name__))


def _as_str(value):
    """Helper function to convert bytes back to str. This is used in
    the __str__ functions for simple string types. If you want a custom
    encoding, use an explicit decode call on the value.

    >>> _as_str("123")
    '123'
    >>> _as_str(b"123")
    '123'
    """
    if not isinstance(value, (str, bytes)):
        raise TypeError("expected str or bytes")
    elif not value:
        return ''
    elif isinstance(value, str):
        # this always works regardless of the python version
        return value
    elif isinstance(value, bytes):
        # >= py3k: simply decode
        return value.decode("utf-8", "replace")
    elif isinstance(value, str):
        # < py3k: use ascii encoding to produce a str
        # (this avoids unicode errors)
        return value.encode("ascii", "replace")


class AnyType(pyffi.utils.graph.DetailNode, Duplex, metaclass=DerivedMeta):
    """Abstract base class from which all types are derived.

    Defines base class for any type that stores mutable data
    which is readable and writable, and can check for exchangeable
    alternatives."""

    def is_interchangeable(self, other):
        """Returns ``True`` if objects are interchangeable, that is,
        "close" enough to each other so they can be considered equal
        for practical purposes. This is useful for instance when comparing
        data and trying to remove duplicates.

        This default implementation simply checks for object identity.

        >>> x = AnyType()
        >>> y = AnyType()
        >>> x.is_interchangeable(y)
        False
        >>> x.is_interchangeable(x)
        True

        :return: ``True`` if objects are close, ``False`` otherwise.
        :rtype: ``bool``
        """
        return self is other

    def __hash__(self):
        """AnyType objects are mutable, so raise type error on hash
        calculation, as they cannot be safely used as dictionary keys.
        """
        raise TypeError("%s objects are unhashable" % self.__class__.__name__)


class _MetaSimpleType(DerivedMeta):
    """This metaclass binds the get_value and set_value methods to the
    value property. We need a metaclass for this because properties are
    non-polymorphic. Further reading:
    http://stackoverflow.com/questions/237432/python-properties-and-inheritance
    http://requires-thinking.blogspot.com/2006/03/note-to-self-python-properties-are-non.html

    .. todo:: Figure out how to get rid of this metaclass
    """

    def __init__(cls, name, bases, dct):
        # call base class constructor
        super(_MetaSimpleType, cls).__init__(name, bases, dct)
        # add value property
        cls.value = property(cls.get_value, cls.set_value,
                             None, cls.value.__doc__)


class SimpleType(AnyType, EditableBase, metaclass=_MetaSimpleType):
    """Base class from which all simple types are derived. Simple
    types contain data which is not divided further into smaller pieces,
    and that can represented efficiently by a (usually native) Python type,
    typically ``int``, ``float``, or ``str``.

    A brief example of usage:

    >>> class Short(SimpleType):
    ...     def __init__(self):
    ...         # for fun, let default value be 3
    ...         self._value = 3
    ...     def set_value(self, value):
    ...         # check type
    ...         if not isinstance(value, int):
    ...             raise TypeError("Expected int but got %s."
    ...                             % value.__class__.__name__)
    ...         # check range
    ...         if value < -0x8000 or value > 0x7fff:
    ...             raise ValueError("Value %i out of range." % value)
    ...         self._value = value
    >>> test = Short()
    >>> print(test)
    3
    >>> test.value = 255
    >>> print(test)
    255
    >>> test.value = 100000 # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: ...
    >>> test.value = "hello world" # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: ...

    Also override :meth:`read` and :meth:`write` if you wish to read and write data
    of this type, and :meth:`is_interchangeable` if you wish to declare data as
    equivalent.
    """

    # added here for documentation purposes - actually set in
    # metaclass
    @property
    def value(self):
        """A property which wraps the actual data. This property
        always calls :meth:`set_value` to assign the value, and ensures
        that the value is valid (type, range, ...). Unless you know
        what you are doing, always use the `value` property to change
        the data.
        """
        return None

    _value = None
    """The data."""

    def __str__(self):
        """String representation. This implementation is simply a wrapper
        around ``str`` on :attr:`_value`.

        :return: String representation.
        :rtype: ``str``
        """
        return str(self.get_value())

    def get_value(self):
        """Return the stored value.

        :return: The stored value.
        :rtype: typing.Any
        """
        return self._value

    def set_value(self, value):
        """Set stored value. Override this method to enable validation
        (type checking, range checking, and so on).

        :param value: The value to store.
        :type value: typing.Any
        """
        self._value = value

    # AnyType

    def is_interchangeable(self, other):
        """This checks for object identity of the value."""
        return isinstance(other, SimpleType) and (self._value is other._value)

    #
    # user interface functions come next
    # these functions are named after similar ones in the TreeItem example
    # at http://doc.trolltech.com/4.3/itemviews-simpletreemodel.html
    #

    # DetailNode

    def get_detail_display(self):
        """Display string for the detail tree. This implementation is simply
        a wrapper around ``str(self.:attr:`_value`)``.

        :return: String representation.
        :rtype: ``str``
        """
        return str(self)

    # editor functions: default implementation assumes that the value is
    # also suitable for an editor; override if not

    def get_editor_value(self):
        return self.get_value()

    def set_editor_value(self, value):
        return self.set_value(value)


class BinaryType(AnyType):
    """Abstract base class for binary data types."""

    @abc.abstractmethod
    def get_size(self, context=Context()):
        """Return number of bytes this type occupies in a file.

        :return: Number of bytes.
        :rtype: ``int``
        """
        raise NotImplementedError


class NumericalType(SimpleType, BinaryType, EditableSpinBox):
    """Base class for numerical types, float or ints.

    :var typing.Union[float,int] _value: The storage numerical number
    :var int _min: The minimum the numerical number man be
    :var int _max: The maximum the numerical number may be
    :var str _struct: The Python struct char
    :var int _size: The byte size the number takes up
    """

    @property
    @abc.abstractmethod
    def _min(self):
        raise NotImplementedError("_min must be defined")

    @property
    @abc.abstractmethod
    def _max(self):
        raise NotImplementedError("_max must be defined")

    @property
    @abc.abstractmethod
    def _struct(self):
        raise NotImplementedError("_struct must be defined")

    @property
    @abc.abstractmethod
    def _size(self):
        raise NotImplementedError("_size must be defined")

    def __init__(self):
        """Initialize the numerical class"""
        self._value = 0

    def get_value(self):
        """Get the numerical value

        :return: The storage numerical number
        :rtype: typing.Union[float, int]
        """
        return self._value

    def set_value(self, value):
        """Set the numerical value

        :param value: The numerical value to set to
        :type value: typing.Union[float, int]
        :raises ValueError: If the value is out of range
        :raises TypeError: If the value isn't a float or int
        """
        if isinstance(value, (float, int)):
            if self._min and value < self._min:
                raise ValueError("Value is too small (%i), expected at least (%i)" % (value, self._min))
            elif self._max and value > self._max:
                raise ValueError("Value is too large (%i), expected at most (%i)" % (value, self._max))

            self._value = value
        else:
            raise TypeError("Value must either be a int or float, got (%s) instead" % type(value))

    # Binary Type

    def get_size(self, context=None):
        return self._size

    # Duplex

    def read(self, stream, context=Context()):
        self._value = struct.unpack(context.byte_order + self._struct, stream.read(self._size))[0]

    def write(self, stream, context=Context()):
        stream.write(struct.pack(context.byte_order + self._struct, self._value))

    # EditableSpinBox

    def get_editor_minimum(self):
        return self._min

    def get_editor_maximum(self):
        return self._max


class BinarySimpleType(BinaryType, SimpleType):
    """Abstract class that implements BinaryType and SimpleType"""
