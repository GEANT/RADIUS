#!/usr/bin/python
import sys
import os
from sb import check_nros, yn_choice, rm_file, radius_restart
import ConfigParser
from shutil import rmtree
from subprocess import call


def main(argv):
    instdir = '/opt/tls/'

    scriptsdir = instdir+'scripts/'
    configfile = scriptsdir+'sb.conf'
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
    nro = False
    port = False
    templdir = instdir + config.get('add_nro', 'templdir')
    tmpdir = instdir + config.get('add_nro', 'tmpdir')
    sitesadir = instdir + config.get('add_nro', 'sitesadir')
    sitesedir = instdir + config.get('add_nro', 'sitesedir')
    modsadir = instdir + config.get('add_nro', 'modsadir')
    modsedir = instdir + config.get('add_nro', 'modsedir')
    proxydir = instdir + config.get('add_nro', 'proxydir')
    certdir = instdir + config.get('add_nro', 'certdir')
    nrosdir = config.get('add_nro', 'nrosdir')
    nrosconfig = config.get('add_nro', 'nrosconfig')
    nrossecret = config.get('add_nro', 'nrossecret')
    nrosradius = config.get('add_nro', 'nrosradius')
    nro = raw_input("NRO code or quit: ")
    nro = nro.lower()
    if nro == 'quit':
        sys.exit(0)
    nros = check_nros()
    if nro not in nros:
        print nro, 'is not registered, nothing to delete'
        sys.exit(0)
    choice = yn_choice('Are you sure that the NRO ' + nro +
                       ' should be deleted', 'n')
    if not choice:
        print 'Delete request was abandoned'
        sys.exit(0)
    rm_file(sitesadir+nro)
    rm_file(sitesadir+'check-eap-tls-'+nro)
    rm_file(sitesedir+nro)
    rm_file(sitesedir+'check-eap-tls-'+nro)
    rm_file(modsadir+'eap_'+nro)
    rm_file(modsedir+'eap_'+nro)
    rm_file(proxydir+nro+'.conf')
    if os.path.isdir(certdir+nro.upper()):
        rmtree(certdir+nro.upper())
    if os.path.isdir(scriptsdir+nro):
        rmtree(scriptsdir+nro)
    if os.path.isdir(nrosdir+nrosconfig+nro.upper()):
        rmtree(nrosdir+nrosconfig+nro.upper())
    if os.path.isdir(nrosdir+nrossecret+nro.upper()):
        rmtree(nrosdir+nrossecret+nro.upper())
    if os.path.isdir(nrosdir+nrosradius+nro.upper()):
        rmtree(nrosdir+nrosradius+nro.upper())
    radius_restart()
    print nro, 'deleted'

if __name__ == "__main__":
    main(sys.argv[1:])
