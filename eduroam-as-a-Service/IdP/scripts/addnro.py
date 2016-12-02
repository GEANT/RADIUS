#!/usr/bin/python
import sys
import os
from shutil import move, copy, rmtree
from subprocess import call
import ConfigParser
from sb import check_nros, yn_choice, radius_restart, rm_file, nextport


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
    nrosdir = instdir + config.get('add_nro', 'nrosdir')
    templ1 = config.get('add_nro', 'templ1')
    templ2 = config.get('add_nro', 'templ2')
    templ3 = config.get('add_nro', 'templ3')
    nrosdir = config.get('add_nro', 'nrosdir')
    nrosconfig = config.get('add_nro', 'nrosconfig')
    nrossecret = config.get('add_nro', 'nrossecret')
    nrosradius = config.get('add_nro', 'nrosradius')
    nro = raw_input("NRO code or quit: ")
    nro = nro.lower()
    if nro == 'quit':
        sys.exit(0)
    ports = []
    nros = check_nros()
    port = 0
    for key in nros:
        if key == nro:
            print 'The NRO', nro, 'is already handled'
            choice = yn_choice('Do you want to delete this NRO and ' +
                               'then add a new configuration', 'n')
            if choice:
                port = nros[key]['port']
                rmtree(scriptsdir+nro)
            else:
                sys.exit(0)
        else:
            ports.append(nros[key]['port'])

    good_crldp = None
    while not good_crldp:
        crldp = raw_input("CRL Distributon Point or quit: ")
        crldp = crldp.strip()
        if crldp == 'quit':
            sys.exit(0)
        if crldp.startswith('http://') or crldp.startswith('https://'):
            while crldp.endswith('/'):
                crldp = crldp[:-1]
            crldp = crldp.replace('/', '\/')
            good_crldp = True
        else:
            print 'CRLDP must start with http:// or https://'
    if port == 0 and len(ports) > 0:
        port = nextport(ports)
    else:
        if port == 0:
            port = 5812
    print('nro: ' + nro + ', domain: ' + nro +
          '.hosted.eduroam.org' + ', port:', port)
    rm_file(sitesadir+nro)
    rm_file(sitesadir+'check-eap-tls-'+nro)
    rm_file(sitesedir+nro)
    rm_file(sitesedir+'check-eap-tls-'+nro)
    rm_file(modsadir+'eap_'+nro)
    rm_file(modsedir+'eap_'+nro)
    rm_file(proxydir+nro+'.conf')
    rm_file(certdir+nro+'.pem')
    rm_file(certdir+nro+'.key')
    rm_file(certdir+'CA-'+nro+'.pem')
    if os.path.isdir(scriptsdir+nro):
        rmtree(scriptsdir+nro)
    if os.path.isdir(nrosdir+nrosconfig+nro.upper()):
        rmtree(nrosdir+nrosconfig+nro.upper())
    if os.path.isdir(nrosdir+nrossecret+nro.upper()):
        rmtree(nrosdir+nrossecret+nro.upper())
    if os.path.isdir(nrosdir+nrosradius+nro.upper()):
        rmtree(nrosdir+nrosradius+nro.upper())
    """
       newcert.sh script creates NRO CA and NRO virtual server certificate
       certificates are available here:
       scriptsdir/nro/certs/root.pem - CA certificate
       scriptsdir/nro/servers/nro.key - server private key
       scriptsdir/nro/servers/nro.pem - server certificate
    """
    call([scriptsdir+"newcert.sh", nro, crldp])
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
    if not os.path.exists(nrosdir + nrosconfig + nro.upper()):
        os.makedirs(nrosdir + nrosconfig + nro.upper())
    if not os.path.exists(nrosdir + nrossecret + nro.upper()):
        os.makedirs(nrosdir + nrossecret + nro.upper())
    if not os.path.exists(nrosdir + nrosradius + nro.upper()):
        os.makedirs(nrosdir + nrosradius + nro.upper())

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
        copy(servercertdir + 'certs/root.pem',
             certdir + 'CA-' + nro + '.pem')
        copy(servercertdir + 'certs/root.pem',
             nrosdir + nrosconfig + nro.upper() + '/' + 'root.pem')
        copy(servercertdir + 'certs/root.pem',
             nrosdir + nrosconfig + nro.upper() + '/' + 'root.pem')
        copy(servercertdir + 'private/root.key',
             nrosdir + nrossecret + nro.upper() + '/' + 'root.key')
        copy(servercertdir + 'servers/' + nro + '.pem',
             certdir)
        copy(servercertdir + 'servers/' + nro + '.pem',
             nrosdir + nrosradius + nro.upper() + '/server.pem')
        copy(servercertdir + 'servers/' + nro + '.key',
             certdir)
        copy(servercertdir + 'servers/' + nro + '.key',
             nrosdir + nrosradius + nro.upper() + '/server.key')
        copy(servercertdir + 'crl/crl.pem',
             nrosdir + nrosconfig + nro.upper() + '/' + 'root.crl')
        """
            rehash.sh script runs c_rehash command
        """
        call([scriptsdir+"rehash.sh", certdir])
    """
        the RADIUS server must be restarted
        to read new configuration
    """
    radius_restart()

if __name__ == "__main__":
    main(sys.argv[1:])
