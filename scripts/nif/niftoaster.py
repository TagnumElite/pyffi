#!/usr/bin/python

"""A script for casting spells on nif files. This script is essentially
a nif specific wrapper around L{pyffi.spells.Toaster}."""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, NIF File Format Library and Tools.
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
#    * Neither the name of the NIF File Format Library and Tools
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
# --------------------------------------------------------------------------

import logging
import sys

from pyffi.formats.NIF import NifFormat
import pyffi.spells.check
import pyffi.spells.nif
import pyffi.spells.nif.check
import pyffi.spells.nif.dump
import pyffi.spells.nif.fix
import pyffi.spells.nif.optimize

class NifToaster(pyffi.spells.nif.NifToaster):
    """Class for toasting nif files, using any of the available spells."""
    SPELLS = [
        pyffi.spells.check.SpellRead,
        pyffi.spells.nif.check.SpellReadWrite,
        pyffi.spells.nif.check.SpellNodeNamesByFlag,
        pyffi.spells.nif.check.SpellCompareSkinData,
        pyffi.spells.nif.check.SpellCheckBhkBodyCenter,
        pyffi.spells.nif.check.SpellCheckCenterRadius,
        pyffi.spells.nif.check.SpellCheckConvexVerticesShape,
        pyffi.spells.nif.check.SpellCheckMopp,
        pyffi.spells.nif.check.SpellCheckSkinCenterRadius,
        pyffi.spells.nif.check.SpellCheckTangentSpace,
        pyffi.spells.nif.check.SpellCheckTriStrip,
        pyffi.spells.nif.check.SpellCheckVersion,
        pyffi.spells.nif.dump.SpellDumpAll,
        pyffi.spells.nif.dump.SpellDumpTex,
        pyffi.spells.nif.dump.SpellHtmlReport,
        pyffi.spells.nif.dump.SpellExportPixelData,
        pyffi.spells.nif.fix.SpellAddTangentSpace,
        pyffi.spells.nif.fix.SpellClampMaterialAlpha,
        pyffi.spells.nif.fix.SpellDelTangentSpace,
        pyffi.spells.nif.fix.SpellDetachHavokTriStripsData,
        pyffi.spells.nif.fix.SpellDisableParallax,
        pyffi.spells.nif.fix.SpellFFVT3RSkinPartition,
        pyffi.spells.nif.fix.SpellFixCenterRadius,
        pyffi.spells.nif.fix.SpellFixSkinCenterRadius,
        pyffi.spells.nif.fix.SpellFixMopp,
        pyffi.spells.nif.fix.SpellFixTexturePath,
        pyffi.spells.nif.fix.SpellMergeSkeletonRoots,
        pyffi.spells.nif.fix.SpellSendGeometriesToBindPosition,
        pyffi.spells.nif.fix.SpellSendDetachedGeometriesToNodePosition,
        pyffi.spells.nif.fix.SpellSendBonesToBindPosition,
        pyffi.spells.nif.fix.SpellScale,
        pyffi.spells.nif.fix.SpellStrip,
        pyffi.spells.nif.optimize.SpellCleanRefLists,
        pyffi.spells.nif.optimize.SpellMergeDuplicates,
        pyffi.spells.nif.optimize.SpellOptimizeGeometry,
        #pyffi.spells.nif.optimize.SpellOptimizeSplit,
        pyffi.spells.nif.optimize.SpellOptimize]
    ALIASDICT = {
        "texdump": "dump_tex",
        "read": "check_read",
        "readwrite": "check_readwrite",
        "ffvt3rskinpartition": "fix_ffvt3rskinpartition",
        "disableparallax": "fix_disableparallax",
        "exportpixeldata": "dump_pixeldata",
        "scale": "fix_scale"}
    EXAMPLES = """* check if PyFFI can read all files in current directory
  (python version of nifskope's xml checker):

    python niftoaster.py check_read .

* optimize all nif files a directory tree, recursively

    python niftoaster.py optimize /path/to/your/nifs/

* print texture information of all nif files a directory tree, recursively

    python niftoaster.py dump_tex /path/to/your/nifs/

* update/generate mopps of all nif files a directory tree, recursively

    python niftoaster.py fix_mopp /path/to/your/nifs/

* update/generate skin partitions of all nif files a directory tree,
recursively, for Freedom Force vs. The 3rd Reich

    python niftoaster.py fix_ffvt3rskinpartition /path/to/your/nifs/

* run the profiler on PyFFI while reading nif files:

    python -m cProfile -s cumulative -o profile_read.txt niftoaster.py check_read .

* find out time spent on a particular test:

    python -m cProfile -s cumulative niftoaster.py check_tristrip

* scale all files in c:\\zoo2 by a factor 100 - useful to
  visualize nif files from games such as Zoo Tycoon 2 that are otherwise too
  small to show up properly in nifskope:

    python niftoaster.py -a 100 fix_scale "c:\\zoo2"
"""

# if script is called...
if __name__ == "__main__":
    # set up logger
    logger = logging.getLogger("pyffi")
    logger.setLevel(logging.DEBUG)
    loghandler = logging.StreamHandler(sys.stdout)
    loghandler.setLevel(logging.DEBUG)
    logformatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
    loghandler.setFormatter(logformatter)
    logger.addHandler(loghandler)
    # call toaster
    NifToaster().cli()

