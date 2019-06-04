"""
PyFFI Absract Classes
=====================

Abstract classes for PyFFI
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
import typing

from pyffi.context import Context


class DerivedMeta(abc.ABCMeta, object):
    """Derived Meta, used for classes with custom meta classes"""


class Readable(metaclass=DerivedMeta):
    """Abstract Readable class"""

    @abc.abstractmethod
    def read(self, stream, context=Context()):
        """Read value from ``stream``, context may be required

        :arg stream: The bytes buffer to work with
        :type stream: typing.BinaryIO
        :arg context: The context the function has to work with
        :type context: typing.Optional[pyffi.context.Context]"""
        raise NotImplementedError


class Writeable(metaclass=DerivedMeta):
    """Abstract Writable class"""

    @abc.abstractmethod
    def write(self, stream, context=Context()):
        """Write value to ``stream``, context may be required

        :arg stream: the bytes to write to
        :type stream: typing.BinaryIO
        :arg context: The context to work with
        :type context: typing.Optional[pyffi.context.Context]"""
        raise NotImplementedError


class Duplex(Readable, Writeable):
    """Abstract Readable and Writable class"""
    pass


class Inspectable(metaclass=DerivedMeta):
    """Abstract Inspectable class"""

    @abc.abstractmethod
    def inspect(self, stream, context=Context()):
        """An inspect method used to quickly check if the buffer is correct

        :var stream: The stream to read from
        :type stream: typing.BinaryIO
        :var context: The context to work with
        :type context: typing.Optional[pyffi.context.Context]"""
        raise NotImplementedError


class FileFormatData(Duplex, Inspectable):
    """Abstract FileFormat Data class"""
