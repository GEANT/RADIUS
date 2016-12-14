#!/usr/bin/python
import sys
from sb import check_nros


def main(argv):
    nros = check_nros()
    for key in nros:
        print key

if __name__ == "__main__":
    main(sys.argv[1:])
