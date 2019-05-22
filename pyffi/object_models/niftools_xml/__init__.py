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

import collections
import logging
import time  # for timing stuff
import xml.sax
from typing import Dict, List

import pyffi.object_models
from pyffi.errors import PyFFIException
from pyffi.object_models.xml import XmlSaxHandler as OldXmlHandler
from pyffi.object_models.xml import XmlError
from pyffi.object_models.niftools_xml.expression import Expression
from pyffi.object_models.niftools_xml.version import Version
from pyffi.object_models.xml.struct_ import StructBase


class StructAttribute(object):
    """Helper class to collect attribute data of struct add tags."""

    name = None
    """The name of this member variable."""

    type_ = None
    """The type of this member variable (type is ``str`` for forward
    declarations, and resolved to :class:`BasicBase` or
    :class:`StructBase` later).
    """

    default = None
    """The default value of this member variable."""

    template = None
    """The template type of this member variable (initially ``str``,
    resolved to :class:`BasicBase` or :class:`StructBase` at the end
    of the xml parsing), and if there is no template type, then this
    variable will equal ``type(None)``.
    """

    arg = None
    """The argument of this member variable."""

    arr1 = None
    """The first array size of this member variable, as
    :class:`Expression` or ``type(None)``.
    """

    arr2 = None
    """The second array size of this member variable, as
    :class:`Expression` or ``type(None)``.
    """

    cond = None
    """The condition of this member variable, as
    :class:`Expression` or ``type(None)``.
    """

    excludeT = None
    """
    """

    onlyT = None
    """
    """

    since = None
    """The first version this member exists, as ``int``, and ``None`` if
    there is no lower limit.
    """

    until = None
    """The last version this member exists, as ``int``, and ``None`` if
    there is no upper limit.
    """

    vercond = None
    """The version condition this member exists, as ``int``, and ``None`` if
    it exists for all user versions.
    :class:`Expression` or ``type(None)``.
    """

    is_abstract = False
    """Whether the attribute is abstract or not (read and written)."""

    def __init__(self, cls, attrs):
        """Initialize attribute from the xml attrs dictionary of an
        add tag.

        :param cls: The class where all types reside.
        :param attrs: The xml add tag attribute dictionary."""
        # mandatory parameters
        self.displayname = attrs["name"]
        self.name = cls.name_attribute(self.displayname)
        try:
            attrs_type_str = attrs["type"]
        except KeyError:
            raise AttributeError("'%s' is missing a type attribute"
                                 % self.displayname)
        if attrs_type_str != "TEMPLATE":
            try:
                self.type_ = getattr(cls, attrs_type_str)
            except AttributeError:
                # forward declaration, resolved at endDocument
                self.type_ = attrs_type_str
        else:
            self.type_ = type(None)  # type determined at runtime
        # optional parameters
        # TODO: Default fetch from tokens
        self.default = attrs.get("default")
        self.template = attrs.get("template")  # resolved in endDocument
        self.arg = attrs.get("arg")
        self.arr1 = attrs.get("arr1")
        self.arr2 = attrs.get("arr2")
        self.cond = attrs.get("cond")
        self.vercond = attrs.get("vercond")
        self.since = attrs.get("ver1")  # TODO: Replace get var to since when nif.xml is updated
        self.until = attrs.get("ver2")  # TODO: Replace get var to until when nif.xml is updated
        self.excludeT = attrs.get("excludeT")
        self.onlyT = attrs.get("onlyT")
        self.doc = ""  # handled in xml parser's characters function
        self.is_abstract = (attrs.get("abstract") == "1")

        # post-processing
        if self.default:
            try:
                tmp = self.type_()
                tmp.set_value(self.default)
                self.default = tmp.get_value()
                del tmp
            except Exception:
                # conversion failed; not a big problem
                self.default = None
        if self.arr1:
            self.arr1 = Expression(self.arr1, cls.name_attribute)
        if self.arr2:
            self.arr2 = Expression(self.arr2, cls.name_attribute)
        if self.cond:
            self.cond = Expression(self.cond, cls.name_attribute)
        if self.vercond:
            self.vercond = Expression(self.vercond, cls.name_attribute)
        if self.arg:
            try:
                self.arg = int(self.arg)
            except ValueError:
                self.arg = cls.name_attribute(self.arg)

        # TODO: Since and Until must fetch tokens and use them
        if self.since:
            self.since = cls.version_number(self.since)
        if self.until:
            self.until = cls.version_number(self.until)


# noinspection PyMethodParameters
class MetaFileFormat(pyffi.object_models.MetaFileFormat):
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


class FileFormat(pyffi.object_models.FileFormat, metaclass=MetaFileFormat):
    """This class can be used as a base class for file formats
    described by an xml file.

    """
    xml_file_name = None  #: Override.
    xml_file_path = None  #: Override.
    logger = logging.getLogger("pyffi.object_models.niftools_xml")
    debug: bool = False

    # We also keep an ordered list of all classes that have been created.
    # The xml_struct list includes all xml generated struct classes,
    # including those that are replaced by a native class in cls (for
    # instance NifFormat.String). The idea is that these lists should
    # contain sufficient info from the xml so they can be used to write
    # other python scripts that would otherwise have to implement their own
    # xml parser. See makehsl.py for an example of usage.
    #
    # (note: no classes are created for basic types, so no list for those)
    xml_enum = []
    xml_alias = []
    xml_bit_struct = []
    xml_struct = []
    xml_token = []
    versions = {}
    scopes = {}
    tokens = {}


class XmlSaxHandler(OldXmlHandler):
    # We inherit OldSaxHandler, add a 0 on the end to not influence OldXmlHandler
    tag_token = 110
    tag_subtoken = 120

    # for compatibility with niftools
    tags_extra: Dict[str, int] = {
        "niftoolsxml": OldXmlHandler.tag_file,
        "compound": OldXmlHandler.tag_struct,
        "niobject": OldXmlHandler.tag_struct,
        "bitflags": OldXmlHandler.tag_bit_struct,
        "token": tag_token,
    }

    def __init__(self, cls: FileFormat, name: str, bases, dct):
        super().__init__(cls, name, bases, dct)

        # initialize dictionaries
        # cls.version maps each supported version string to a version number
        cls.versions: Dict[str, Version] = {}
        # cls.games maps each supported game to a list of header version
        # numbers
        cls.games: Dict[str, str] = collections.OrderedDict()

        #
        cls.tokens = collections.OrderedDict()

        # Used for scope lookup, eg scope['vercond'] == ['verexpr', 'global', 'operator']
        cls.scopes: Dict[str, List[str]] = {}

        # Current token group name
        self.current_token = None

        # Completed struct additions for each struct
        self.completed_struct_additions: Dict[str, List[str]] = {}

    def start_parent_tag_file(self):
        if self.__tag == self.tag_version:
            self.push_tag(self.__tag)
            self.version_string = str(self.__attrs["id"])
            self.cls.versions[self.version_string] = Version(**self.__attrs)
        elif self.__tag == self.tag_struct:
            self.push_tag(self.__tag)
            self.class_name = self.__attrs["name"]
            # struct types can be organized in a hierarchy
            # if inherit attribute is defined, then look for corresponding
            # base block
            class_basename = self.__attrs.get("inherit")
            if class_basename:
                # if that base struct has not yet been assigned to a
                # class, then we have a problem
                try:
                    self.class_bases += (getattr(self.cls, class_basename),)
                except KeyError:
                    raise XmlError(
                        "typo, or forward declaration of struct %s"
                        % class_basename)
            else:
                self.class_bases = (StructBase,)
            # istemplate attribute is optional
            # if not set, then the struct is not a template
            # set attributes (see class StructBase)
            self.class_dict = {
                "_is_template": self.__attrs.get("istemplate", "0") in ("true", "1"),
                "_attrs": [],
                "_games": {},
                "_since": self.__attrs.get("since"),
                "_until": self.__attrs.get("until"),
                "_versions": self.__attrs.get("versions", "").split(" "),
                "__attrs": dict(self.__attrs),
                "__doc__": "",
                "__module__": self.cls.__module__,
            }
        elif self.__tag == self.tag_token:
            self.push_tag(self.__tag)

            name = self.__attrs['name']
            self.current_token = name

            if name not in self.tags_extra:
                self.tags_extra[name] = self.tag_subtoken

            if name in self.cls.tokens:
                raise XmlError("Token '%s' already defined in file" % name)
            else:
                self.cls.tokens[name] = {}

            attrs = self.__attrs['attrs']
            for x in attrs.split(' '):
                if x in self.cls.scopes:
                    self.cls.scopes[x].append(name)
                else:
                    self.cls.scopes[x] = [name]
        else:
            super(XmlSaxHandler, self).start_parent_tag_file()

    def start_parent_tag_token(self):
        self.push_tag(self.__tag)
        # token -> sub token
        if self.__tag == self.tag_subtoken:
            if self.__name != self.current_token:
                raise XmlError("Token '%s' used in wrong token group '%s'" % (self.__name, self.current_token))

            self.cls.tokens[self.current_token][self.__attrs['token']] = self.__attrs['string']
        else:
            raise XmlError("Unrecognised tag '%s' in token group '%s' declaration" % (self.__name, self.current_token))

    def start_parent_tag_struct(self):
        self.push_tag(self.__tag)
        # struct -> attribute
        if self.__tag == self.tag_attribute:
            name = self.__attrs['name']
            if self.class_name in self.completed_struct_additions:
                if name in self.completed_struct_additions[self.class_name]:
                    base_class = list(filter(lambda x: x.displayname == name, reversed(self.class_dict['_attrs'])))[0]
                    if isinstance(base_class.type_, str):
                        if self.__attrs['type'] != base_class.type_:
                            raise XmlError("Duplicate Struct attribute found '%s' in '%s' with differing types" % (name, self.class_name))
                        else:
                            # TODO: Add special MultiStructAttribute
                            pass
                else:
                    self.completed_struct_additions[self.class_name].append(name)
            else:
                self.completed_struct_additions[self.class_name] = [name]
            # add attribute to class dictionary
            self.class_dict["_attrs"].append(StructAttribute(self.cls, self.__attrs))
        else:
            raise XmlError("Only add tags allowed in struct declaration")

    def end_tag_token(self):
        # Reset variable
        # self.current_token = None
        pass

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
