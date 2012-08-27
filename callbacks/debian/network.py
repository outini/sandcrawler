"""
Specifics networks callbacks for Debian
"""
network_config = "/etc/network/interfaces"

def get_iface(iface):
    """ get network iface configuration """
    print "netconfig for debian !!"
    return True, None

def get_routes(tables=""):
    """ get network routes """
    return True, None
