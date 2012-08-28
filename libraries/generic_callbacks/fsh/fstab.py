# -*- coding: iso-latin-1 -*-
"""
fstab callbacks for filesystem hierarchy
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

# we import as private,
# only public functions and attributes are set as callback methods
import sc_logs as __LOG
import fabric_wrp as __fapi
import sc_config as __config
import sc_common as __scc


def load(self):
    print "load OK: %s" % (self)

def write(self):
    print "write OK"
