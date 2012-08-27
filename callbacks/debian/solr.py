"""
Specifics SolR callbacks for debian
"""

# we import as private,
# only public functions and attributes are set as callback methods
import fabric_wrp as __fapi

solr_repository = "http://archive.apache.org/dist/lucene/solr"
solr_archive_path = ""
solr_version = ""

def retrieve_version(self, version, storage_path):
    """ retrieve specific solr version from solr repository """
    ## filesystem operations callback is required
    if not hasattr(self, "fsh"):
        self.load_callbacks("fsh")

    solr_file = "apache-solr-%s.tgz" % (version)
    solr_path = "%s/%s" % (version, solr_file)
    out = self.fsh.wget_file("%s/%s" % (solr_repository, solr_path),
                             "%s/%s" % (storage_path.rstrip('/'), solr_file),
                             use_sudo = True)

    self.solr_version = version
    self.solr_archive_path = "%s/%s" % (storage_path.rstrip('/'), solr_file)

    return (not out.failed, out)

def deploy_war_file(self, destdir, warfile = None):
    """ deploy SolR war file in destination directory """
    ## filesystem operations callback is required
    if not hasattr(self, "fsh"):
        self.load_callbacks("fsh")

    if warfile == None:
        warfile_path = "apache-solr-%s/dist" % (self.solr_version)
        warfile = "%s/apache-solr-%s.war" % (warfile_path, self.solr_version)

    tmp_path = "/tmp"

    out = self.fsh.tar_extract(self.solr_archive_path, tmp_path, [warfile],
                               use_sudo = True)
    if out.failed is True:
        return (not out.failed, out)

    out = self.fsh.move_file("%s/%s" % (tmp_path, warfile), destdir,
                             use_sudo = True)
    if out.failed is True:
        return (not out.failed, out)

    out = self.fsh.remove_file("%s/%s" % (tmp_path, warfile.split('/')[0]),
                               recursive = True, use_sudo = True)
    return (not out.failed, out)

def deploy_solr_config(self, destdir, cfg_archive = None):
    """ extract configuration from archive to destination directory """
    pass

def set_solr_home(self, home_path, javaopts_file):
    """ set solr home environment variable in file containing java_opts """
    ## filesystem operations callback is required
    if not hasattr(self, "fsh"):
        self.load_callbacks("fsh")

    self.solr_home = home_path
    self.solr_config = "%s/conf" % (home_path)
    self.solr_data = "%s/data" % (home_path)
    home_javaopt = '-Dsolr.solr.home=%s' % (self.solr_home)

    out = self.fsh.sed_file(javaopts_file, '^JAVA_OPTS="(.*)"',
                            'JAVA_OPTS="\\1 %s"' % (home_javaopt))
    if out.failed is True:
        return (not out.failed, out)

    out = self.fsh.make_dir("%s/{conf,data}" % (home_path), use_sudo = True)
    if out.failed is True:
        return (not out.failed, out)

    out = self.fsh.chown_file(home_path, "tomcat6", "tomcat6",
                              recursive = True)
    if out.failed is True:
        return (not out.failed, out)

    out = self.fsh.symlink("%s/conf" % (home_path), "/etc/tomcat6/solr",
                           use_sudo = True)

    return (not out.failed, out)
