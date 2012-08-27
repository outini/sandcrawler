"""
Specifics system callbacks for Debian
"""

# we import as private
import fabric_wrp as __fapi

initd_path = "generic"

def start_service(self, service):
    """ service simple starter """
    #return __fapi.sudo(self.srv_ip, "%s/%s start" % (sys_initd_path, service))
    print "%s: %s/%s start" % (self.srv_ip, initd_path, service)

def sysuser_exists(self, username):
    """ check if sysuser exists """
    return __fapi.file_contains(self.srv_ip,
                                "^" + username + ":",
                                "/etc/passwd")

def set_sysuser_passwd(self, user, passwd):
    """ set sysuser password """
    chpasswd = "echo '" + user + ":" + passwd + "' | chpasswd -m"
    return __fapi.sudo(self.srv_ip, chpasswd)

# def addSysGroup(self, group):
#     if not fabric.contrib.files.contains("^" + group + ":", "/etc/group"):
#         err = fabric.api.sudo("addgroup " + group + " 2>&1" ,pty=True)
#         if err.return_code != 0 : return False
#     return True

# def addSysUser2SysGroup(self, user, group):
#     if not fabric.contrib.files.contains("^" + group + ":.*:(.*,)?" + user + "(,.*)?$", "/etc/group"):
#         err = fabric.api.sudo("adduser " + user + " " + group + " 2>&1" ,pty=True)
#         if err.return_code != 0 : return False
#     return True
