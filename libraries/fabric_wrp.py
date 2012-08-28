# -*- coding: iso-latin-1 -*-
"""
fabric api wrapper linked to fabric v0.9.1
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

import fabric.api
from fabric.context_managers import settings, hide
from fabric.contrib.files import exists, append, contains, sed, upload_template
import re

def quietfab():
    """ make fabric quiet """
    fabric.state.output.status = False
    fabric.state.output.running = False
    fabric.state.output.stderr = True
    fabric.state.output.warnings = False
    fabric.state.output.debug = False
    fabric.state.output.aborts = True
    fabric.state.output.stdout = False
    return True

def remote_exec(cmd, use_sudo, user=None, shell=True, nocheck=False):
    """ wrapper to fabric run and sudo """
    if use_sudo:
        out = fabric.api.sudo(cmd, user=user, pty=True, shell=shell)
    else:
        out = fabric.api.run(cmd, pty=True, shell=True)

    if out.return_code != 0 and not nocheck:
        raise RuntimeError("exec failed: %s\n%s" % (cmd, out))

    out.raw = out.__str__()
    out.lines = out.splitlines()

    return out

def sudo(ipaddr, cmd, user=None, shell=True, nocheck=False):
    """ run remote command as sudo """
    with settings(host_string=ipaddr):
        return remote_exec(cmd, use_sudo=True,
                           user=user, shell=shell, nocheck=nocheck)

def run(ipaddr, cmd, shell=True, nocheck=False):
    """ run remote command """
    with settings(host_string=ipaddr):
        return remote_exec(cmd, shell=shell, use_sudo = False,
                            nocheck=nocheck)

def local(cmd, nocheck=True):
    """ run local command """
    with hide('running', 'stdout', 'warnings', 'stderr'):
        out = fabric.api.local(cmd)
        if out.return_code != 0 and not nocheck:
            raise RuntimeError("localExecFail", "%s" % (out))

    out.raw = out.__str__()
    out.lines = out.splitlines()

    return out

def file_exists(ipaddr, filename):
    """ check if file exists """
    with settings(host_string = ipaddr):
        return exists(filename)

def file_contains(ipaddr, pattern, filename):
    """ check if file contains pattern """
    with settings(host_string = ipaddr):
        return contains(pattern, filename)

def get_file_content(ipaddr, filename, use_sudo = False):
    """ retrieve file content """
    with settings(host_string = ipaddr):
        if not file_exists(ipaddr, filename):
            return None

        cmd = "cat %s" % (filename)
        out = remote_exec(cmd, use_sudo = use_sudo)
        out.lines_clean = []
        for line in out.lines:
            clean_line = re.sub(r"#.*", r"", line).strip()
            if len(clean_line):
                out.lines_clean.extend([clean_line])

        return out

def list_files(ipaddr, file_pattern,
               full = True, use_sudo = False):
    """ list matching file and display fullpath or just filename """

    cmd = "ls -1 %s" % (file_pattern)
    with settings(host_string = ipaddr):
        out = remote_exec(cmd, use_sudo = use_sudo, nocheck = True)

    files = []
    if out.return_code == 0:
        if full:
            files = out.lines
        else:
            for line in out.lines:
                files.append(line.split("/")[-1])

    return files

def file_append(ipaddr, filename, content,
                use_sudo = False, partial = True):
    """ append content to a file """
    if not file_exists(ipaddr, filename):
        return False

    with settings(host_string = ipaddr):
        return append(content, filename,
                      use_sudo = use_sudo, partial = partial)

def write_file(ipaddr, filename, file_content, mode = "w", use_sudo = False):
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
        return remote_exec("%s" % (cmd), use_sudo = use_sudo)

def copy_file(ipaddr, file_src, file_dst, use_sudo = False):
    """ copy a file """
    if not file_exists(ipaddr, file_src):
        return False

    cmd = "cp %s %s" % (file_src, file_dst)
    with settings(host_string = ipaddr):
        return remote_exec("%s" % (cmd), use_sudo = use_sudo)

def move_file(ipaddr, file_src, file_dst, use_sudo = False):
    """ copy a file """
    if not file_exists(ipaddr, file_src):
        return False

    cmd = "mv %s %s" % (file_src, file_dst)
    with settings(host_string = ipaddr):
        return remote_exec("%s" % (cmd), use_sudo = use_sudo)

def sed_file(ipaddr, filename, pat_src, pat_dst, use_sudo = True):
    """ sed the content of file """
    if not file_exists(ipaddr, filename):
        return False

    with settings(host_string = ipaddr):
        return sed(filename, pat_src, pat_dst, use_sudo = use_sudo)

def remove_file(ipaddr, filename, recursive = False, use_sudo = False):
    """ remove a file """
    if recursive is True:
        opts = "-r"
    else:
        opts = ""

    cmd = "rm %s %s" % (opts, filename)
    with settings(host_string = ipaddr):
        return remote_exec("%s" % (cmd), use_sudo=use_sudo)

def make_dir(ipaddr, directory, use_sudo = False):
    """ create directory using mkdir -p """
    cmd = "mkdir -p %s" % (directory)
    with settings(host_string = ipaddr):
        return remote_exec("%s" % (cmd), use_sudo = use_sudo)

def upload_tmpl(ipaddr, template, filename, context, use_sudo = False):
    """ upload a template """
    cmd = "rm %s" % (filename)
    with settings(host_string = ipaddr):
        return upload_template(template, filename, context,
                               use_sudo = use_sudo)
