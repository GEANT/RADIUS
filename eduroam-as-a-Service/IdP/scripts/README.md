### Silverbullet Managed IdP tools

This directory contains scripts used to create the RADIUS-TLS configuration
for a new NRO.

####addnro.py script
This script creates the configuration files 
for a new NRO and adds them to the RADIUS-TLS configuration.
The script can be called in two ways:
1. without command line arguments - interactive run is started
  - the script prompts for a NRO code
  - the configuration for this NRO is created
  - when this NRO already exists it can be replaced by a new instance
2. with a file as the first argument 
  - it is assumed that this file contains data for bulk loading in the following format:
```
NRO_code CRL_Distribution_Point_URL 
```

The addnro.py calls **newcert.sh** script to create NRO CA and server certificate.
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
It prompts for the NRO code or can be calld with a file as the first argument to
do bulk deleting. The file contains NRO codes (one per line).

The shownro.py script lists configured NROs and its RADIUS-TLS ports.

The sb.py contains functions used by scripts described above.
