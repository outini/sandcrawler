#! /usr/bin/env python
# -*- coding: iso-latin-1 -*-
"""
fabric api wrapper
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

import fabric.api
from fabric.context_managers import settings, hide
from fabric.contrib.files import exists, append

import re

def quietfab():
    """ make fabric quiet """
    fabric.state.output.status = False
    fabric.state.output.running = False
    fabric.state.output.stderr = True
    fabric.state.output.warnings = True
    fabric.state.output.debug = False
    fabric.state.output.aborts = True
    fabric.state.output.stdout = False
    return True

def remote_exec(cmd, use_sudo):
    """ wrapper to fabric run and sudo """
    if use_sudo:
        func = fabric.api.sudo
    else:
        func = fabric.api.run

    out = func(cmd, pty=True)
    if out.return_code != 0 and not fabric.api.env.warn_only:
        raise RuntimeError("execFail", "%s" % (out))

    out.raw = out.__str__()
    out.lines = out.splitlines()

    return out

def sudo(ipaddr, cmd):
    """ run remote command as sudo """
    with settings(host_string = ipaddr):
        return remote_exec(cmd, use_sudo=True)

def run(ipaddr, cmd):
    """ run remote command """
    with settings(host_string = ipaddr):
        return remote_exec(cmd, use_sudo=False)

def file_exists(ipaddr, filename):
    """ check if file exists """
    with settings(host_string = ipaddr):
        return exists(filename)

def get_file_content(ipaddr, filename, use_sudo=False):
    """ retrieve file content """
    with settings(host_string = ipaddr):
        if not file_exists(ipaddr, filename):
            return None

        cmd = "cat %s" % (filename)
        out = remote_exec(cmd, use_sudo=use_sudo)
        out.lines_clean = []
        for line in out.lines:
            clean_line = re.sub(r"#.*", r"", line).strip()
            if len(clean_line):
                out.lines_clean.extend([clean_line])

        return out

def list_files(ipaddr, file_pattern, full=True, use_sudo=False):
    """ list matching file and display fullpath or just filename """

    cmd = "ls %s" % (file_pattern)
    with settings(hide("warnings"),
                  host_string = ipaddr,
                  warn_only = True):
        out = remote_exec(cmd, use_sudo=use_sudo)

    files = []
    if out.return_code == 0:
        if full:
            files = out.lines
        else:
            for line in out.lines:
                files.append(line.split("/")[-1])

    return files

def file_append(ipaddr, filename, content, use_sudo=False, partial=True):
    """ append content to a file """
    if not file_exists(ipaddr, filename):
        return False

    with settings(host_string = ipaddr):
        return append(content, filename, use_sudo=use_sudo, partial=partial)

def write_file(ipaddr, filename, file_content, mode="w", use_sudo=False):
    """ write content to a file  """
    if type(file_content) is not type([]):
        file_content = [file_content]

    if mode == "w":
        cmd = "sed 's/^X//' > '%s' <<'EOF'\nX%s\nEOF" % (
            filename, "\nX".join(file_content))
    else:
        cmd = "sed 's/^X//' >> '%s' <<'EOF'\nX%s\nEOF" % (
            filename, "\nX".join(file_content))

    with settings(host_string = ipaddr):
        return remote_exec("%s" % (cmd), use_sudo=use_sudo)

def copy_file(ipaddr, file_src, file_dst, use_sudo=False):
    """ copy a file """
    if not file_exists(ipaddr, file_src):
        return False

    cmd = "cp %s %s" % (file_src, file_dst)
    with settings(host_string = ipaddr):
        return remote_exec("%s" % (cmd), use_sudo=use_sudo)
