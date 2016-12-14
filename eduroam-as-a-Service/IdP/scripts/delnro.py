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
    eapautzdir = instdir + config.get('add_nro', 'eapautzdir')
    eapauthdir = instdir + config.get('add_nro', 'eapauthdir')
    certdir = instdir + config.get('add_nro', 'certdir')
    nrosdir = config.get('add_nro', 'nrosdir')
    nrosconfig = config.get('add_nro', 'nrosconfig')
    nrossecret = config.get('add_nro', 'nrossecret')
    nrosradius = config.get('add_nro', 'nrosradius')
    try:
        if sys.argv[1]:
            args = True
            arg = sys.argv[1]
            rows = []
            if os.path.isfile(arg):
                with open(arg, 'r') as argfile:
                    for row in argfile:
                        rows.append(row.rstrip())
            else:
                print 'Input file does not exists, the script will run ' + \
                      'interactively'
                args = False
    except:
        args = False
    if args:
        cnt = len(rows)-1
    else:
        cnt = 0
    while cnt >= 0:
        if not args:
            nro = raw_input("NRO code or quit: ")
            nro = nro.lower()
            if nro == 'quit':
                sys.exit(0)
        else:
            el = rows[cnt].split()
            nro = el[0].lower()
        nros = check_nros()
        if nro not in nros:
            print nro, 'is not registered, nothing to delete'
            cnt = cnt - 1
            continue
        if not args:
            choice = yn_choice('Are you sure that the NRO ' + nro +
                               ' should be deleted', 'n')
            if not choice:
                print 'Delete request was abandoned'
                cnt = cnt - 1
                continue
        rm_file(sitesadir+'check-eap-tls-'+nro)
        rm_file(sitesedir+'check-eap-tls-'+nro)
        rm_file(modsadir+'eap_'+nro)
        rm_file(modsedir+'eap_'+nro)
        rm_file(proxydir+nro+'.conf')
        rm_file(eapautzdir+'eap_'+nro)
        rm_file(eapauthdir+'eap_'+nro)
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
        cnt = cnt - 1

if __name__ == "__main__":
    main(sys.argv[1:])
