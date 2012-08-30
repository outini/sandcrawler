# -*- coding: iso-latin-1 -*-
"""
`fstab` callbacks for filesystem hierarchy
These depend on `fsh` callbacks and are stored in `fsh.fstab`
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
import sc_logs as __log
import sc_config as __config
import sc_common as __scc

import sc_pythongen as pygen

fstab_file = "/etc/fstab"
syntax_fields = ['filesystem', 'mountpoint', 'type',
                 'options', 'dump', 'pass']
content = None

def load(self):
    """
    Load fstab content from remote host.
    Default fstab location is: /etc/fstab

    `content` attribute is setted from the load.
    This attribute contains for each line:
      line number, filesystem, mountpoint, type, options, dump, pass, comment

    If content is successfully imported, method returns True, False otherwise.
    """
    line_num = 0
    fields = dict()

    out = self.mom.get_file_content(self.fstab_file)
    if out.failed is True:
        return False

    for line in out.lines:
        line_num += 1

        ## getting commented part
        comment = None
        s_line = line.split('#')
        if len(s_line) > 1:
            comment = '#'.join(s_line[1:])
        line = s_line[0]

        fields.update({ line_num: { 'comment': comment }})
        if len(line):
            line_fields = dict(zip(syntax_fields, line.split()))
            fields[line_num].update(line_fields)

    self.content = fields

    return True


def add_entry(self, entry):
    """
    Add an fstab entry to the content dict.
    The passed entry should be a dict with the following keys:
        dump
        filesystem
        mountpoint
        options
        pass
        type
    These keys match the fstab file fields.
    Optionnal key 'comment' is used to store comments

    This method return a tuple with:
        - the return boolean
        - the dict describing the new content (or None)
    """
    if self.content is None:
        return (False, None)

    self.content.update({ "%s" % (len(self.content)+1): entry })

    return (True, self.content)

def del_entry(self, entry, force_multiple = False):
    """
    Delete an fstab entry to the content dict.
    The passed entry should be a dict with one or more of the following keys:
        dump
        filesystem
        mountpoint
        options
        pass
        type
    These keys match the fstab file fields.
    The passed keys are used to match entries from the fstab content.
    Only one entry has to match, if several match, method return False and
    nothing is done.

    This method return a tuple with:
        - the return boolean
        - the dict describing the deleted entry (or None)
    """
    if self.content is None:
        return (False, None)

    matched_entries = self.find_entry(entry)
    if not len(matched_entries):
        return (False, None)

    if len(matched_entries) > 1 and force_multiple is False:
        __log.log_w('%s: multiple fstab entries matched' % (self.trk.hostname))
        return (False, None)

    ## removing the matched entries from fstab content
    for key in matched_entries.keys():
        del(self.content[key])

    ## resort the content dict for lines number consistency
    index = 0
    resort_content = dict()
    for key in sorted(self.content.keys()):
        index += 1
        resort_content.update({index: self.content[key]})
    self.content = resort_content

    return (True, matched_entries)

def find_entry(self, entry):
    """
    Find all matching entries from the content dict.
    The passed entry should be a dict with one or more of the following keys:
        dump
        filesystem
        mountpoint
        options
        pass
        type
    These keys match the fstab file fields.
    The passed keys are used to match entries from the fstab content.

    This method return a dict describing the matched entries
    """
    matches = dict()
    for line, fields in self.content.iteritems():
        current, wanted = set(fields.keys()), set(entry.keys())
        matched_keys = current.intersection(wanted)
        matched_fields = [ key for key in matched_keys \
                               if entry[key] == fields[key] ]

        if len(matched_fields) == len(entry):
            matches.update({line: fields})

    ## method for partial match ?
    # if not len(match_list):
    #     return dict()

    # match_list = sorted(match_list, reverse = True)
    # best_mcount = match_list[0][0]
    # for entry in [ key[1] for key in match_list if key[0] == best_mcount ]:
    #     best_matches.update(entry)

    return matches


def validate_entry(self, entry):
    """
    Validate an fstab entry using syntax_fields.
    Only the presence of each fields is checked.

    Return True if success, False otherwise.
    """
    try:
        [ entry[key] for key in self.syntax_fields ]
        return True
    except KeyError:
        return False

def __none2empty(value):
    """Quick transform of None object in str('')"""
    if value is None:
        return str()
    return value

def write(self, backup = True, stdout = False):
    """
    Write fstab content to remote host's fstab
    If content is successfully written, method returns True, False otherwise.

    This method return a tuple containing:
      - the return boolean
      - the content lines list written
    """
    if self.content is None:
        return (False, None)

    content_to_write = list()
    for line_n in sorted(self.content.keys()):
        entry_fields = [ __none2empty(self.content[line_n].get(key)) \
                             for key in self.syntax_fields ]
        comment = self.content[line_n].get('comment')
        entry = "\t".join(entry_fields).strip()

        ## keep good looking file
        comment_start = len(entry) and " #" or "#"
        if comment is not None:
            line = "%s%s%s" % (entry, comment_start, comment)
        else:
            line = entry

        content_to_write.append(line)

    if stdout is True:
        print "\n".join(content_to_write)
        return (True, content_to_write)

    if backup is True:
        out = self.mom.copy_file(self.fstab_file, "%s.bak" % self.fstab_file,
                                 use_sudo = True)
        if out.failed is True:
            return (False, content_to_write)

    out = self.mom.write_file(self.fstab_file, content_to_write,
                              use_sudo = True)
    return (not out.failed, content_to_write)
