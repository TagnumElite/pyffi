"""
Context
=======

Various contexts used by by Types, Engines and Formats.
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


class Context(object):
    """Base Context class

    :var pyffi.object_models.FileFormat.Data data: Data"""

    __slots__ = ('data',)

    def __init__(self, format_data=None):
        """

        :param format_data: FileFormat.Data
        :type format_data: pyffi.object_models.FileFormat.Data
        """

        self.data = format_data

    @property
    def byte_order(self):
        """Gets the byte order for structs

        :rtype: ``str``"""

        if self.data:
            return getattr(self.data, '_byte_order', '<')
        return '<'

    def get_type(self, name):
        if self.data:
            return getattr(self.data, name, None)


class TypeContext(Context):
    """This is context used during read and write of context-based types."""


class FileContext(Context):
    """File Context"""
