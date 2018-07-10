#!/usr/bin/python
import os
import re
import ConfigParser
import dbus
from subprocess import call


def radius_restart():
    sysbus = dbus.SystemBus()
    systemd1 = sysbus.get_object('org.freedesktop.systemd1',
                                 '/org/freedesktop/systemd1')
    manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
    job = manager.RestartUnit('radiusd.service', 'fail')


def yn_choice(msg, default='y'):
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = raw_input("%s (%s) " % (msg, choices))
    values = ('y', 'yes', '') if choices == 'Y/n' else ('y', 'yes')
    return choice.strip().lower() in values


def check_nros():
    """
        define the RADIUS instalation path here
    """
    instdir = 'FR_INSTALLATION_DIRECTORY'
    scriptsdir = instdir+'scripts/'
    configfile = scriptsdir+'sb.conf'
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
    proxydir = instdir + config.get('add_nro', 'proxydir')
    sitesadir = instdir + config.get('add_nro', 'sitesadir')
    sitesedir = instdir + config.get('add_nro', 'sitesedir')
    modsadir = instdir + config.get('add_nro', 'modsadir')
    modsedir = instdir + config.get('add_nro', 'modsedir')
    certdir = instdir + config.get('add_nro', 'certdir')
    nros = {}
    for file in os.listdir(proxydir):
        name = file.replace('.conf', '')
        if name == 'README':
            continue
        if os.path.isfile(sitesadir+name) and \
                os.path.isfile(sitesedir+name) and \
                os.path.isfile(sitesadir+'check-eap-tls-'+name) and \
                os.path.isfile(sitesedir+'check-eap-tls-'+name) and \
                os.path.isfile(modsadir+'eap_'+name) and \
                os.path.isfile(modsedir+'eap_'+name) and \
                os.path.isfile(certdir+name+'.pem') and \
                os.path.isfile(certdir+'CA-'+name+'.pem'):
            nrotype = 'local'
        nros[name] = {'status': True}
    return nros


def rm_file(f):
    """
        delete file
    """
    try:
        os.remove(f)
    except:
        pass
