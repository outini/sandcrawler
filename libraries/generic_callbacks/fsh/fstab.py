"""
fstab callbacks for filesystem hierarchy
"""

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
