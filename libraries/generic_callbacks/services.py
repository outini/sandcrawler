"""
Generic callbacks for services
"""

# we import as private
import sc_logs as __LOG
import fabric_wrp as __fapi
import sc_config as __config

__services_configfile = "conf.d/services.conf"

def retrieve_config_infos(self, service_name, action):
    """ retrieve configuration informations for service_name/action """
    config_dict = dict()
    config = __config.get_config(__services_configfile, self.systemtype)

    # trying service specific configuration, or falling back to GENERIC
    # no specific nor generic section found, nothing can be done
    (section_name, section_content) = config.get_section(service_name,
                                                         default = "GENERIC")
    if section_content == None:
        __LOG.log_c("service not defined and GENERIC section not found")
        return None

    # sudo usage to do action on service name
    config_dict['use_sudo'] = config.getopt(section_name,
                                            ['use_sudo'], default = False,
                                            vartype="boolean")

    # pre action command to run (specific -> generic -> None)
    config_dict['pre'] = config.getopt(section_name,
                                       ['pre_%s' % (action), 'pre'])

    # action command to run (required)
    config_dict['cmd'] = config.getopt(section_name,
                                       ['cmd_%s' % (action), 'cmd'])

    # post action command to run (specific -> generic -> None)
    config_dict['post'] = config.getopt(section_name,
                                        ['post_%s' % (action), 'post'])

    # fallback action command to run (specific -> generic -> None)
    config_dict['fallback'] = config.getopt(section_name,
                                            ['fallback_%s' % (action),
                                             'fallback'])

    return config_dict

def srvctl(self, service_name, action):
    """
    control lambda services based on config files

    srvctl( str(service_name), str(action) )
    return: tupple( bool(), object/None)
    """
    __LOG.log_d("action '%s' on service %s" % (action, service_name))
    config = retrieve_config_infos(self, service_name, action)
    if config is None:
        __LOG.log_c("action '%s' on service %s aborted" % (action,
                                                           service_name))
        return False

    context = {
        'service_name': service_name,
        'action': action,
        'step': None
        }

    fapiexec = config['use_sudo'] and __fapi.sudo or __fapi.run

    if config['pre'] is not None:
        context.update({'step': 'pre'})
        run = config['pre'] % (context)
        out = fapiexec(self.srv_ip, run, nocheck=True)
        __LOG.log_d('pre out: %s' % (out))
        if out.failed:
            __LOG.log_c('pre command failed: %s' % (run))
            __LOG.log_c('output message: %s' % (out))
            if config['fallback'] != None:
                out = fapiexec(self.srv_ip, config['fallback'] % (context))
                __LOG.log_d('fallback out: %s' % (out))
            return not out.failed

    context.update({'step': 'cmd'})
    run = config['cmd'] % (context)
    out = fapiexec(self.srv_ip, run, nocheck=True)
    __LOG.log_d('cmd out: %s' % (out))
    if out.failed:
        __LOG.log_c('command failed: %s' % (run))
        __LOG.log_c('output message: %s' % (out))
        if config['fallback'] is not None:
            out = fapiexec(self.srv_ip, config['fallback'] % (context))
            __LOG.log_d('fallback out: %s' % (out))
        return not out.failed

    if config['post'] is not None:
        context.update({'step': 'post'})
        run = config['post'] % (context)
        out = fapiexec(self.srv_ip, run, nocheck = True)
        __LOG.log_d('post out: %s' % (out))
        if out.failed:
            __LOG.log_c('post command failed: %s' % (run))
            __LOG.log_c('output message: %s' % (out))
            if config['fallback'] is not None:
                out = fapiexec(self.srv_ip, config['fallback'] % (context))
                __LOG.log_d('fallback out: %s' % (out))
            return (not out.failed, out)

    return True

def start(self, service_name):
    """ wrapper to start lambda services """
    return srvctl(self, service_name, "start")

def stop(self, service_name):
    """ wrapper to stop lambda services """
    return srvctl(self, service_name, "stop")
