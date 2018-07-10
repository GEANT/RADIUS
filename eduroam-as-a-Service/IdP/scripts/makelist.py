#!/usr/bin/python
import sys
import os
from shutil import move, copy, rmtree
from subprocess import call
import ConfigParser


def main(argv):
    """
        define the RADIUS instalation path here
    """
    instdir = 'FR_INSTALLATION_DIRECTORY'
    scriptsdir = instdir+'scripts/'
    configfile = scriptsdir+'sb.conf'
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
    templdir = instdir + config.get('add_nro', 'templdir')
    nrofile = templdir + 'known_nros'
    good_crldp = False
    crldp = ''
    try:
        crldp = sys.argv[1]
        if (crldp.strip().startswith('http://') or \
            crldp.strip().startswith('https://')):
                good_crldp = True
    except:
        pass
    if not good_crldp:
        while not good_crldp:
            crldp = raw_input("CRL Distributon Point or quit: ")
            crldp = crldp.strip()
            if crldp == 'quit':
                sys.exit(0)
            if crldp.startswith('http://') or crldp.startswith('https://'):
                good_crldp = True
            else:
                print 'CRLDP must start with http:// or https://'
    if not crldp.endswith('/'):
        crldp = crldp + '/'
    if os.path.isfile(nrofile):
        with open(nrofile, 'r') as f:
           for row in f:
               print row.rstrip(), crldp + row.rstrip() + '.der'

if __name__ == "__main__":
    main(sys.argv[1:])
