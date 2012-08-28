# -*- coding: iso-latin-1 -*-
"""
== SandCrawler callbacks system ==

Implementation of new systems/OS is made via creation of modules named with the
name of target system (ie. debian, solaris, netbsd, ...)

Two sub-modules are required for each system/OS:
  system: definition of several system based methods
  network: definition of several system based network methods

SandCrawler libraries will also need specifics callbacks to be usable. See
python __doc__ of librarie to know which callbacks to implement for each of it.

For each librarie, required function have to be defined. Functions prototype
and function returned value have to be defined like describes in librarie
__doc__. Every functions defined in modules (required or not) has to use the
self attribute.

More documentation will come soon...
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"
