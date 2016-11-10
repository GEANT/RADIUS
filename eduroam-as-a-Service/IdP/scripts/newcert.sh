#!/bin/bash
# newcert.sh nro
SCRIPTDIR=`dirname $0`
cd $SCRIPTDIR
TEMPLATES="templates/"
TEMPLDIR="${SCRIPTDIR}/../${TEMPLATES}"
NRO="${1,,}"
CA_NAME="Silverbullet Server ${1^^} CA"
mkdir ${NRO}
cd $NRO
mkdir certs crl newcerts  private
echo "1000"> serial
touch index.txt
echo "unique_subject = no">index.txt.attr
Country=EU
Organization=GEANT
OrganizationalUnit=Silverbullet
Email=" "
echo $Country > /tmp/cert-data
echo $Organization >> /tmp/cert-data
echo $OrganizationalUnit >> /tmp/cert-data
echo $CA_NAME >> /tmp/cert-data
echo $Email >> /tmp/cert-data
openssl genrsa -out private/rootCA.key 2048
openssl req -x509 -new -nodes -key private/rootCA.key -days 7305 -out ./certs/rootCA.pem -config ../openssl.cnf < /tmp/cert-data
h="${1,,}.hosted.eduroam.org"
mkdir servers 
openssl genrsa -out servers/$NRO.key 2048 -config ../openssl.cnf
Host="$h"
echo $Host
echo $Country > /tmp/cert-data
echo $Organization >> /tmp/cert-data
echo $OrganizationalUnit >> /tmp/cert-data
echo $Host >> /tmp/cert-data
echo $Email >> /tmp/cert-data
openssl req -new -key servers/$NRO.key -out servers/$NRO.csr -config ../openssl.cnf < /tmp/cert-data
sdir=`pwd`
file="${TEMPLDIR}server_cert"
sed "s/SSSS/$h/;" $file >/tmp/server_cert
openssl ca -in servers/$NRO.csr -out servers/$NRO.pem -config ../openssl.cnf -extensions server_cert -extfile /tmp/server_cert -batch -days 1826