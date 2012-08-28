# -*- coding: iso-latin-1 -*-
"""
common functions for sandcrawler
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

import sys
import time
import socket
import paramiko
import fabric_wrp as fapi
import sc_logs as __LOG

class EmptyClass:
    """ Empty class for various purposes """

class AttStr(str):
    """
    String with attribute.
    Yes, it rocks.
    Yes, all your problems vanished.
    Yes, fsHhshhhshhhHHh tsssk tssk fFSShhhsh
    """

def findcaller(level=1):
    """ find function which called """
    filename = sys._getframe(level).f_code.co_filename
    caller = sys._getframe(level).f_code.co_name
    return (caller, filename)

def is_host_up(host, port=22):
    """ check host connection on ip/port """
    original_timeout = socket.getdefaulttimeout()
    new_timeout = 3
    socket.setdefaulttimeout(new_timeout)
    host_status = False
    try:
        paramiko.Transport((host, port))
        host_status = True
    except:
        pass

    socket.setdefaulttimeout(original_timeout)
    __LOG.log_d("connection on %s port %s: %s" % (host, port, host_status))
    return host_status

def wait_host(host_ip, status, wait_round, host_port=22):
    """ wait for a status change """
    if status == "UP":
        state = True
    elif status == "DOWN":
        state = False
    else:
        raise ValueError("unknown status '%s'" % (status))

    while is_host_up(host_ip, int(host_port)) != state and wait_round > 0:
        time.sleep(5)
        wait_round -= 1

    if is_host_up(host_ip, 22) is not state:
        return False
    return True

def check_type(attr, reference, soft=False):
    """ check if attr type is reference type """
    if type(attr) != reference:
        if soft:
            return False
        raise TypeError("type should be %s" % (reference))
    return True

def check_dict(dict_obj, description):
    """ check keys and values of dict_obj """
    for key, value in description.iteritems():
        if len(value) < 2 or (not value[1] and len(value) < 3):
            raise TypeError("malformated description for key %s" % (key))
        if not dict_obj.has_key(key):
            if value[1]:
                raise TypeError("key %s is required but not found" % (key))
            else: dict_obj.update({key: value[2]})
        else:
            if type(dict_obj[key]) != value[0]:
                raise TypeError("value of key %s should be %s" % (key,
                                                                  value[0]))
    return dict_obj

def ip2mac(ip):
    """ generate virtual mac address from IP """
    (b, c, d) = ip.split('.')[1:4]
    return "00:16:3E:%02X:%02X:%02X" % (int(b), int(c), int(d))

def genRandom(length, chars="A-Za-z0-9"):
    """ retrieve random stuff from urandom """
    random = "</dev/urandom tr -dc '%s' | head -c%s" % (chars, length)
    return fapi.local(random)

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
    elif not len(itemlist):
        return dict()
    elif not isinstance(itemlist[0], str):
        raise TypeError("type of first element must be str")

    key = itemlist.pop(0)
    if not len(itemlist):
        itemlist = [None]

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
