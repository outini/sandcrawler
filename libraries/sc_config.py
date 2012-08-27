#! /usr/bin/env python
# -*- coding: iso-latin-1 -*-
"""
configuration management for sandcrawler
configuration files default search path is:
    ./conf.d/

Config class is inherited from ConfigParser.SafeConfigParser
Documentation is available at:
    http://docs.python.org/library/configparser.html

methods inherited:
    # SafeConfigParser.set(section, option, value)
    # ConfigParser.get(section, option[, raw[, vars]])
    # ConfigParser.items(section[, raw[, vars]])
    # RawConfigParser.defaults()
    # RawConfigParser.sections()
    # RawConfigParser.add_section(section)
    # RawConfigParser.has_section(section)
    # RawConfigParser.options(section)
    # RawConfigParser.has_option(section, option)
    # RawConfigParser.read(filenames)
    # RawConfigParser.readfp(fp[, filename])
    # RawConfigParser.get(section, option)
    # RawConfigParser.getint(section, option)
    # RawConfigParser.getfloat(section, option)
    # RawConfigParser.getboolean(section, option)
    # RawConfigParser.items(section)
    # RawConfigParser.set(section, option, value)
    # RawConfigParser.write(fileobject)
    # RawConfigParser.remove_option(section, option)
    # RawConfigParser.remove_section(section)
    # RawConfigParser.optionxform(option)
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
DEFAULT_SEARCH_PATH = "conf.d"

class Config(ConfigParser.SafeConfigParser):
    """ simple class to store and use configuration """
    def __init__(self, configfile, search_paths = list(), chainload = True):
        ConfigParser.SafeConfigParser.__init__(self)
        self.configfile = configfile
        self.search_paths = search_paths
        self.config = None

        self.load()
        store_config(self.configfile, self)

    def load(self):
        """ load configuration from files """
        # if configfile contains '/', load as full path file
        # search_paths are disabled when using fullpath configfile
        if "/" not in self.configfile:
            self.read('%s/%s' % (DEFAULT_SEARCH_PATH, self.configfile))
            self.chainload()
        else:
            self.read(self.configfile)

        return True

    def chainload(self):
        """ chainload configuration from search paths """
        if type(self.search_paths) != type(list()):
            raise RuntimeError('search_paths must be a list of paths')

        for path in self.search_paths:
            # search paths are relative to DEFAULT_SEARCH_PATH
            self.read("%s/%s/%s" % (DEFAULT_SEARCH_PATH, path,
                                    self.configfile))

        return True

    def empty_config(self):
        """ erase the whole configuration content """
        for section in self.sections():
            self.remove_section(section)

        return True

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

def get_config(configfile, search_paths = list()):
    """ get Config classes by filename and prefix """
    try:
        if search_paths != CONFIG_LIST[configfile].search_paths:
            CONFIG_LIST[configfile].empty_config()
            CONFIG_LIST[configfile].search_paths = search_paths
            CONFIG_LIST[configfile].load()
        return CONFIG_LIST[configfile]
    except (KeyError, AttributeError):
        __LOG.log_d("reading configfile: %s (%s)" % (configfile, search_paths))
        return Config(configfile, search_paths = search_paths)

def store_config(configfile, config_class):
    """ store config by filename """
    CONFIG_LIST.update({configfile: config_class})
    return True
