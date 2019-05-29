import doctest
import logging
import sys
import unittest

import pyffi
import pyffi.types.common
import pyffi.engines
import pyffi.engines.xml
import pyffi.engines.mex
import pyffi.types.any
import pyffi.types.simple
import pyffi.types.array
import pyffi.types.binary
import pyffi.types.basic
import pyffi.engines.xml.bit_struct
import pyffi.engines.xml.enum
import pyffi.engines.xml.expression
import pyffi.engines.xml.struct_
import pyffi.utils
import pyffi.utils.tristrip
import pyffi.utils.vertex_cache
import pyffi.utils.mathutils
import pyffi.utils.quickhull
import pyffi.utils.inertia
import pyffi.utils.tangentspace
import pyffi.utils.mopp
# import pyffi.formats.nif
"""
import pyffi.formats.cgf
import pyffi.formats.kfm
import pyffi.formats.dds
import pyffi.formats.tga
import pyffi.formats.egm
import pyffi.formats.esp
import pyffi.formats.tri
import pyffi.formats.bsa
import pyffi.formats.egt
import pyffi.formats.psk
import pyffi.formats.rockstar.dir_
import pyffi.spells
# import pyffi.spells.nif
# import pyffi.spells.nif.fix
# import pyffi.spells.nif.modify
# import pyffi.spells.nif.check
# import pyffi.spells.nif.dump"""

# these two do not yet work on py3k
from tests import test_logger

if sys.version_info[0] < 3:
    import pyffi.engines.xsd
    import pyffi.formats.dae


# set up logger

# this is a hack for StreamHandler to make it work with doctest
# see http://mail.python.org/pipermail/python-list/2007-January/423842.html
class WrapStdOut(object):
    def __getattr__(self, name):
        return getattr(sys.stdout, name)


logger = logging.getLogger("pyffi")
logger.setLevel(logging.INFO)  # skip debug messages
loghandler = logging.StreamHandler(WrapStdOut())
loghandler.setLevel(logging.DEBUG)
logformatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
loghandler.setFormatter(logformatter)
logger.addHandler(loghandler)


def create_suite():
    # force number of jobs to be 1 (multithreading makes doctesting difficult)
    pyffi.spells.Toaster.DEFAULT_OPTIONS["jobs"] = 1

    mods = [val for (key, val) in sys.modules.items()
            if key.startswith('pyffi')]

    suite = unittest.TestSuite()

    test_logger.info("Executing doctests")
    for mod in mods:
        try:
            suite.addTest(doctest.DocTestSuite(mod))
        except ValueError:  # no tests
            test_logger.debug(str(mod) + "does not have a test suite")
            pass

    file_paths = {'formats/cgf/cgftoaster.txt',
                  'spells/nif/dump_tex.txt',
                  'spells/nif/ffvt3rskin.txt',
                  'spells/nif/fix_clampmaterialalpha.txt',
                  'spells/nif/fix_cleanstringpalette.txt',
                  'spells/nif/fix_detachhavoktristripsdata.txt',
                  'spells/nif/fix_tangentspace.txt',
                  'spells/nif/fix_tangentspace_series_parallel.txt',
                  'spells/nif/fix_texturepath.txt',
                  'spells/nif/modify_allbonepriorities.txt',
                  'spells/nif/modify_delbranches.txt',
                  'spells/nif/modify_delvertexcolor.txt',
                  'spells/nif/modify_substitutestringpalette.txt',
                  'spells/nif/opt_delunusedbones.txt',
                  'spells/nif/opt_delzeroscale.txt',
                  'spells/nif/opt_vertex_cache.txt',

                  # Contain outstanding issues
                  # 'spells/egm/optimize.txt',
                  # 'formats/kfm/kfmtoaster.txt', #Not Implemented
                  # various regression tests (outside documentation)
                  # 'docs-sphinx/intro.rst', #outside of test dir...
                  }

    suite.addTest(doctest.DocFileSuite(*file_paths))

    # for path in file_paths:
    #     test_logger.debug("Adding File to Suite: `%s`", path)
    #     suite.addTest(doctest.DocFileSuite(path))

    # TODO: examples
    # suite.addTest(doctest.DocFileSuite('examples/*.txt'))

    return unittest.TextTestRunner().run(suite).wasSuccessful()


def test():
    test_logger.info("Executing Suite - ")
    # run tests
    return create_suite()


if __name__ == '__main__':
    create_suite()
