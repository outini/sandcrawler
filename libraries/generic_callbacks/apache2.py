#! /usr/bin/env python
# -*- coding: iso-latin-1 -*-
"""
Generic callbacks for apache2 control.

Requirements:
    - generic_callbacks/fsh
    - generic_callbacks/services
"""

__docformat__ =     "restructuredtext en"
__author__ =        "Guillaume 'Llew' Delpierre"
__credits__ =       "Guillaume 'Llew' Delpierre"
__license__ =       "GPLv3"
__maintainer__ =    "Guillaume 'Llew' Delpierre"
__email__ =         "gde@llew.me"
__file__ =          "apache2.py"
__status__ =        "Development"

# We import as private.
import sc_config as __config
import sc_logs as __LOG

def list_sites(self, directory, site=''):
    """
    List site into sites-available or site-enabled directory.
    ``directory`` is required and must be set in conf.d/*/services.conf.
    In this case, ``*`` must be your env.
    ``site`` could be empty or wildcard for now, glob characters are not
    allowed right now.

    ToDo: accept glob character to ``site``.
    """
    config = {}
    # Filesystem operations callback (fsh) is required.
    if not hasattr(self, 'fsh'):
        self.load_callbacks('fsh')

    config = __config.get_config('services.conf',
                [self.systemtype]).get_section('apache2')[1]

    valid_directory = ['available', 'enabled']
    if directory not in valid_directory:
        __LOG.log_die("%s: not a valid path." % (directory))

    config_path_site = config["path_sites_%s" % (directory)]
    site_exist = self.fsh.file_exists("%s" % (config_path_site.rstrip('/') +
                    '/' + site))

    if not site or site == '*':
        out = self.fsh.list_files("%s" % (
            config_path_site.rstrip('/') + '/' + site))
        return out
    else:
        if site_exist is False:
            __LOG.log_die("File %s: not found in %s" % (site, config_path_site))
        else:
            out = self.fsh.list_files("%s" % (
                config_path_site.rstrip('/') + '/' + site))
            return out, site, site_exist

def start(self):
    """ Start apache2 service. """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    out = self.services.srvctl("apache2", "start")
    return out

def stop(self, grace=False):
    """ Stop apache2 service. """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    if grace:
        out = self.services.srvctl("apache2", "graceful-stop")
    else:
        out = self.services.srvctl("apache2", "stop")
    return out

def reload_service(self):
    """ Reload apache2 service. """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    out = self.services.srvctl('apache2', 'graceful')
    return out

def restart(self, grace=False):
    """
    Restart apache2 via apachectl
    """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    if grace:
        out = self.services.srvctl('apache2', 'graceful')
    else:
        out = self.services.srvctl('apache2', 'restart')
    return out

def configtest(self):
    """
    Test apache2 configuration file.
    """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    out = self.services.srvctl('apache2', 'configtest')
    return out

def server_status(self):
    """
    Show server-status
    """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    out = self.services.srvctl('apache2', 'server_status')
    return out

