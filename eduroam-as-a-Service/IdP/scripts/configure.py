#!/usr/bin/python
import os
import re
import sys
from shutil import move, copytree

install = raw_input("FR installation path or quit: ")
if install == 'quit':
    sys.exit(0)
if not install.endswith('/'):
        install = install + '/'
if os.path.exists(install) and os.path.isdir(install):
    print(install + 'exists')
else:
    try:
        os.makedirs(install)
    except OSError:
        print('Cannot create the instalation directory, '
              'check your permissions')
        sys.exit(1)
prefix = 'scripts/'
tmp = 'tmp/'
cnt = 0
for fname in ['sb.py', 'addnro.py', 'delnro.py', 'makelist.py']:
    if os.path.isfile(prefix + fname):
        cnt = cnt + 1
        with open(prefix + fname, 'r') as f:
            try:
                fw = open(tmp + fname, 'w')
                cnt = cnt + 1
            except:
                print('ERROR: can not open for writing ' + tmp + fname)
                continue
            for row in f:
                if 'FR_INSTALLATION_DIRECTORY' in row:
                    fw.write(row.replace('FR_INSTALLATION_DIRECTORY', install))
                else:
                    fw.write(row)
            fw.close()
    else:
        print('ERROR: ' + prefix + fname + ' not found')
if cnt == 8:
    print('Success!')
    for fname in os.listdir('.'):
        if os.path.isdir(fname):
            copytree(fname, install + fname, True)
    for fname in ['sb.py', 'addnro.py', 'delnro.py', 'makelist.py']:
        move(install + tmp + fname, install + prefix + fname)
        os.chmod(install + prefix + fname, 0755)
    print('Go to the installation directory to create NROs configuration.')
    print('Next steps:')
    print('\tcd ' + install)
    print('\t./scripts/addnro.py')
else:
    print 'Check errors'
