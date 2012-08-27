#! /usr/bin/env python
# -*- coding: iso-latin-1 -*-
"""
systems specifics for sandcrawler
"""

# If you're using python 2.5
from __future__ import with_statement

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

import sc_logs as __LOG
import fabric_wrp as __fapi


def check_prerequisites(srv_ip):
    """ check prerequisites on remote host """
    ret = True

    __LOG.log_d("trying to run command")
    out = __fapi.run(srv_ip, 'whoami', nocheck=True)
    if out.failed:
        __LOG.log_c("unable to execute commands on remote host")
        ret = False

    __LOG.log_d("trying to run sudo command")
    out = __fapi.sudo(srv_ip, 'whoami', nocheck=True)
    if out.failed:
        __LOG.log_c("unable to execute commands with sudo on remote host")
        ret = False

    return ret

def sysguess(ipaddr):
    """ guess on system of remote target """
    out = __fapi.run(ipaddr, 'uname -s')
    if out.failed:
        raise RuntimeError('unable to guess system on %s' % (ipaddr))

    if out == "Linux":
        out = __fapi.run(ipaddr, 'cat /etc/issue')
        system = out.split()[0].lower()
    else: system = out.lower()

    hostname = __fapi.run(ipaddr, "hostname")

    return hostname, system
