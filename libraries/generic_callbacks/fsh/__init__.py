# -*- coding: iso-latin-1 -*-
"""
Generic callbacks for filesystem hierarchy
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

# we import as private,
# only public functions and attributes are set as callback methods
import sc_logs as __LOG
import fabric_wrp as __fapi
import sc_config as __config
import sc_common as __scc


def file_exists(self, filename):
    """ check if file exists """
    return __fapi.file_exists(self.srv_ip, filename)

def list_files(self, file_pattern, full = True, use_sudo = False):
    """ list files """
    return __fapi.list_files(self.srv_ip, file_pattern,
                             full = full, use_sudo = use_sudo)

def write_file(self, filename, file_content, mode = "w", use_sudo = False):
    """ write content to a file  """
    return __fapi.write_file(self.srv_ip, filename, file_content,
                             mode = mode, use_sudo = use_sudo)

def file_append(self, filename, content, use_sudo = False, partial = True):
    """ append content to a file """
    return __fapi.file_append(self.srv_ip, filename, content,
                              use_sudo = use_sudo, partial = partial)

def copy_file(self, file_src, file_dst, use_sudo = False):
    """ copy a file """
    return __fapi.copy_file(self.srv_ip, file_src, file_dst,
                            use_sudo = use_sudo)

def move_file(self, file_src, file_dst, use_sudo = False):
    """ move a file """
    return __fapi.move_file(self.srv_ip, file_src, file_dst,
                            use_sudo = use_sudo)

def remove_file(self, filename, recursive = False, use_sudo = False):
    """ remove a file on filesystem """
    return __fapi.remove_file(self.srv_ip, filename,
                              recursive = recursive, use_sudo = use_sudo)

def chmod_file(self, filename, mode, use_sudo = False):
    """ chmod file with mode """
    if use_sudo:
        return __fapi.sudo(self.srv_ip, "chmod %s %s" % (mode, filename))
    return __fapi.run(self.srv_ip, "chmod %s %s" % (mode, filename))

def chown_file(self, filename, owner, group, recursive = True):
    """ chown file with owner and group """
    opts = ""
    if recursive is True:
        opts = "-R"

    return __fapi.sudo(self.srv_ip,
                       "chown %s %s:%s %s " % (opts, owner, group, filename))

def sed_file(self, filename, pat_src, pat_dst, use_sudo = True):
    """ sed the content of file """
    return __fapi.sed_file(self.srv_ip, filename,
                           pat_src, pat_dst,
                           use_sudo = use_sudo)

def file_contains(self, pattern, filename):
    """ check if file contains pattern """
    return __fapi.file_contains(self.srv_ip, pattern, filename)

def get_file_content(self, filename, use_sudo = False):
    """ retrieve file content """
    return __fapi.file_contains(self.srv_ip, pattern, filename)

def upload_tmpl(self, template, filename, context, use_sudo = False):
    """ upload a template """
    return __fapi.upload_tmpl(self.srv_ip, template, filename, context,
                              use_sudo = use_sudo)

def install_skel(self, skelpath, dirtarget):
    """ install skel in directory """
    return __fapi.sudo(self.srv_ip, "rsync -a %s %s" % (skelpath, dirtarget))

def symlink(self, target, source, use_sudo = False):
    """ create symlink with 'ln' binary """
    if use_sudo:
        return __fapi.sudo(self.srv_ip, "ln -s %s %s" % (target, source))
    return __fapi.run(self.srv_ip, "ln -s %s %s" % (target, source))

def wget_file(self, target, storage, use_sudo = False):
    """ wget file or directory """

    cmd = "wget %s -O %s" % (target, storage)
    if use_sudo:
        return __fapi.sudo(self.srv_ip, cmd, nocheck = True)
    return __fapi.run(self.srv_ip, cmd, nocheck = True)

def tar_extract(self, target, storage, files = list(),
                compr = True, use_sudo = False):
    """ extract files from tar archive """

    opts = "xf"
    if compr is True:
        opts = "xzf"

    cmd = "tar %s %s -C %s %s" % (opts, target, storage, " ".join(files))
    if use_sudo:
        return __fapi.sudo(self.srv_ip, cmd, nocheck = True)
    return __fapi.run(self.srv_ip, cmd, nocheck = True)

def make_dir(self, directory, use_sudo = True):
    """ create directory using mkdir -p """
    return __fapi.make_dir(self.srv_ip, directory, use_sudo = use_sudo)
