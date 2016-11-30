#!/bin/bash
# newcert.sh nro crldp
KEYSIZE=4096
SCRIPTDIR=`dirname $0`
cd $SCRIPTDIR
TEMPLATES="templates/"
TEMPLDIR="${SCRIPTDIR}/../${TEMPLATES}"
NRO="${1,,}"
CRLDP="${2}"
CA_NAME="Silverbullet Server ${1^^} CA"
mkdir ${NRO}
cd $NRO
mkdir certs crl newcerts  private
SERIAL=`shuf -i 100000-999999 -n 1`
echo $SERIAL
echo $SERIAL> serial
echo '1000'> crlnumber
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
openssl genrsa -out private/root.key $KEYSIZE
openssl req -x509 -new -nodes -key private/root.key -days 7305 -out ./certs/root.pem -config ../openssl.cnf < /tmp/cert-data
h="${1,,}.hosted.eduroam.org"
mkdir servers 
openssl genrsa -out servers/$NRO.key $KEYSIZE -config ../openssl.cnf
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
sed -e "s/SSSS/$h/" -e "s/NRO/$NRO/" -e "s/CRLDP/$CRLDP/" $file >/tmp/server_cert_$NRO
openssl ca -in servers/$NRO.csr -out servers/$NRO.pem -config ../openssl.cnf -extensions server_cert -extfile /tmp/server_cert_$NRO -batch -days 1826
rm /tmp/server_cert_$NRO
openssl ca -gencrl -out crl/crl.pem -crldays 2000 -config ../openssl.cnf
