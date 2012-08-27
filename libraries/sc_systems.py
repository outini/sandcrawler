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
__license__ = "beerware"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

import sys
import inspect
import fabric_wrp as fapi

###### NOT WORKING, NO TIME TO FIX
# class Generic:
#     """ generic class for unimplemented os/distribs """
#     def __init__(self):
#         return None

#     def __getattr__(self, attrname):
#         """ getattr override for unimplemented methods """

#         def __unimplemented(*args):
#             """ generic unimplemented methods handler """
#             msg = "%s not implemented in callbacks" % (attrname)
#             raise RuntimeError("unimplemented", msg)

#         #if attrname in [ member[0] for member in inspect.getmembers(self)]:
#         #if attrname in dir(self):
#         if attrname in self.__dict__:
#             return getattr(self, attrname)
#         __unimplemented()

class CallBacks():
    """ class to store callbacks """
    def __init__(self, target_module):
        __import__(target_module)
        self.calls = sys.modules[target_module]

        for attr in dir(self.calls):
            # import everything but builtins and privates
            if attr[0:2] == "__":
                continue

            # callback store exemple:
            print "callback store: self.%s --> %s.%s" % (
                attr, self.calls.__name__, attr)

            # store callback
            setattr(self, attr,
                    getattr(self.calls, attr))
        return None

class Server:
    """ server class with os/distribs callbacks """
    def __init__(self, srv_ip):
        self.srv_ip = srv_ip
        # detect target system type
        self.systemtype = self.guess_system()

        # load user's standard callbacks for guessed system
        self.load_callbacks()

    def load_callbacks(self, callback=""):
        """ callbacks loader """
        if not len(callback):
            # load standard callbacks if no args
            required_callbacks = ["system", "network"]
            for callback in required_callbacks:
                target_module = "callbacks.%s.%s" % (self.systemtype, callback)
                setattr(self, callback, CallBacks(target_module))
        else:
            # load callback specified by arg
            target_module = "callbacks.%s.%s" % (self.systemtype, callback)
            setattr(self, callback, CallBacks(target_module))

    def guess_system(self, systype=""):
        """ guess on system of remote target """
        if not len(systype):
            out = fapi.run(self.srv_ip, 'cat /etc/issue')
            system = out.split()[0].lower()
        else:
            system = systype

        return system

    def exec_method(self, method, *args):
        """ """
        try:
            getattr(self.callbacks, method)(args)
        except:
            raise RuntimeError("fail", "bla")
