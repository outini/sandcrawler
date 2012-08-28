# -*- coding: iso-latin-1 -*-
"""
systems specifics for sandcrawler
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

import sys
import types
import collections
import sc_logs as LOG
import sc_common as scc
import fabric_wrp as fapi

class CallBacks():
    """ class to store callbacks """
    def __init__(self, trunk, parent, module):
        LOG.log_d("initialising Callbacks class %s" % (module))
        self.trk = trunk
        self.mom = parent
        modlist = list()

        # replace OS type by generic prefix in module name
        # "debian.system" become "generic_callbacks.system"
        clean_mod = ".".join(module.split('.')[1:])
        generic_module = "generic_callbacks.%s" % (clean_mod)
        LOG.log_d("generic module is %s" % (generic_module))

        # add users' callbacks prefix
        target_module = "callbacks.%s" % (module)

        generic_imported = self.try_import(generic_module)
        if generic_imported is not None:
            LOG.log_d("generic module successfully imported")
            modlist.extend([generic_imported])

        specific_imported = self.try_import(target_module)
        if specific_imported is not None:
            LOG.log_d("user's module successfully imported")
            modlist.extend([specific_imported])

        if not len(modlist):
            raise ImportError("unable to import required callbacks: %s" % (
                    module))

        LOG.log_d("importing methods and attributes from each module")
        self.retriev_attrs_and_methods(modlist)

    @staticmethod
    def try_import(module):
        """ try to import module """
        # add generic_callbacks methods and attributes if found
        try:
            __import__(module)
            return sys.modules[module]
        except ImportError:
            LOG.log_d("module '%s' not found" % (module))
            return None

    def retriev_attrs_and_methods(self, modules_list):
        """ retrieve attributes and methods from each module """
        for mod in modules_list:
            LOG.log_d("importing from %s" % (mod.__name__))
            for attr in dir(mod):
                # import everything but builtins and privates
                if attr[0:2] == "__":
                    continue

                module_attr = getattr(mod, attr)
                ## store callback, if callable self refer to the callback
                if isinstance(module_attr, collections.Callable):
                    setattr(self, attr,
                            types.MethodType(module_attr, self))
                else:
                    setattr(self, attr, module_attr)

        return True

def fapi_wrapper(method_name):
    """ trying metaclass """
    def _method(self, *argl, **argd):
        # adding self.srv_ip as first argument for every fapi invocations
        # all the fabric_wrp methods MUST take the ip as first argument
        argl = list(argl)
        argl.insert(0, self.srv_ip)
        argl = tuple(argl)
        return getattr(fapi, '%s' % method_name)(*argl,**argd)
    return _method

class Server:
    """ server class with os/distribs callbacks """
    def __init__(self, srv_ip, load=True, systemtype=None):
        LOG.log_d("initialising Server(%s, %s, %s)" % (srv_ip, load,
                                                       systemtype))
        self.srv_ip = srv_ip
        self.hostname = None
        self.systemtype = systemtype

        self.fapi = scc.AttStr('fapi calls wrapper')
        self.load_fapi()

        if load:
            LOG.log_d("guessing server's system type")
            self.guess_system(systemtype)


    def is_up(self, port = 22):
        """ check if host is UP """
        return scc.is_host_up(self.srv_ip, int(port))


    def __getparent(self, callback_name):
        """ get parent from callback name """
        splitted = callback_name.split('.')
        if len(splitted) == 1:
            return None

        parent = self
        for member in splitted[:-1]:
            if not hasattr(parent, member):
                parent.load_callbacks(member)
            parent = getattr(parent, member)

        return parent


    def load_callbacks(self, callback):
        """ callbacks loader """
        if self.systemtype == None and not self.guess_system():
            return False

        # load callback specified by arg, split by dot and recurse load
        callback_name = callback.split('.')[-1]
        parent = self.__getparent(callback)
        if parent is None or not hasattr(parent, 'trk'):
            trunk = parent = self
        else:
            trunk = parent.trk

        target_module = "%s.%s" % (self.systemtype, callback)
        setattr(parent, callback_name, CallBacks(trunk, parent,
                                                 target_module))

        return True


    def load_fapi(self):
        """
        wrap methods from fabric_wrp module
        wrapper assume that the first argument of each fapi methods is srv_ip
        all invocations have to be done without the first argument (srv_ip)
        """
        for attr in dir(fapi):
            if attr[0:2] == "__":
                continue

            module_attr = getattr(fapi, attr)
            if isinstance(module_attr, collections.Callable):
                setattr(self.fapi, attr,
                        types.MethodType(fapi_wrapper(attr), self))
            else:
                setattr(self, attr, module_attr)

        return True


    def guess_system(self, systype=None):
        """ guess on system of remote target """
        if systype == None:
            if not self.is_up():
                return False

            try:
                sysinfos_mod = "callbacks.systems_infos"
                __import__(sysinfos_mod)
            except ImportError:
                sysinfos_mod = "generic_callbacks.systems_infos"
                __import__(sysinfos_mod)

            LOG.log_d("guessing system using '%s'" % (sysinfos_mod))
            guess = sys.modules[sysinfos_mod].sysguess
            requisites = sys.modules[sysinfos_mod].check_prerequisites

            requisites(self.srv_ip)
            self.hostname, self.systemtype = guess(self.srv_ip)
            LOG.log_d("system guessed as %s" % (self.systemtype))

        else: self.systemtype = systype

        return True
