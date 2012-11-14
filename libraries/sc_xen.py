# -*- coding: iso-latin-1 -*-
"""
xen functions for sandcrawler

This librarie need a specific callback named xen
This callback will be callable via self.xen

It must contains at least the following function and attribute:

  confpath_xen = "/path/to/xen/configuration"
  libpath_xenapi = "/path/to/xen/api/libs"

  def get_ip_domuconfig(self, dict(domu_config)):
      # received dict is a standard xen domU config converted in dict
      return str(ipaddress)
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

import re
import sc_systems
import sc_common as scc
import fabric_wrp as fapi
import sc_pythongen as pygen
import sc_logs as log

## we store current dom0 for use between modules
DOM0_LIST = dict()
CURRENT_DOM0 = None

class XenRaw:
    """ raw data fetcher """
   def __init__(self, dom0_instance):
        self.dom0_instance = dom0_instance
        self.xmlist_py_template = [
            'import sys',
            'sys.path.insert(1,"%s")' % (
                self.dom0_instance.xen.libpath_xenapi),
            'from xen.xm import main',
            'server = main.ServerProxy(main.serverURI)',
            'except: print "[]"']

        return None

    def xminfo_raw(self):
        """ raw xm info """
        cmd_xminfo = "xm info"
        cmd_xminfo_c = "%s -c" % (cmd_xminfo)
        cmd = "%s && %s" % (cmd_xminfo, cmd_xminfo_c)
        return self.dom0_instance.fapi.sudo(cmd)

    def __xmlist_raw(self, xmlist_cmd):
        """ raw xm list """
        xmlist_py = list(self.xmlist_py_template)
        xmlist_py.insert(-1, "try: %s" % (xmlist_cmd))
        cmd = "python -c '%s'" % ("\n".join(xmlist_py))
        return self.dom0_instance.fapi.sudo(cmd)

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
        return self.dom0_instance.fapi.sudo("xm %s" % (xm_opts))


class Dom0(sc_systems.Server):
    """ dom0 server class """
    def __init__(self, dom0_ip, name="", load=True):
        sc_systems.Server.__init__(self, dom0_ip)

        log.log_i("initialising new Dom0(%s, %s)" % (dom0_ip, name))

        ## using xen callbacks definitions
        self.xen = None
        self.load_callbacks("xen")
        self.load_callbacks("fsh")

        self.name = name
        self.xenapi = XenRaw(self)
        self.infos = scc.AttStr("dom0 structure")
        self.infos.used_cpus = None
        self.infos.free_cpus = None
        self.infos.domain0 = scc.AttStr("domain0 structure")
        self.infos.domus = dict()

        if load:
            self.load_xminfo()
            self.load_domain0()
            self.load_all_domus(self.list_all_domus())

        return None

    def load_xminfo(self):
        """ xm info output to python struct """
        log.log_d("%s: loading xminfos" % (self.srv_ip))

        err = self.xenapi.xminfo_raw()
        raw_lines = err.lines

        xminfo_entries = []
        for line in raw_lines:
            s_line = re.split("\s+:\s+", line.strip(), maxsplit=1)
            if len(s_line) >= 2:
                xminfo_entries.append(s_line)
            else: xminfo_entries[-1].extend(s_line)

        #log.log_d('xminfo_entries: %s' % (xminfo_entries))
        scc.list2struct(self.infos,
                        xminfo_entries)

        return self.infos

    def load_domain0(self):
        """ load domain-0 running state """
        log.log_d("%s: loading domain0 infos" % (self.srv_ip))

        domustate_list = self.xenapi.xmlist_bydomu_raw('Domain-0')

        domustate_dict = scc.list2dict(eval(domustate_list))['domain']
        scc.dict2struct(self.infos.domain0, domustate_dict)
        return True

    def list_all_domus(self):
        """ list all domus """
        r_domus = self.list_running_domus()
        c_domus = self.list_domus_configs()
        all_domus = list(set(r_domus + c_domus))

        return all_domus

    def list_running_domus(self):
        """ running domus listing """
        log.log_d("%s: listing running domUs" % (self.srv_ip))

        running_domus = []
        self.infos.used_cpus = 0
        # retrieve xm list output and convert each domU in dict
        out = self.xenapi.xmlist_bytype_raw()
        for domu in eval(out):
            domu_dict = scc.list2dict(domu)['domain']
            if domu_dict['name'] != "Domain-0":
                running_domus.append(domu_dict['name'])
                self.infos.used_cpus += int(domu_dict['vcpus'])

        # return list of domU dicts
        if hasattr(self.infos, 'nr_cpus'):
            self.infos.free_cpus = (
                int(self.infos.nr_cpus) - self.infos.used_cpus
                )

        return running_domus

    def list_domus_configs(self):
        """ domU configuration listing """
        log.log_d("%s: listing domUs configuration" % (self.srv_ip))

        # list filename *.cfg in xen config path
        configs = self.fsh.list_files(self.srv_ip,
                                  "%s/*.cfg" % (self.xen.confpath_xen),
                                  full=False)

        # return files list without extensions
        return [ ".".join(config.split('.')[0:-1]) for config in configs ]

    def new_domu(self, domu_name, load=False, srv_ip=None):
        """ create new domu """
        # create empty domu forked from dom0 specs
        # domu systemtype is not known at this point
        if srv_ip == None:
            srv_ip = self.srv_ip

        domu_struct = DomU(domu_name,
                           srv_ip,
                           self,
                           load=load,
                           systemtype=self.systemtype)

        # store domu
        self.infos.domus.update({domu_name: domu_struct})

        return True

    def load_all_domus(self, domus):
        """ create and load all found domus """
        log.log_d("%s: loading all hosted domUs infos" % (self.srv_ip))

        for domu in domus:
            self.new_domu(domu, load=True)

        return True

class DomU(sc_systems.Server):
    """ domU class """
    def __init__(self, name, ipaddr, dom0, load=True, systemtype=None):
        sc_systems.Server.__init__(self, ipaddr,
                                   load=load, systemtype=systemtype)

        log.log_i("initialising new DomU(%s, %s, %s)" % (name,
                                                         ipaddr, systemtype))

        self.name = name
        self.dom0 = dom0
        self.state = None
        self.config = None

        if load:
            self.load_config()
            self.load_state()

        return None

    def init_domu(self):
        """ init system type and reload callbacks """
        self.guess_system()
        return True

    def load_state(self):
        """ import domU running state """
        log.log_d("%s: loading domU running state" % (self.srv_ip))

        domustate_list = self.dom0.xenapi.xmlist_bydomu_raw(self.name)
        e_domustate_list = eval(domustate_list)
        if len(e_domustate_list):
            domustate_dict = scc.list2dict(e_domustate_list)['domain']
            self.state = scc.dict2struct(scc.AttStr("state structure"),
                                         domustate_dict)
        return True

    def load_config(self, config_content=list(), reinit=False):
        """ import domU configuration to config struct """
        log.log_d("%s: loading domU configuration" % (self.srv_ip))

        configfile = "%s/%s.cfg" % (self.dom0.xen.confpath_xen, self.name)

        if not len(config_content):
            config = self.fsh.get_file_content(configfile)
            if config == None:
                return False
            config = config.lines
        else: config = config_content

        clean_config = list()
        # cleaning config but formating is kept
        for line in config:
            clean_line = re.sub(r"#.*", r"", line)
            clean_line = re.sub(r"^\s+$", r"", clean_line)
            if len(clean_line):
                clean_config.extend([clean_line])

        # exec python domU configfile in a dict context
        plaintext_config = "\n".join(clean_config)
        config_dict = dict()
        unused = dict()
        exec plaintext_config in unused, config_dict

        # convert config dict in config structure
        self.config = scc.dict2struct(scc.AttStr("config structure"),
                                      config_dict)

        # check if domu is auto started
        configfile_auto = "%s/auto/%s.cfg" % (self.dom0.xen.confpath_xen,
                                              self.name)
        if self.fsh.file_exists(configfile_auto):
            self.config.auto = True
        else: self.config.auto = False

        # store domu configuration filename
        self.config.configfile = configfile

        # reinit parent with IP and reload callbacks if asked
        domu_ip = self.dom0.xen.get_ip_domuconfig(config_dict)
        self.srv_ip = domu_ip
        if reinit:
            self.init_domu()

        return True

    def set_config_attr(self, attr, value):
        """ Set domU configuration attribute """
        setattr(self.config, attr, value)
        return True

    def write_config(self):
        """ write configuration on dom0 """
        file_content = ""
        attrs = self.config.__dict__
        for attr in sorted(attrs):
            ## auto and configfile attributes are not part of xen
            if attr == "auto" or attr == "configfile":
                continue

            ## format content with python syntax
            file_content = "%s%s" % (file_content,
                                     pygen.dump_(attr, attrs[attr]))

        # write configuration on dom0
        filename = self.config.configfile
        self.fsh.write_file(filename, file_content, use_sudo=True)
        return True

    def start(self):
        """ start domU via xm commands """
        # do xm create on dom0
        xm_create = self.dom0.xenapi.xm_exec(
            'create %s' % (self.config.configfile))
        if xm_create.return_code != 0:
            return False

        # wait for host to start and return result
        return scc.wait_host(self.srv_ip, "UP", 15)

    def stop(self):
        """ stop domU using system callbacks """
        # be sure not to stop the dom0 if domU network config not loaded
        if self.srv_ip == self.dom0.srv_ip:
            return False

        # shutdown domU and return status change
        self.fapi.sudo("shutdown -h now")
        return scc.wait_host(self.srv_ip, "DOWN", 10)

    def destroy(self):
        """ destroy domU via xm commands """
        xm_destroy = self.dom0.xenapi.xm_exec('destroy %s' % (self.name))
        if xm_destroy.return_code != 0:
            return False
        return True


def store_dom0(dom0_obj):
    """ dom0 classes storage """
    dom0_ip = dom0_obj.srv_ip
    DOM0_LIST.update({dom0_ip: dom0_obj})
    return True

def get_dom0(dom0_ip="", dom0="", load=True):
    """ get current dom0 instance or create it """
    global CURRENT_DOM0
    if CURRENT_DOM0 == None:
        if dom0_ip == "":
            return False, None
        else:
            CURRENT_DOM0 = Dom0(dom0_ip, dom0, load=load)
            store_dom0(CURRENT_DOM0)
            return True, CURRENT_DOM0
    else:
        if dom0_ip != CURRENT_DOM0.srv_ip:
            if DOM0_LIST.has_key(dom0_ip):
                CURRENT_DOM0 = DOM0_LIST[dom0_ip]
            else:
                CURRENT_DOM0 = Dom0(dom0_ip, dom0, load=load)
                store_dom0(CURRENT_DOM0)
        return True, CURRENT_DOM0
