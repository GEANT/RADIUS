This directory contains scripts used to extend the RADIUS-TLS configuration
for a new NRO.

The main tool - addnro.py script creates the configuration files 
for a new NRO and adds them to the RADIUS-TLS configuration.
Requires two parameters: a NRO code and port number for
virtual server. Each NRO must be assigned a different port number.
Future versions of the system may be expanded to acquire the port number
automatically.
The addnro.py calls newcert.sh script to create NRO CA and server certificate.
This call can be skipped if cerificates are created in an another
way. In this case put certificates in the following location:
1. NRO CA certificate - `scriptsdir`/`nro_code`/certs/rootCA.pem
2. server certificate - `scriptsdir`/`nro_code`/certs/nro_code.pem
3. server private key - `scriptsdir/`nro_code`/private/nro_code.key
New certificates are copied to the Silverbullet certificates directory and
then c_rehash command is run in this directory.
Finally the RADIUS server is restarted.

To add a new NRO run e.g.

/opt/tls/scripts/addnro.py --nro=pl --port=5812


