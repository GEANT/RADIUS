### eduroam-as-a-Service - IdP tools

This directory contains config files for RADIUS-TLS.

* **etc** subdirectory contains files for FreeRADIUS configuration

* **scripts** subdirectory contains scripts to add a new NRO

* **templates** subdirectory contains template files

Copy files from **etc/raddb** subdirectory to the RADIUS-TLS configuration.

Go to the FreeRADIUS installation tree and remove *default* and *inner-tunnel* from *etc/raddb/sites-enabled*.

Copy **scripts** and **templates** subdirectory to the RADIUS-TLS installation directory.


