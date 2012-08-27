#! /usr/bin/env python
# -*- coding: iso-latin-1 -*-
"""
common functions for sandcrawler
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


class AttStr(str):
    """
    String with attribute.
    Yes, it rocks.
    Yes, all your problems vanished.
    Yes, fsHhshhhshhhHHh tsssk tssk fFSShhhsh
    """

def list2struct(struct, itemlist):
    """ convert itemlist to struct """
    if not isinstance(itemlist, list):
        raise TypeError("type must be list")
#    elif not len(itemlist) or len(itemlist) == 1:
#        raise RuntimeError("length of itemlist must be at least 2")
#    elif not isinstance(itemlist[0], str):
#        raise TypeError("type of first element must be str")

    for attr in itemlist:
        attr_name = attr.pop(0)
        if len(attr) > 1:
            attr_value = attr
        else:
            attr_value = attr[0]
        setattr(struct, attr_name, attr_value)
    
    return struct

def dict2struct(struct, itemdict):
    """ convert itemdict to struct """
    if not isinstance(itemdict, dict):
        raise TypeError("type must be dict")

    for key, value in itemdict.iteritems():
        if isinstance(value, dict):
            v_struct = AttStr("%s structure" % (key))
            value = dict2struct(v_struct, value)
        setattr(struct, key, value)

    return struct

def list2dict(itemlist):
    """ convert itemlist to dict """
    if not isinstance(itemlist, list):
        raise TypeError("type must be list")
    elif not len(itemlist) or len(itemlist) == 1:
        raise RuntimeError("length of itemlist must be at least 2")
    elif not isinstance(itemlist[0], str):
        raise TypeError("type of first element must be str")

    key = itemlist.pop(0)
    values = {}
    if isinstance(itemlist[0], str):
        if len(itemlist) < 2:
            values = itemlist[0]
        else:
            values = list2dict(itemlist)
    elif isinstance(itemlist[0], list):
        for value in itemlist:
            if len(value) and isinstance(value[0], str):
                values.update(list2dict(value))
            else:
                if len(itemlist) == 1:
                    values = value
                else:
                    values = itemlist
                break
    else:
        if len(itemlist) == 1:
            values = itemlist[0]
        else:
            values = itemlist

    return {key: values}
