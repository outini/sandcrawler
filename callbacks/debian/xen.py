# -*- coding: iso-latin-1 -*-
"""
Specifics xen callbacks for Debian
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

confpath_xen = "/etc/xen"
libpath_xenapi = "/usr/lib/xen-default/lib/python"

def get_ip_domuconfig(self, domu_config):
    """ extract domu IP from domU configuration """
    # get vifs configuration
    if domu_config.has_key('vif'):
        ip_entries = domu_config['vif']
    else: ip_entries = list()
    for ip_entry in ip_entries:
        ip_infos = ip_entry.split(',')
        # looking for ip= field
        ipaddrs = [ field.split("=")[1] for field in ip_infos
                    if field[0:3] == "ip=" ]

        # return the first 10.1.* IP
        for ipaddr in ipaddrs:
            first_bytes = ipaddr.split('.')[0:2]
            if first_bytes != ['10','20'] and first_bytes != ['10','21']:
                return ipaddr

    return None
