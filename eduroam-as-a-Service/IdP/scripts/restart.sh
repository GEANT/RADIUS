#!/bin/bash
RADIUSDPID=/opt/tls/var/run/radiusd/radiusd.pid
#if [ `ps -ef|grep radiusd|grep fxx` ]
if [ -f $RADIUSDPID ]
then
        echo 'not debug'
else
        echo 'debug'
        pkill -9 radiusd
fi
/opt/tls/sbin/radiusd -d /opt/tls/etc/raddb
