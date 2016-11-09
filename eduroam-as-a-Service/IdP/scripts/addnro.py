#!/usr/bin/python
import sys
import getopt
import os
from shutil import move, copy
from subprocess import call
import dbus
import ConfigParser

"""
   Creates the configuration files for a new NRO and
   adds them to the RADIUS-TLS configuration.
   Requires two parameters: a NRO code and port number for
   virtual server. The port number must be unique.
   Calls newcert.sh script to create NRO CA and server certificate.
   This script can be skipped if cerificates are created in an another
   way. In this case put certificates in the following location:
   1. NRO CA certificate - scriptsdir/`nro_code`/certs/rootCA.pem
   2. server certificate - scriptsdir/`nro_code`/certs/nro_code.pem
   3. server private key - scriptsdir/`nro_code`/private/nro_code.key
   Puts certificates to the Silverbullet certificates directory and
   runs c_rehash command in this directory/
   Finally the RADIUS server is restarted.
"""

def main(argv):
    """
        define the RADIUS instalation path here
    """
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
    templ1 = config.get('add_nro', 'templ1')
    templ2 = config.get('add_nro', 'templ2')
    templ3 = config.get('add_nro', 'templ3')
    try:
        opts, args = getopt.getopt(argv, "",
                                   ["help", "nro=", "port="])
    except getopt.GetoptError:
        print('addnro.py --nro=nro_code --port=radius_port')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--help':
            print('addnro.py --nro=nro_code --port=radius_port')
            sys.exit(2)
        elif opt in ("--nro"):
            nro = arg.lower()
        elif opt in ("--port"):
            port = int(arg)
    if not nro or not port:
        print('addnro.py --nro=nro_code --port=radius_port')
        sys.exit(2)
    print('nro: ' + nro + ', domain: ' + nro +
          '.hosted.eduroam.org' + ', port:', port)
    """
       newcert.sh script creates NRO CA and NRO virtual server certificate
       certificates are available here:
       scriptsdir/`nro_code`/certs/rootCA.pem - CA certificate
       scriptsdir/`nro_code`/servers/`nro_code`.key - server private key
       scriptsdir/`nro_code`/servers/`nro_code`.pem - server certificate
    """
    call([scriptsdir+"newcert.sh", nro])
    """
        create all config files
    """
    realm = nro + '.hosted.eduroam.org'
    esc_realm = realm.replace('.', '\\.')
    port2 = port + 1
    lines = []
    f = open(templdir+templ1, 'r')
    for line in f:
        lines.append(line % {'nro': nro, 'escaped_realm': esc_realm,
                             'port_auth': port, 'port_acct': port2})
    f.close()
    f = open(tmpdir+nro, 'w')
    f.write(''.join(lines))
    f.close()
    lines = []
    f = open(templdir + templ2 + 'nro', 'r')
    for line in f:
        lines.append(line % {'nro': nro, 'escaped_realm': esc_realm,
                             'proc': '%'})
    f.close()
    f = open(tmpdir + templ2 + nro, 'w')
    f.write(''.join(lines))
    f.close()
    lines = []
    f = open(templdir + templ3 + 'nro', 'r')
    for line in f:
        lines.append(line % {'nro': nro, 'proc': '%'})
    f.close()
    f = open(tmpdir + templ3 + nro, 'w')
    f.write(''.join(lines))
    f.close()
    lines = []
    f = open(templdir + 'nro.conf', 'r')
    for line in f:
        lines.append(line % {'nro': nro, 'escaped_realm': esc_realm})
    f.close()
    f = open(tmpdir + nro + '.conf', 'w')
    f.write(''.join(lines))
    f.close()
    """
        move config files to its destination
    """
    if os.path.isfile(tmpdir + nro) and os.path.isdir(sitesadir):
        """
            new virtual server for NRO
        """
        move(tmpdir + nro, sitesadir)
        """
            enable new virtual server
        """
        os.symlink(sitesadir + nro, sitesedir + nro)
    if os.path.isfile(tmpdir + templ2 + nro) and os.path.isdir(sitesadir):
        """
            check-eap-tls for NRO
        """
        move(tmpdir + templ2 + nro, sitesadir)
        """
            enable check-eap-tls for NRO
        """
        os.symlink(sitesadir + templ2 + nro, sitesedir + templ2 + nro)
    if os.path.isfile(tmpdir + templ3 + nro) and os.path.isdir(modsadir):
        """
            eap config for NRO
        """
        move(tmpdir + templ3 + nro, modsadir)
        """
            enable eap config for NRO
        """
        os.symlink(modsadir + templ3 + nro, modsedir + templ3 + nro)
    if os.path.isfile(tmpdir + nro + '.conf') and os.path.isdir(proxydir):
        """
            proxy config for NRO
        """
        move(tmpdir+nro+'.conf', proxydir)
    if os.path.isdir(scriptsdir + nro) and os.path.isdir(certdir):
        """
           copy certificates to its destination - silverbullet certs dir
        """
        servercertdir = scriptsdir + nro + '/'
        copy(servercertdir + 'certs/rootCA.pem',
             certdir + 'CA-' + nro + '.pem')
        copy(servercertdir + 'servers/' + nro + '.pem',
             certdir)
        copy(servercertdir + 'servers/' + nro + '.key',
             certdir)
        """
            rehash.sh script runs c_rehash command
        """
        call([scriptsdir+"rehash.sh", certdir])
    """
        the RADIUS server must be restarted
        to read new configuration
    """
    sysbus = dbus.SystemBus()
    systemd1 = sysbus.get_object('org.freedesktop.systemd1',
                                 '/org/freedesktop/systemd1')
    manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
    job = manager.RestartUnit('radiusd.service', 'fail')

if __name__ == "__main__":
    main(sys.argv[1:])
