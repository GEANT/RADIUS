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
    srcfile = ''
    dstfile = ''
    if len(sys.argv) > 1:
        crldp = sys.argv[1]
    if len(sys.argv) < 3:
        srcfile = nrofile
    else:
        srcfile = sys.argv[2]
    print crldp
    if crldp != '':
        if (crldp.strip().startswith('http://') or \
            crldp.strip().startswith('https://')):
                good_crldp = True
    if not good_crldp:
        while not good_crldp:
            crldp = raw_input("CRL Distributon Point or quit or help: ")
            crldp = crldp.strip()
            if crldp == 'quit':
                sys.exit(0)
            if crldp == 'help':
                print('Usage: makelist.py [arg1 [arg2]]')
                print('no arguments:\tasks for CRL Distribution Point '
                      'and uses templates/known_nros as source file')
                print('one argument:\tCRL Distribution Point')
                print('two arguments:\tCRL Distribution Point and source file with NRO codes')
                sys.exit(0)
            if crldp.startswith('http://') or crldp.startswith('https://'):
                good_crldp = True
            else:
                print 'CRLDP must start with http:// or https://'
    if not crldp.endswith('/'):
        crldp = crldp + '/'
    print "CRLDP:", crldp
    if os.path.isfile(srcfile):
        with open(srcfile, 'r') as f:
           print 'source file:', srcfile
           dstfile = templdir + 'nros_file'
           print 'destination file:', dstfile
           fw = open(dstfile, 'w')
           for row in f:
               fw.write(row.rstrip() + ' ' + crldp + row.rstrip() + '/crl/root.crl\n')
           fw.close()

if __name__ == "__main__":
    main(sys.argv[1:])
