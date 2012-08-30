# -*- coding: iso-latin-1 -*-
"""
Specifics SolR callbacks for debian
"""

__docformat__ = 'restructuredtext en'
__author__ = "Denis 'jawa' Pompilio"
__credits__ = "Denis 'jawa' Pompilio"
__license__ = "GPLv3"
__maintainer__ = "Denis 'jawa' Pompilio"
__email__ = "denis.pompilio@gmail.com"
__status__ = "Development"

solr_repository = "http://archive.apache.org/dist/lucene/solr"
solr_archive_path = ""
solr_version = ""

def retrieve_version(self, version, storage_path):
    """
    Retrieve specific solr version from solr repository
    The default used repository is from apache:
        http://archive.apache.org/dist/lucene/solr

    Arguments:
        str(version)        The version of SolR available on repository
        str(storage_path)   The path in which retrieved archive will be stored

    This method return a tuple containing:
        the return boolean
        the fabric api execution object
    """
    ## filesystem operations callback is required
    if not hasattr(self.trk, "fsh"):
        self.trk.load_callbacks("fsh")

    storage_path = storage_path.rstrip('/')

    solr_file = "apache-solr-%s.tgz" % (version)
    solr_path = "%s/%s" % (version, solr_file)
    out = self.trk.fsh.wget_file("%s/%s" % (solr_repository, solr_path),
                                 "%s/%s" % (storage_path, solr_file),
                                 use_sudo = True)

    self.solr_version = version
    self.solr_archive_path = "%s/%s" % (storage_path, solr_file)

    return (not out.failed, out)


def deploy_war_file(self, destdir, warfile = None):
    """
    Deploy SolR war file in destination directory
    Warfile is took from the SolR archive

    Arguments:
        str(destdir)        The destination directory for warfile
        str(warfile)        The warfile to extract from SolR archive
                            If None, default warfile is used.

    The default SolR warfile used from the archvie is (%s is the SolR version):
        apache-solr-%s/dist/apache-solr-%s.war

    This method return a tuple containing:
        the return boolean
        the fabric api execution object
    """
    ## filesystem operations callback is required
    if not hasattr(self.trk, "fsh"):
        self.trk.load_callbacks("fsh")

    if warfile == None:
        warfile_path = "apache-solr-%s/dist" % (self.solr_version)
        warfile = "%s/apache-solr-%s.war" % (warfile_path, self.solr_version)

    tmp_path = "/tmp"

    out = self.trk.fsh.tar_extract(self.solr_archive_path, tmp_path,
                                   [warfile], use_sudo = True)
    if out.failed is True:
        return (not out.failed, out)

    out = self.trk.fsh.move_file("%s/%s" % (tmp_path, warfile), destdir,
                                 use_sudo = True)
    if out.failed is True:
        return (not out.failed, out)

    out = self.trk.fsh.remove_file("%s/%s" % (tmp_path, warfile.split('/')[0]),
                                   recursive = True, use_sudo = True)
    return (not out.failed, out)


def set_solr_home(self, home_path, javaopts_file):
    """
    Set solr home environment variable in file containing java_opts
    This method is useful while using tomcat environnement.

    Arguments:
        str(home_path)        The home directory of SolR
        str(javaopts_file)    The file used for JAVA suplementary options
                              (match is done on: ^JAVA_OPTS=".*")

    This method return a tuple containing:
        the return boolean
        the fabric api execution object
    """
    ## filesystem operations callback is required
    if not hasattr(self.trk, "fsh"):
        self.trk.load_callbacks("fsh")

    self.solr_home = home_path
    self.solr_config = "%s/conf" % (home_path)
    self.solr_data = "%s/data" % (home_path)
    home_javaopt = '-Dsolr.solr.home=%s' % (self.solr_home)

    out = self.trk.fsh.sed_file(javaopts_file, '^JAVA_OPTS="(.*)"',
                                'JAVA_OPTS="\\1 %s"' % (home_javaopt))
    if out.failed is True:
        return (not out.failed, out)

    out = self.trk.fsh.make_dir("%s/{conf,data}" % (home_path),
                                use_sudo = True)
    if out.failed is True:
        return (not out.failed, out)

    out = self.trk.fsh.chown_file(home_path, "tomcat6", "tomcat6",
                                  recursive = True)
    if out.failed is True:
        return (not out.failed, out)

    out = self.trk.fsh.symlink("%s/conf" % (home_path), "/etc/tomcat6/solr",
                               use_sudo = True)

    return (not out.failed, out)
