# -*- coding: iso-latin-1 -*-
"""
Simple module to display python code
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

def set_indent(level):
    """ set indentation """
    return " " * level * 4

def dump_(name, data, level=0):
    """ dump any types """
    output = ""
    if type(data).__name__ == "dict":
        output += dump_dict(name, data, level)
    elif type(data).__name__ == "list":
        output += dump_list(name, data, level)
    elif type(data).__name__ == "bool":
        output += dump_bool(name, data, level)
    #elif type(data).__name__ == "function":
    #    output += self.dump_function(name, data, level)
    #elif type(data).__name__ == "instance":
    #    output += self.dump_instance(name, data, level)
    else: # type(data).__name__ == "str":
        output += dump_str(name, data, level)

    return output

def dump_dict(name, data, level=0):
    """ dump dicts """
    output = str()
    indent = set_indent(level)
    if len(name):
        output += "%s%s = " % (indent, name)

    output += "{\n"
    level += 1
    indent = set_indent(level)

    for entry in sorted(data):
        output += "%s'%s':" % (indent, str(entry))
        output += dump_("", data[entry], level)

    level -= 1
    indent = set_indent(level)
    if level != 0:
        output += indent + "},\n"
    else:
        output += indent + "}\n"

    return output

def dump_str(name, value, level=0):
    """ dump strings """
    output = ""
    indent = set_indent(level)
    if len(name):
        output = indent + name + " = "
    if level != 0:
        output += "'" + str(value) + "',"
    else:
        output += "'" + str(value) + "'"

    return output + "\n"

def dump_list(name, data, level=0):
    """ dump lists """
    output = ""
    indent = set_indent(level)
    if len(name):
        output += indent + name + " = "

    output += "[\n"
    level += 1
    indent = set_indent(level)

    for entry in data:
        output += indent
        output += dump_("", entry, level)

    level -= 1
    indent = set_indent(level)
    if level != 0:
        output += indent + "],\n"
    else:
        output += indent + "]\n"

    return output

def dump_bool(name, value, level=0):
    """ dump booleans """
    output = ""
    indent = set_indent(level)
    if len(name):
        output = indent + name + " = "
    if level != 1:
        output += str(value) + ","
    else:
        output += str(value)

    return output + "\n"

