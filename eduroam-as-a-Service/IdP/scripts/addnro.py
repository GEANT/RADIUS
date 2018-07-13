#!/usr/bin/python
import sys
import os
from shutil import move, copy, rmtree
from subprocess import call
import ConfigParser
from sb import check_nros, yn_choice, radius_restart, rm_file


def main(argv):
    """
        define the RADIUS instalation path here
    """
    instdir = 'FR_INSTALLATION_DIRECTORY'

    scriptsdir = instdir+'scripts/'
    configfile = scriptsdir+'sb.conf'
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
    nro = False
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
    templ4 = config.get('add_nro', 'templ4')
    eapautzdir = instdir + config.get('add_nro', 'eapautzdir')
    eapauthdir = instdir + config.get('add_nro', 'eapauthdir')
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
        if args and nro in nros:
            cnt = cnt - 1
            print nro, 'skipped'
            continue
        isca = '0'
        for key in nros:
            if key == nro:
                print 'The NRO', nro, 'is already handled'
                choice = yn_choice('Do you want to delete this NRO ' +
                                   'and its server CA and then create ' +
                                   'a new CA and new configuration', 'n')
                if choice:
                    rmtree(scriptsdir+nro)
                else:
                    choice = yn_choice('Do you want to create ' +
                                       'the new server certificate ' +
                                       'for this NRO', 'n')
                    if choice:
                        isca = '1'
                    else:
                        sys.exit(0)
        good_crldp = None
        clrdp = None
        if args:
            crldp = el[1]
            good_crldp = True
        while not good_crldp:
            crldp = raw_input("CRL Distributon Point or quit: ")
            crldp = crldp.strip()
            if crldp == 'quit':
                sys.exit(0)
            if crldp.startswith('http://') or crldp.startswith('https://'):
                good_crldp = True
            else:
                print 'CRLDP must start with http:// or https://'
        while crldp.endswith('/'):
            crldp = crldp[:-1]
        crldp = crldp.replace('/', '\/')
        cnt = cnt - 1
        print('nro: ' + nro + ', domain: ' + nro +
              '.hosted.eduroam.org')
        rm_file(sitesadir+'check-eap-tls-'+nro)
        rm_file(sitesedir+'check-eap-tls-'+nro)
        rm_file(modsadir+'eap_'+nro)
        rm_file(modsedir+'eap_'+nro)
        rm_file(eapautzdir+'eap_'+nro)
        rm_file(eapauthdir+'eap_'+nro)
        if os.path.isdir(certdir+nro.upper()):
            rmtree(certdir+nro.upper())
        if isca == 0 and os.path.isdir(scriptsdir+nro):
            rmtree(scriptsdir+nro)
        if os.path.isdir(nrosdir+nrosconfig+nro.upper()):
            rmtree(nrosdir+nrosconfig+nro.upper())
        if os.path.isdir(nrosdir+nrossecret+nro.upper()):
            rmtree(nrosdir+nrossecret+nro.upper())
        if os.path.isdir(nrosdir+nrosradius+nro.upper()):
            rmtree(nrosdir+nrosradius+nro.upper())
        """
           newcert.sh script creates NRO CA and NRO virtual server certificate

           when created certificates are available here:
           scriptsdir/nro/certs/root.pem - CA certificate
           scriptsdir/nro/servers/nro.key - server private key
           scriptsdir/nro/servers/nro.pem - server certificate

           If you already have server certificate place credentials in the
           appropriate files (as indicated above) and comment out 
           following call.
        """
        call([scriptsdir+"newcert.sh", nro, crldp, isca])
        """
            create all config files
        """
        realm = nro + '.test.hosted.eduroam.org'
        esc_realm = realm.replace('.', '\\.')
        lines = []
        lines = []
        f = open(templdir + templ1 + 'nro', 'r')
        for line in f:
            lines.append(line % {'nro': nro, 'escaped_realm': esc_realm,
                                 'proc': '%'})
        f.close()
        f = open(tmpdir + templ1 + nro, 'w')
        f.write(''.join(lines))
        f.close()
        lines = []
        f = open(templdir + templ2 + 'nro', 'r')
        for line in f:
            lines.append(line % {'nro': nro, 'bignro': nro.upper(),
                                 'proc': '%'})
        f.close()
        f = open(tmpdir + templ2 + nro, 'w')
        f.write(''.join(lines))
        f.close()
        lines = []
        f = open(templdir + templ3 + 'nro', 'r')
        for line in f:
            lines.append(line % {'nro': nro})
        f.close()
        f = open(tmpdir + templ3 + nro, 'w')
        f.write(''.join(lines))
        f.close()
        lines = []
        f = open(templdir + templ4 + 'nro', 'r')
        for line in f:
            lines.append(line % {'nro': nro})
        f.close()
        f = open(tmpdir + templ4 + nro, 'w')
        f.write(''.join(lines))
        f.close()
        lines = []
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

        if os.path.isfile(tmpdir + templ1 + nro) and os.path.isdir(sitesadir):
            """
                check-eap-tls for NRO
            """
            move(tmpdir + templ1 + nro, sitesadir + templ1 + nro)
            """
                enable check-eap-tls for NRO
            """
            os.symlink(sitesadir + templ1 + nro, sitesedir + templ1 + nro)
        if os.path.isfile(tmpdir + templ2 + nro) and os.path.isdir(modsadir):
            """
                eap config for NRO
            """
            move(tmpdir + templ2 + nro, modsadir + templ2 + nro)
            """
                enable eap config for NRO
            """
            os.symlink(modsadir + templ2 + nro, modsedir + templ2 + nro)
        if os.path.isfile(tmpdir + nro + '.conf') and os.path.isdir(proxydir):
            """
                proxy config for NRO
            """
            move(tmpdir + nro + '.conf', proxydir + nro + '.conf')
        if os.path.isfile(tmpdir + templ3 + nro) and os.path.isdir(eapautzdir):
            """
                eap in authorization section for NRO
            """
            move(tmpdir+templ3+nro, eapautzdir + 'eap_' + nro)
        if os.path.isfile(tmpdir + templ4 + nro) and os.path.isdir(eapauthdir):
            """
                eap in authenticate section for NRO
            """
            move(tmpdir+templ4+nro, eapauthdir + 'eap_' + nro)
        if os.path.isdir(scriptsdir + nro):
            os.makedirs(certdir + nro.upper())
            """
               copy certificates to its destination - silverbullet certs dir
            """
            servercertdir = scriptsdir + nro + '/'
            copy(servercertdir + 'certs/root.pem',
                 nrosdir + nrosconfig + nro.upper() + '/' + 'root.pem')
            copy(servercertdir + 'private/root.key',
                 nrosdir + nrossecret + nro.upper() + '/' + 'root.key')
            copy(servercertdir + 'servers/' + nro + '.pem',
                 certdir + nro.upper())
            copy(servercertdir + 'servers/' + nro + '.pem',
                 nrosdir + nrosradius + nro.upper() + '/server.pem')
            copy(servercertdir + 'servers/' + nro + '.key',
                 certdir + nro.upper())
            copy(servercertdir + 'servers/' + nro + '.key',
                 nrosdir + nrosradius + nro.upper() + '/server.key')
            copy(servercertdir + 'crl/crl.pem',
                 nrosdir + nrosconfig + nro.upper() + '/' + 'root.crl')
    """
        the RADIUS server must be restarted
        to read new configuration
    """
    radius_restart()
    """
        what next
    """
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    print("Do not forget to adjust the FreeRADIUS configuration\n")
    print("\tremove symbolic links if they still exist:\n")
    print("\t\t" + instdir + "etc/raddb/sites-enabled/default\n")
    print("\t\t" + instdir + "etc/raddb/sites-enabled/inner-tunnel\n")
    print("\tadjust certificates settings - see all __change_it__"
          " in " + instdir + "etc/raddb/sites-enabled/tls\n")
    

if __name__ == "__main__":
    main(sys.argv[1:])
