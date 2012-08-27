#! /usr/bin/env python
# -*- coding: iso-latin-1 -*-
"""
xen functions for sandcrawler
"""

# If you're using python 2.5
from __future__ import with_statement

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "beerware"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

import sys
import re
import sc_systems
import sc_common as scc
import fabric_wrp as fapi
import sc_pythongen

## we store current dom0 for use between modules
DOM0_LIST = {}
CURRENT_DOM0 = None

class XenRaw(sc_systems.Server):
    """ raw data fetcher """
    def __init__(self, srv_ip):
        sc_systems.Server.__init__(self, srv_ip)
        self.load_callbacks("xen")

        self.xmlist_py_template = [
            'import sys',
            'sys.path.insert(1,"%s")' % (self.xen.libpath_xenapi),
            'from xen.xm import main',
            'server = main.ServerProxy(main.serverURI)']

        return None

    def xminfo_raw(self):
        """ raw xm info """
        cmd_xminfo = "xm info"
        cmd_xminfo_c = "%s -c" % (cmd_xminfo)
        cmd = "%s && %s" % (cmd_xminfo, cmd_xminfo_c)
        return fapi.sudo(self.srv_ip, cmd)

    def __xmlist_raw(self, xmlist_cmd):
        """ raw xm list """
        xmlist_py = list(self.xmlist_py_template)
        xmlist_py.append(xmlist_cmd)
        cmd = "python -c '%s'" % ("\n".join(xmlist_py))
        return fapi.sudo(self.srv_ip, cmd)

    def xmlist_bydomu_raw(self, domu_name):
        """ raw by domu xm list """
        list_bydomu = 'print server.xend.domain("%s", 1)'
        return self.__xmlist_raw(list_bydomu % (domu_name))

    def xmlist_bytype_raw(self, state="all"):
        """ raw by type xm list """
        list_bytype = 'print server.xend.domains_with_state(True,"%s", 1)'
        return self.__xmlist_raw(list_bytype % (state))

    def xm_exec(self, xm_opts):
        """ Wrapper to run xm commands """
        return fapi.sudo(self.srv_ip, "xm %s" % (xm_opts))


class Dom0(sc_systems.Server):
    """ dom0 server class """
    def __init__(self, dom0_ip, dom0="", load=True):
        sc_systems.Server.__init__(self, dom0_ip)
        self.load_callbacks("xen")

        self.dom0 = dom0
        self.dom0_ip = dom0_ip
        self.xenapi = XenRaw(dom0_ip)
        self.infos = scc.AttStr("dom0 structure")
        self.infos.domain0 = scc.AttStr("domain0 structure")
        self.infos.domus = {}

        if load:
            self.load_xminfo()
            self.load_domain0()
            self.list_domus_configs(load=True)
            self.infos.running_domus = self.list_running_domus()
        return None

    def load_xminfo(self):
        """ xm info output to python struct """
        err = self.xenapi.xminfo_raw()
        raw_lines = err.lines

        xminfo_entries = []
        for line in raw_lines:
            s_line = re.split("\s+:\s+", line.strip(), maxsplit=1)
            if len(s_line) >= 2:
                xminfo_entries.append(s_line)
            else: xminfo_entries[-1].extend(s_line)

        scc.list2struct(self.infos,
                        xminfo_entries)
        
        return self.infos

    def load_domain0(self):
        """ load domain-0 running state """
        domustate_list = self.xenapi.xmlist_bydomu_raw('Domain-0')
        domustate_dict = scc.list2dict(eval(domustate_list))['domain']
        scc.dict2struct(self.infos.domain0, domustate_dict)
        return True

    def list_running_domus(self):
        """ running domus listing """
        running_domus = []
        out = self.xenapi.xmlist_bytype_raw()
        for domu in eval(out):
            domu_dict = scc.list2dict(domu)['domain']
            running_domus.append(domu_dict['name'])
        return running_domus

    def list_domus_configs(self, load=False):
        """ domU configuration listing """
        configs = fapi.list_files(self.dom0_ip,
                                  "%s/*.cfg" % (self.xen.confpath_xen),
                                  full=False)
        hosts = []
        for config in configs:
            domu_name = config.split('.')[0]
            hosts.append(domu_name)
            if load:
                domu_struct = DomU(domu_name,
                                   self.dom0,
                                   self.dom0_ip,
                                   load=True)
                self.infos.domus.update({domu_name: domu_struct})
            
        return hosts

class DomU(sc_systems.Server):
    """ domU class """
    def __init__(self, name, dom0, dom0_ip, load=True):
        sc_systems.Server.__init__(self, dom0_ip)
        self.load_callbacks("xen")

        self.name = name
        self.dom0 = dom0
        self.dom0_ip = dom0_ip
        self.xenapi = XenRaw(dom0_ip)
        self.auto = False
        self.running = False
        self.config = scc.AttStr("config structure")

        self.configfile = "%s/%s.cfg" % (
            self.xen.confpath_xen, self.name)
        self.configfile_auto = "%s/auto/%s.cfg" % (
            self.xen.confpath_xen, self.name)

        if load:
            self.load_config()
            self.load_state()

        return None

    def load_state(self):
        """ import domU running state """
        domustate_list = self.xenapi.xmlist_bydomu_raw(self.name)
        domustate_dict = scc.list2dict(eval(domustate_list))['domain']
        scc.dict2struct(self, domustate_dict)
        return True

    def load_config(self):
        """ import domU configuration to config struct """

        if fapi.file_exists(self.dom0_ip,
                            self.configfile_auto):
            self.auto = True
        else: self.auto = False

        config = fapi.get_file_content(self.dom0_ip,
                                       self.configfile)
        if config == None:
            return False

        config_dict = {}
        unused = {}
        exec "\n".join(config.lines_clean) in unused, config_dict
        self.config = scc.dict2struct(scc.AttStr("config structure"),
                                      config_dict)

        return True

    def set_config_attr(self, attr, value):
        """ Set domU configuration attribute """
        setattr(self.config, attr, value)
        return True

    def write_config(self):
        """ write configuration on dom0 """
        pygen = sc_pythongen.PythonGenerator()

        file_content = ""
        for attr, value in self.config.__dict__.iteritems():
            file_content = "%s%s" % (file_content,
                                     pygen.dump_(attr, value))

        filename = self.configfile
        fapi.write_file(self.dom0_ip,
                        filename, file_content,
                        use_sudo=True)
        return True

    def start(self):
        """ start domU via xm commands """
        return self.xenapi.xm_exec('create %s' % (self.configfile))

    def destroy(self):
        """ destroy domU via xm commands """
        return self.xenapi.xm_exec('destroy %s' % (self.name))
        

def store_dom0(dom0_obj):
    """ dom0 classes storage """
    dom0_ip = dom0_obj.dom0_ip
    DOM0_LIST.update({dom0_ip: dom0_obj})
    return True

def get_dom0(dom0_ip="", dom0=""):
    """ get current dom0 instance or create it """
    global CURRENT_DOM0
    if CURRENT_DOM0 == None:
        if dom0_ip == "":
            return False, None
        else:
            CURRENT_DOM0 = Dom0(dom0_ip, dom0)
            store_dom0(CURRENT_DOM0)
            return True, CURRENT_DOM0
    else:
        if dom0_ip != CURRENT_DOM0.dom0_ip:
            if DOM0_LIST.has_key(dom0_ip):
                CURRENT_DOM0 = DOM0_LIST[dom0_ip]
            else:
                CURRENT_DOM0 = Dom0(dom0_ip, dom0)
                store_dom0(CURRENT_DOM0)
        return True, CURRENT_DOM0
