"""
:mod:`pyffi.formats.psk` --- Unreal (.psk & .psa)
=================================================

A .psk file contains static geometry data, a .psa contains animation
keyframes.

Implementation
--------------

.. autoclass:: PskFormat
   :show-inheritance:
   :members:

Regression tests
----------------

Read a PSK file
^^^^^^^^^^^^^^^

>>> # check and read psk file
>>> from os.path import dirname
>>> dirpath = __file__
>>> for i in range(4): #recurse up to root repo dir
...     dirpath = dirname(dirpath)
>>> repo_root = dirpath
>>> format_root = os.path.join(repo_root, 'tests', 'formats', 'psk')
>>> file = os.path.join(format_root, 'examplemesh.psk')
>>> stream = open(file, 'rb')
>>> data = PskFormat.Data()
>>> data.inspect(stream)
>>> # do some stuff with header?
>>> data.read(stream) # doctest: +ELLIPSIS
>>> # do some stuff with data?

Parse all PSK files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in PskFormat.walkData(format_root):
...     try:
...         # the replace call makes the doctest also pass on windows
...         os_path = stream.name
...         split = (os_path.split(os.sep))[-4:]
...         rejoin = os.path.join(*split).replace(os.sep, "/")
...         print("reading %s" % rejoin)
...     except Exception:
...         print(
...             "Warning: read failed due corrupt file,"
...             " corrupt format description, or bug.") # doctest: +REPORT_NDIFF
reading tests/formats/psk/examplemesh.psk

Create an PSK file from scratch and write to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> data = PskFormat.Data()
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> data.write(stream)
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

import os
import re

import pyffi.engines
import pyffi.object_models
import pyffi.types.common
import pyffi.engines.xml
from pyffi.utils.graph import EdgeFilter


class PskFormat(pyffi.engines.xml.FileFormat):
    """This class implements the PSK format."""
    xml_file_name = 'psk.xml'
    # where to look for psk.xml and in what order:
    # PSKXMLPATH env var, or PskFormat module directory
    xml_file_path = [os.getenv('PSKXMLPATH'), os.path.dirname(__file__)]
    # file name regular expression match
    RE_FILENAME = re.compile(r'^.*\.psk$', re.IGNORECASE)

    # basic types
    int = pyffi.types.common.Int
    uint = pyffi.types.common.UInt
    byte = pyffi.types.common.Byte
    ubyte = pyffi.types.common.UByte
    char = pyffi.types.common.Char
    short = pyffi.types.common.Short
    ushort = pyffi.types.common.UShort
    float = pyffi.types.common.Float

    class ZString20(pyffi.types.common.FixedString):
        _len = 20

    class ZString64(pyffi.types.common.FixedString):
        _len = 64

    @staticmethod
    def version_number(version_str):
        """Converts version string into an integer.

        :param version_str: The version string.
        :type version_str: str
        :return: A version integer.
        """
        raise NotImplementedError

    class Data(pyffi.object_models.FileFormat.Data):
        """A class to contain the actual psk data."""
        version = 0  # no versioning, so far
        user_version = 0

        def inspect_quick(self, stream):
            """Quickly checks if stream contains PSK data, by looking at
            the first 8 bytes. Reads the signature and the version.

            :param stream: The stream to inspect.
            :type stream: file
            """
            pos = stream.tell()
            try:
                signat = stream.read(8)
                if signat == b'ACTRHEAD':
                    self.file_type = PskFormat.FileType.ACTRHEAD
                elif signat == b'ANIMHEAD':
                    self.file_type = PskFormat.FileType.ANIMHEAD
                else:
                    raise ValueError(
                        "Invalid signature (got '%s' instead of"
                        " b'ANIMHEAD' or b'ACTRHEAD'" % signat)
            finally:
                stream.seek(pos)

        # overriding pyffi.engines.FileFormat.Data methods

        def inspect(self, stream):
            """Quickly checks if stream contains PSK data, and reads
            everything up to the arrays.

            :param stream: The stream to inspect.
            :type stream: file
            """
            self.inspect_quick(stream)
            pos = stream.tell()
            try:
                self._header_value_.read(stream, self)
            finally:
                stream.seek(pos)

        def read(self, stream):
            """Read a psk file.

            :param stream: The stream from which to read.
            :type stream: ``file``
            """
            self.inspect_quick(stream)
            pyffi.engines.xml.struct_.StructBase.read(
                self, stream, self)

            # check if we are at the end of the file
            if stream.read(1):
                raise ValueError(
                    'end of file not reached: corrupt psk file?')

        def write(self, stream):
            """Write a psk file.

            :param stream: The stream to which to write.
            :type stream: ``file``
            """
            # write the data
            pyffi.engines.xml.struct_.StructBase.write(
                self, stream, self)

        # DetailNode

        def get_detail_child_nodes(self, edge_filter=EdgeFilter()):
            return self._header_value_.get_detail_child_nodes(
                edge_filter=edge_filter)

        # GlobalNode

        def get_global_child_nodes(self, edge_filter=EdgeFilter()):
            if self.file_type == PskFormat.FileType.ACTRHEAD:
                yield self.points
                yield self.wedges
                yield self.faces
                yield self.materials
                yield self.bones
                yield self.influences
            elif self.file_type == PskFormat.FileType.ANIMHEAD:
                yield self.bones
                yield self.animations
                yield self.raw_keys

    class Chunk:
        # GlobalNode

        def get_global_display(self):
            return self.chunk_id.decode("utf8", "ignore")


if __name__ == '__main__':
    import doctest

    doctest.testmod()
