"""
Specifics system callbacks for Debian
"""

# we import as private
import fabric_wrp as __fapi

initd_path = "/etc/init.d"

def start_service(self, service):
    """ service simple starter """
    #return __fapi.sudo(self.srv_ip, "%s/%s start" % (sys_initd_path, service))
    print "%s: %s/%s start" % (self.srv_ip, initd_path, service)
