import fabric.api
import os

class PythonGenerator:
    def __init__(self):
        self.indent = ""
        return None

    def setIndent(self, level):
        self.indent = ""
        numspace = level * 4
        for i in range(0,numspace):
            self.indent = self.indent + " "

    def dump_(self, name, data, level=0):
        output = ""
        if type(data).__name__ == "dict":
            output += self.dump_dict(name, data, level)
        elif type(data).__name__ == "list":
            output += self.dump_list(name, data, level)
        elif type(data).__name__ == "bool":
            output += self.dump_bool(name, data, level)
        #elif type(data).__name__ == "function":
        #    output += self.dump_function(name, data, level)
        #elif type(data).__name__ == "instance":
        #    output += self.dump_instance(name, data, level)
        else: # type(data).__name__ == "str":
            output += self.dump_str(name, data, level)

        return output

    def dump_dict(self, name, data, level=0):
        output = ""
        self.setIndent(level)
        if len(name):
            output += self.indent + name + " = "

        output += "{\n"
        level += 1
        self.setIndent(level)
            
        for entry in data:
            output += self.indent + "'" + str(entry) + "': "
            output += self.dump_("", data[entry], level)

        level -= 1
        self.setIndent(level)
        if level != 0:
            output += self.indent + "},\n"
        else: output += self.indent + "}\n"

        return output

    def dump_str(self, name, value, level=0):
        s = ""
        self.setIndent(level)
        if len(name):
            s = self.indent + name + " = "
        if level != 0: s += "'" + str(value) + "',"
        else: s += "'" + str(value) + "'"

        return s + "\n"

    def dump_list(self, name, data, level=0):
        output = ""
        list = ""
        self.setIndent(level)
        if len(name):
            output += self.indent + name + " = "

        output += "[\n"
        level += 1
        self.setIndent(level)

        for entry in data:
            output += self.indent
            output += self.dump_("", entry, level)

        level -= 1
        self.setIndent(level)
        if level != 0:
            output += self.indent + "],\n"
        else: output += self.indent + "]\n"

        return output

    def dump_bool(self, name, value, level=0):
        bool = ""
        self.setIndent(level)
        if len(name):
            bool = self.indent + name + " = "
        if level != 1: bool += str(value) + ","
        else: bool += str(value)

        return bool + "\n"

