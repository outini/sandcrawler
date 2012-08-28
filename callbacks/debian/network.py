# -*- coding: iso-latin-1 -*-
"""
Specifics networks callbacks for Debian
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

import sc_common as __scc
import fabric_wrp as __fapi

network_config = "/etc/network/interfaces"
nbs_aliases_cfg = "/etc/nbs/network/aliases.cfg"

def check_iface(self, iface):
    """ check network iface presence """
    out = __fapi.sudo(self.srv_ip,
                      "ifconfig %s" % (iface), nocheck = True)
    if out.return_code != 0:
        return False
    return True

def get_iface(self, iface):
    """ get network iface configuration """
    if not check_iface(iface):
        return (False, None)

    iface = __scc.AttStr("network interface %s" % (iface))
    return (True, iface)

def get_routes(tables = ""):
    """ get network routes """
    return (True, None)
