""""""

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

# noinspection PyCompatibility
from dataclasses import dataclass, field
from typing import List


@dataclass
class Version(object):
    """Version object for each version"""

    id: str = field(compare=False)
    num: str
    supported: bool = field(default=False, compare=False)
    user: List[str] = field(default_factory=list)
    bsver: List[str] = field(default_factory=list)
    custom: bool = field(default=False, compare=False)
    ext: List[str] = field(default_factory=list, compare=False)
    games: List[str] = field(default_factory=list, compare=False, init=False)

    def add_game(self, game: str):
        self.games.append(game)

    @property
    def version(self) -> int:
        """Converts version string into an integer.
        :return: 
        :rtype: int
        """

        # 3.03 case is special
        if self.num == '3.03':
            return 0x03000300

        # NS (neosteam) case is special
        if self.num == 'NS':
            return 0x0A010000

        try:
            ver_list = [int(x) for x in self.num.split('.')]
        except ValueError:
            return -1  # version not supported (i.e. version_str '10.0.1.3a' would trigger this)

        if len(ver_list) > 4 or len(ver_list) < 1:
            return -1  # version not supported

        for ver_digit in ver_list:
            if (ver_digit | 0xff) > 0xff:
                return -1  # version not supported

        while len(ver_list) < 4:
            ver_list.append(0)

        return (ver_list[0] << 24) + (ver_list[1] << 16) + (ver_list[2] << 8) + ver_list[3]
