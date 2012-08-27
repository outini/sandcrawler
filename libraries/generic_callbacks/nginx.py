#! /usr/bin/env python
# -*- coding: iso-latin-1 -*-
"""
Generic callbacks for nginx control.

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
__file__ =          "nginx.py"
__status__ =        "Development"

def enable_site(self, site, available_sites, enabled_sites):
    """
    Enable an nginx site by creating symlinks.

    Argument site:
        Nginx site that you want to enable.
    Argument available_sites:
        Directory with files providing information on available sites.
    Arguments enabled_sites:
        Directory with links to the files in available_sites for enabled sites.
    """
    # Filesystem operations callback (fsh) is required
    if not hasattr(self, "fsh"):
        self.load_callbacks("fsh")

    out = self.fsh.symlink("%s %s", use_sudo=True % (
                                    (available_sites.rstrip('/') + '/'+ site),
                                    (enabled_sites.rstrip('/') + '/' + site)))

def disable_site(self, site, enabled_sites):
    """
    Disable an nginx site by removing symlinks.

    Argument site:
        Nginx site that you want to disable.
    Arguments enabled_sites:
        Directory with links to the files in available_sites for enabled sites.
    """
    # Filesystem operations callback (fsh) is required
    if not hasattr(self, "fsh"):
        self.load_callbacks("fsh")

    out = self.fsh.remove_file("%s", use_sudo=True % (
                                        enabled_sites.rstrip('/') + '/' + site))

def list_sites(self, site, directory):
    """
    List site into directory.

    Argument site:
        Could be empty.
    Argument directory:
        Should be your directory with available or enabled sites.
    """
    # Filesystem operations callback (fsh) is required.
    if not hasattr(self, "fsh"):
        self.load_callbacks("fsh")

    out = self.fsh.list_files("%s" % (directory.rstrip('/') + '/' + site))
    return out

def start(self):
    """ Start nginx service. """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    out = self.services.srvctl("nginx", "start")

def stop(self):
    """ Stop nginx service. """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    out = self.services.srvctl("nginx", "stop")

def reload(self):
    """ Reload nginx service. """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    out = self.services.srvctl('nginx', 'reload')

def configtest(self):
    """
    Test nginx configuration file.
    """
    # Services callback is required.
    if not hasattr(self, "services"):
        self.load_callbacks("services")

    out = self.services.srvctl('nginx', 'configtest')
    return (not out.failed, out)
