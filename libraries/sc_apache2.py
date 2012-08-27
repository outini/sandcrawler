#! /usr/bin/env python
# -*- coding: iso-latin-1 -*-
"""
Apache2 management for sandcrawler
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

import sc_logs as __LOG

def config2struct(config_lines):
    """convert apache2 configuration to structure"""
    
