#!/usr/bin/python
import sys
from sb import check_nros, nextport


def main(argv):
    nros = check_nros()
    ports = []
    for key in nros:
        print key, '-', 'port ' + str(nros[key]['port']) + \
            ('', '')[nros[key]['status']]
        ports.append(nros[key]['port'])
    print 'Next port to use:', nextport(ports)

if __name__ == "__main__":
    main(sys.argv[1:])
