"""
Generic callbacks for system users
"""

# we import as private,
# only public functions and attributes are set as callback methods
import sc_logs as __LOG
import fabric_wrp as __fapi
import sc_config as __config
import sc_common as __scc

__USERS_CONFIGFILE = "users.conf"
__SYSUSER_DEFAULT_SHELL = "/bin/false"

def retrieve_config_infos(self):
    """ retrieve config info """
    caller = __scc.findcaller(2)[0]
    config = __config.get_config(__USERS_CONFIGFILE, [self.systemtype])
    return config.get_section(caller)

def user_group_ctl(self, config, context):
    """ run command describe in config """
    if config.has_key('use_sudo') and config['use_sudo'] == 'True':
        rexec = __fapi.sudo
    else: rexec = __fapi.run

    out = rexec(self.srv_ip, config['cmd'] % (context), nocheck=True)
    return (not out.failed, out)

def gen_pwhash(self, password):
    """ generate password hash on remote host """
    __LOG.log_d("generating password hash")
    config = self.users.retrieve_config_infos()[1]

    context = {'password': password}
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("password hash generated: %s" % (ret[0]))

    return ret

def sysuser_exists(self, username):
    """ check if sysuser exists """
    __LOG.log_d("checking user %s" % (username))
    config = retrieve_config_infos(self)[1]

    context = {'username': username}
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("user %s exists: %s" % (username, ret))

    return ret

def sysuser_set_passwd(self, username, password):
    """ set sysuser password """
    __LOG.log_d("setting user %s password" % (username))
    config = retrieve_config_infos(self)[1]

    context = {
        'username': username,
        'password_hash': gen_pwhash(self, password)[1]
        }
    ret = user_group_ctl(self, config, context)
    __LOG.log_d('password setted: %s' % (repr(ret)))

    return ret

def sysuser_rename(self, username_src, username_dst):
    """ rename a sysuser """
    __LOG.log_d("renamming user %s to %s" % (username_src, username_dst))
    config = retrieve_config_infos(self)[1]

    context = {
        'username_src': username_src,
        'username_dst': username_dst,
        }
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("user renamed: %s" % (repr(ret)))

    return ret

def sysuser_change_home(self, username, home):
    """ change user's home """
    __LOG.log_d("changing user %s home to %s" % (username, home))
    config = retrieve_config_infos(self)[1]

    context = {
        'username': username,
        'home': home,
        }
    ret = user_group_ctl(self, config, context)
    __LOG.log_d('home changed: %s' % (repr(ret)))

    return ret


def sysuser_get_uid(self, username):
    """ get sysuser numeric uid """
    __LOG.log_d("getting user %s id" % (username))
    config = retrieve_config_infos(self)[1]

    context = {'username': username}
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("got user uid: %s" % (repr(ret)))

    return ret

def sysuser_set_groups(self, username, groups, update=True, primary_group=""):
    """ set sysuser groups """
    __LOG.log_d("setting groups for user %s" % (username))
    config = retrieve_config_infos(self)[1]

    if type(groups) != list:
        raise TypeError("type of groups should be list")
    if type(primary_group) != str:
        raise TypeError("type of primary_group should be str")

    # cleaning user from all groups if not update
    # adding user "already member groups" if update
    if not update:
        __fapi.sed_file(self.srv_ip,
                        config['groupfile'],
                        r'([,:])%s(,([^:]*))*' % (username), r'\1\3',
                        use_sudo=config.has_key('use_sudo'))
    else: groups = list(set(groups + sysuser_get_groups(self, username)[1]))

    # set primary group with first group if needed
    if len(primary_group):
        __LOG.log_d("primary group: %s" % (primary_group))
        primary_group_opt = config['primary_group_opt'] % (
            {'primary_group': primary_group})
    else: primary_group_opt = ""

    if len(groups):
        __LOG.log_d("secondary groups: %s" % (groups))
        secondary_groups = ",".join(groups)
        secondary_groups_opt = config['secondary_groups_opt'] % (
            {'secondary_groups': secondary_groups})
    else: secondary_groups = secondary_groups_opt = ""

    context = {
        'username': username,
        'primary_group': primary_group,
        'secondary_groups': secondary_groups,
        'primary_group_opt': primary_group_opt,
        'secondary_groups_opt': secondary_groups_opt
        }
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("groups setted: %s" % (repr(ret)))

    return ret

def sysuser_get_groups(self, username, numeric=False):
    """ get sysuser groups list (primay first) """
    __LOG.log_d("getting groups of user %s" % (username))
    config = retrieve_config_infos(self)[1]

    # if numeric is True, use numeric_opt from config
    numeric_opt = numeric and config['numeric_opt'] or ""
    context = {
        'username': username,
        'numeric_opt': numeric_opt
        }
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("got user groups: %s" % (repr(ret)))

    # if succeed, split groups by space
    groups = ret[0] and ret[1].split() or []
    return ret[0], groups

def sysuser_get_infos(self, username):
    """ get passwd entry for username """
    __LOG.log_d("getting infos for user %s" % (username))
    config = retrieve_config_infos(self)[1]

    fields_desc = ['username', 'password', 'uid', 'gid',
                   'infos', 'homedir', 'shell']

    passwd_content = __fapi.get_file_content(self.srv_ip,
                                             config['passwdfile'])
    for line in passwd_content.lines:
        fields = line.split(':')

        if not len(fields) == 7:
            continue

        if fields[0] == username:
            return True, dict(zip(fields_desc, fields))

    return False, None

def __check_userinfos(userinfos):
    """ check keys and values of userinfos dict """
    __scc.check_type(userinfos, dict)
    description = {
        'username': (str, True),
        'password': (str, False, None),
        'ref_user': (str, False, None),
        'uid': (str, False, None),
        'gid': (str, False, None),
        'groups': (list, False, None),
        'homedir': (str, False, None),
        'shell': (str, False, __SYSUSER_DEFAULT_SHELL),
        }
    return __scc.check_dict(userinfos, description)

def sysuser_infos(self, username):
    """ retrieve sysuser informations """
    infos = {}
    methods = ['sysuser_get_uid',
               'sysuser_get_groups']

    return infos

def sysuser_add(self, userinfos, mkgrp=False, mkhome=False):
    """ add a sysuser """
    __LOG.log_d("adding user %s" % (userinfos['username']))
    config = retrieve_config_infos(self)[1]

    userinfos = __check_userinfos(userinfos)

    bl_fields = ['ref_user', 'password', 'username']
    common_fields = [ field for field in userinfos if field not in bl_fields ]

    if userinfos['ref_user'] != None:
        ret = sysuser_get_infos(self, userinfos['ref_user'])
        if not ret[0]:
            return False, "unable to retrieve ref_user informations"
        ref_infos = ret[1]

        # retrieve ref_user's groups
        ref_groups = sysuser_get_groups(self, userinfos['ref_user'])[1]
        ref_groups.pop(0)
        ref_infos['groups'] = ref_groups

        for field in common_fields:
            if userinfos[field] == None:
                userinfos[field] = ref_infos[field]

    if userinfos['groups'] != None:
        if mkgrp:
            for group in userinfos['groups']:
                sysgroup_exists(self, group)[0] or sysgroup_add(self, group)
        userinfos['groups'] = ",".join(userinfos['groups'])

    context = {'username': userinfos['username']}
    for field in common_fields:
        context['%s_opt' % field] = ""
        if userinfos[field] != None:
            context['%s_opt' % field] = config['%s_opt' % field] % (
                {field: userinfos[field]})

    if userinfos['uid'] != None:
        context['force_uid_opt'] = config['force_uid_opt']
    else: context['force_uid_opt'] = ""

    if mkhome:
        context['mkhome_opt'] = config['mkhome_opt']
    else: context['mkhome_opt'] = ""

    ret = user_group_ctl(self, config, context)
    __LOG.log_d("user added: %s" % (repr(ret)))

    if userinfos['password'] != None:
        sysuser_set_passwd(self, userinfos['username'], userinfos['password'])

    #return ret
    return ret

def sysuser_del(self, username, purge=False):
    """ delete a system user """
    __LOG.log_d("removing user %s" % (username))
    config = retrieve_config_infos(self)[1]

    # if purge is True, use purge_opt from config
    purge_opt = purge and config['purge_opt'] or ""

    context = {
        'username': username,
        'purge_opt': purge_opt
        }
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("user removed: %s" % (repr(ret)))

    return ret

def sysgroup_exists(self, groupname):
    """ check if groupname exists """
    __LOG.log_d("checking group %s" % (groupname))
    config = retrieve_config_infos(self)[1]

    out = __fapi.file_contains(self.srv_ip,
                               "^" + groupname + ":",
                               config['groupfile'])

    __LOG.log_d("group %s exists: %s" % (groupname, not out.failed))
    return (not out.failed, out)

def sysgroup_add(self, groupname):
    """ add system group """
    __LOG.log_d("adding group %s" % (groupname))
    config = retrieve_config_infos(self)[1]

    context = {'groupname': groupname}
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("group added: %s" % (repr(ret)))

    return ret

def sysgroup_del(self, groupname):
    """ delete system group """
    __LOG.log_d("deleting group %s" % (groupname))
    config = retrieve_config_infos(self)[1]

    context = {'groupname': groupname}
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("group added: %s" % (repr(ret)))

    return ret

def sysgroup_rename(self, groupname_src, groupname_dst):
    """ rename a sysuser """
    __LOG.log_d("renamming group %s to %s" % (groupname_src, groupname_dst))
    config = retrieve_config_infos(self)[1]

    context = {
        'groupname_src': groupname_src,
        'groupname_dst': groupname_dst
        }
    ret = user_group_ctl(self, config, context)
    __LOG.log_d("group renammed: %s" % (repr(ret)))

    return ret
