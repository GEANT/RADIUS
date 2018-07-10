#!/usr/bin/python
import os
import re
import sys
from shutil import move

prefix = 'scripts/'
tmp = 'tmp/'
install = raw_input("FR installation path or quit: ")
if install == 'quit':
    sys.exit(0)
if not install.endswith('/'):
        install = install + '/'
for fname in ['sb.py', 'addnro.py', 'delnro.py', 'makelist.py']:
    if os.path.isfile(prefix + fname):
       with open(prefix + fname, 'r') as f:
           fw = open(tmp + fname, 'w')
           for row in f:
               if 'FR_INSTALLATION_DIRECTORY' in row:
                   fw.write(row.replace('FR_INSTALLATION_DIRECTORY', install))
               else:
                   fw.write(row)
           fw.close()
           move(tmp + fname, prefix + fname)
           os.chmod(prefix + fname, 0755)

