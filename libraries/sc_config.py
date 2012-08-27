#! /usr/bin/env python
# -*- coding: iso-latin-1 -*-
"""
configuration management for sandcrawler
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

# Is named configparser (lowercase) in python 3.0+
import ConfigParser
import sc_logs as __LOG

# store of Config classes
CONFIG_LIST = dict()

class Config(ConfigParser.SafeConfigParser):
    """ simple class to store and use configuration """
    def __init__(self, configfile, search_path = None):
        ConfigParser.SafeConfigParser.__init__(self)
        self.configfile = configfile
        self.config = None

        # load configfile if found
        # update it if necessary with system specifics (systype != None)
        #self.update(configfile)
        specific_config = format_configname(configfile, prefix = search_path)
        self.read(specific_config)
        store_config(specific_config, self)

    def get_section(self, section_name, default = None):
        """ get section content as a dict """
        section_content = dict()
        try:
            for item in self.items(section_name, 1):
                section_content.update({item[0]: item[1]})
        except ConfigParser.NoSectionError:
            if default is not None:
                return self.get_section(default)
            else:
                return (None, None)

        return (section_name, section_content)

    def getopt(self, section_name, keys, default = None, vartype = None):
        """ get key, fallbacks or default """

        if type(keys) is not list:
            keys = [keys]
        if vartype not in ['boolean', 'int', 'float', None]:
            raise TypeError("unknown vartype: %s" % (vartype))

        for key in keys:
            try:
                if vartype is not None:
                    getkey = getattr(self, "get%s" % (vartype))
                    return getkey(section_name, key)
                else:
                    return self.get(section_name, key, 1)
            except ConfigParser.NoOptionError:
                pass

        return default

def format_configname(configfile, prefix = None):
    """ format config filename with prefix """
    split_configfile = configfile.split('/')
    filename = split_configfile.pop()
    path = "/".join(split_configfile)
    if prefix is not None:
        filename = "%s_%s" % (prefix, filename)

    return "%s/%s" % (path, filename)

def get_config(configfile, systype = None, refresh = False):
    """ get Config classes by filename and prefix """
    formated_configname = format_configname(configfile, prefix = systype)
    try:
        if refresh:
            raise RuntimeError("config refresh requested")
        return CONFIG_LIST[formated_configname]
    except (KeyError, RuntimeError):
        __LOG.log_d("reading configfile: %s" % (formated_configname))
        return Config(configfile, search_path = systype)

def store_config(configfile, config_class):
    """ store config by filename """
    CONFIG_LIST.update({configfile: config_class})
    return True
