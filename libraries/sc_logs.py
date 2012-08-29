# -*- coding: iso-latin-1 -*-
"""
logging functions for sandcrawler
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

import os
import sys
import logging
import logging.handlers
import ConfigParser
import sc_common as scc

###
### USE OF PYTHON LOGGING FACILITY
### http://docs.python.org/library/logging.html
###

DEFAULT_CONFIG = "conf.d/logging.conf"
DEFAULT_CONFIG_INCLUDES = "conf.d/logging.d/"

class SandLogging:
    """ wrapper class to configure logging facility """
    def __init__(self):
        """ initialise logging facility from configuration files """
        self.config = ConfigParser.ConfigParser()
        self.handlers = dict()
        self.formatters = dict()

        self.load_configuration()

    def load_configuration(self):
        """ load main configuration logging.conf """
        # order of the following is important !
        # formatters have to be load before handlers
        main_config = DEFAULT_CONFIG
        self.config.read(main_config)
        self.load_additionnal_configs()
        self.__load_formatters()
        self.__load_handlers()
        self.__load_loggers()

    def load_additionnal_configs(self):
        """ load additionnal configurations from include path """
        inc = DEFAULT_CONFIG_INCLUDES
        for item in os.listdir(inc):
            if os.path.isfile(inc + item) and item[-5:] == ".conf":
                self.config.read(inc + item)

    def __load_formatters(self):
        """ load formatters from configuration """
        for section in self.config.sections():
            if section[0:10] == "formatter_":
                formatter = section[10:]
                options = self.config.options(section)
                lformat = None
                datefmt = None

                if "format" in options:
                    lformat = self.config.get(section, "format", 1)
                if "datefmt" in options:
                    datefmt = self.config.get(section, "datefmt", 1)

                formatter_class = logging.Formatter(lformat, datefmt)
                self.formatters.update({formatter: formatter_class})

        return True

    def __load_handlers(self):
        """ load handlers for configuration """
        fixups = []
        for section in self.config.sections():
            if section[0:8] == "handler_":
                handler = section[8:]
                options = self.config.options(section)

                klass = self.config.get(section, "class")
                klass = eval(klass, vars(logging))
                args = self.config.get(section, "args")
                args = eval(args, vars(logging))
                handler_class = klass(*args)

                if "level" in options:
                    level = getattr(logging, self.config.get(section, "level"))
                    handler_class.setLevel(level)
                if "formatter" in options:
                    formatter = self.config.get(section, "formatter")
                    handler_class.setFormatter(self.formatters[formatter])

                if klass == logging.handlers.MemoryHandler:
                    if "target" in options:
                        target = self.config.get(section, "target")
                        fixups.append((handler_class, target))

                self.handlers.update({handler: handler_class})

        for handler_class, target in fixups:
            handler_class.setTarget(self.handlers[target])

        return True

    def __load_loggers(self):
        """ load loggers from configuration """
        section = "logger_root"
        options = self.config.options(section)

        root = logging.root

        if "level" in options:
            level = getattr(logging, self.config.get(section, "level"))
            root.setLevel(level)
        for handler in root.handlers[:]:
            root.removeHandler(handler)

        handlers = self.config.get(section, "handlers").split(',')
        for handler in handlers:
            root.addHandler(self.handlers[handler.strip()])

        existing = root.manager.loggerDict.keys()

        for section in self.config.sections():
            # logger_root has already been processed
            if section != "logger_root" and section[0:7] == "logger_":
                logger = section[7:]
                options = self.config.options(section)

                if "qualname" in options:
                    qualname = self.config.get(section, "qualname")
                else: qualname = logger

                handlers = self.config.get(section, "handlers").split(',')
                propagate = 0

                logger_class = logging.getLogger(qualname)

                if "level" in options:
                    level = getattr(logging, self.config.get(section, "level"))
                    logger_class.setLevel(level)
                if "propagate" in options:
                    propagate = self.config.getint(section, "propagate")
                for handler in logger_class.handlers[:]:
                    logger_class.removeHandler(handler)

                logger_class.propagate = propagate
                logger_class.disabled = 0

                for handler in handlers:
                    logger_class.addHandler(self.handlers[handler.strip()])

        # Disable any old loggers.
        for logger in existing:
            root.manager.loggerDict[logger].disabled = 1

        return True

# on initial import, SANDLOG is initialised
SANDLOG = SandLogging()

def log_(msg, level):
    """ generic logging function """
    #(caller, filename) = scc.findcaller(3)
    filename = scc.findcaller(3)[1]
    module = filename.split("/")[-1][0:-3]

    logger = logging.getLogger(module)
    getattr(logger, level)(msg)

# some short wrappers
def log_d(msg):
    """ log debug messages """
    return log_(msg, "debug")

def log_i(msg):
    """ log info messages """
    return log_(msg, "info")

def log_w(msg):
    """ log warning messages """
    return log_(msg, "warning")

def log_c(msg):
    """ log critical messages """
    return log_(msg, "critical")

def log_e(msg):
    """ log error messages """
    return log_(msg, "error")

def log_die(msg):
    """ log die message and stop """
    log_(msg, "error")
    sys.exit("Aborting from critical error.")
