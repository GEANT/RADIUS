### eduroam-as-a-Service - IdP tools

#### Howto start
Download the latest stable freeRADIUS version, compile and install.

Fetch this git content.

Run the configuration script to initialize a target directory structure:
```
cd RADIUS/eduroam-as-a-Service/IdP
.\scripts\configure.py
```
Then follow instructions on screen.

#### About this directory

* **etc** subdirectory contains files for FreeRADIUS configuration

* **scripts** subdirectory contains scripts to add a new NRO

* **templates** subdirectory contains template files

Files from **etc/raddb** subdirectory will go to the RADIUS-TLS configuration.

Make sure that *default* and *inner-tunnel* sites are not enabled in your configuration. 



