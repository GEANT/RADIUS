This directory contains scripts used to extend the RADIUS-TLS configuration
for a new NRO.

The main tool - addnro.py script creates the configuration files 
for a new NRO and adds them to the RADIUS-TLS configuration.
The script is interactive. It prompts for the NRO code.
When this NRO already exists it can be replaced by a new instance.
The port for virtual server of the new NRO is acquired automatically.

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

The delnro.py script allows to remove a NRO wrom the RADIS-TLS configuration.
It prompts for the NRO code.

The shownro.py script lists configured NROs and its RADIUS-TLS ports.

The sb.py contains functions used by scripts described above.
