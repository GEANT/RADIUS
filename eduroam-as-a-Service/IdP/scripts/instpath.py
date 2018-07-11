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
cnt = 0;
for fname in ['sb.py', 'addnro.py', 'delnro.py', 'makelist.py']:
    if os.path.isfile(prefix + fname):
       cnt = cnt + 1
       with open(prefix + fname, 'r') as f:
           try:
               fw = open(tmp + fname, 'w')
               cnt = cnt + 1
           except:
               print 'ERROR: can not open for writing', tmp + fname    
               continue
           for row in f:
               if 'FR_INSTALLATION_DIRECTORY' in row:
                   fw.write(row.replace('FR_INSTALLATION_DIRECTORY', install))
               else:
                   fw.write(row)
           fw.close()
           try:
               move(tmp + fname, prefix + fname)
               cnt = cnt + 1
           except IOError:
               print 'ERROR:', 'move ' + tmp + fname, 'to', prefix + fname, 'failed'
               continue
           os.chmod(prefix + fname, 0755)
    else:
        print 'ERROR: ' + prefix + fname, 'not found'
if cnt == 12:
    print 'Success!'
else:
    print 'Check errors'
   

