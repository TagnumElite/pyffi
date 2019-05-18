""""""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import time  # for timing stuff
import xml.sax
from typing import Dict, List

import pyffi.object_models
from pyffi.object_models.xml import StructAttribute
from pyffi.object_models.xml import XmlError
from pyffi.object_models.niftools_xml.version import Version


# noinspection PyMethodParameters
class MetaFileFormat(pyffi.object_models.xml.MetaFileFormat):
    """The MetaFileFormat metaclass transforms the XML description
    of a file format into a bunch of classes which can be directly
    used to manipulate files in this format.

    The actual implementation of the parser is delegated to
    pyffi.object_models.niftools_xml.FileFormat.
    """

    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare NifFormat to have metaclass
        MetaFileFormat, so upon creation of the NifFormat class,
        the __init__ function is called, with

        :param cls: The class created using MetaFileFormat, for example
            NifFormat.
        :param name: The name of the class, for example 'NifFormat'.
        :param bases: The base classes, usually (object,).
        :param dct: A dictionary of class attributes, such as 'xml_file_name'.
        """

        super(MetaFileFormat, cls).__init__(name, bases, dct)

        # preparation: make deep copy of lists of enums, structs, etc.
        cls.xml_enum = cls.xml_enum[:]
        cls.xml_alias = cls.xml_alias[:]
        cls.xml_bit_struct = cls.xml_bit_struct[:]
        cls.xml_struct = cls.xml_struct[:]

        # parse XML

        # we check dct to avoid parsing the same file more than once in
        # the hierarchy
        xml_file_name = dct.get('xml_file_name')
        if xml_file_name:
            # set up XML parser
            parser = xml.sax.make_parser()
            parser.setContentHandler(XmlSaxHandler(cls, name, bases, dct))

            # open XML file
            xml_file = cls.openfile(xml_file_name, cls.xml_file_path)

            # parse the XML file: control is now passed on to XmlSaxHandler
            # which takes care of the class creation
            cls.logger.debug("Parsing %s and generating classes."
                             % xml_file_name)
            start = time.clock()
            try:
                parser.parse(xml_file)
            finally:
                xml_file.close()
            cls.logger.debug("Parsing finished in %.3f seconds."
                             % (time.clock() - start))


class FileFormat(pyffi.object_models.xml.FileFormat, metaclass=MetaFileFormat):
    """This class can be used as a base class for niftools file formats
    described by an xml file."""
    pass


class XmlSaxHandler(pyffi.object_models.xml.XmlSaxHandler):
    def __init__(self, cls, name, bases, dct):
        super().__init__(cls, name, bases, dct)

        # initialize dictionaries
        # cls.version maps each supported version string to a version number
        cls.versions: Dict[str, Version] = {}
        # cls.games maps each supported game to a list of header version
        # numbers
        cls.games: Dict[str, str] = {}

    def start_parent_tag_file(self):
        if self.__tag == self.tag_version:
            self.push_tag(self.__tag)
            self.version_string = str(self.__attrs["id"])
            self.cls.versions[self.version_string] = Version(**self.__attrs)
        else:
            super(XmlSaxHandler, self).start_parent_tag_file()

    def document_tag_version(self):
        # fileformat -> version
        if self.stack[1] == self.tag_file:
            games_dict: Dict[str, str] = self.cls.games
        else:
            raise XmlError("Version parsing error at '%s'" % self.__chars)

        # update the games_dict dictionary
        for game_str in (str(g.strip()) for g in self.__chars.split(',')):
            if game_str.startswith('{{') and game_str.endswith('}}'):
                main_game = game_str.strip('{}')
                self.cls.versions[self.version_string].add_game(main_game)
                if main_game in games_dict:
                    raise XmlError("Duplicate Main Game: '%s'" % main_game)
                else:
                    games_dict[main_game] = self.version_string
            else:
                self.cls.versions[self.version_string].add_game(game_str)
