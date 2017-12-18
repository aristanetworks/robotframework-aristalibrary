#!/usr/bin/env python

import sys
import os

from robot.libdoc import libdoc

ROOT = os.path.normpath(os.path.join(os.path.abspath(__file__), '..', '..'))
#sys.path.insert(0, os.path.join(ROOT))

if __name__ == '__main__':
    ipath = os.path.join(ROOT, 'AristaLibrary', 'AristaLibrary.py')
    opath = os.path.join(ROOT, 'docs', 'AristaLibrary.html')
    try:
        libdoc(ipath, opath)
    except (IndexError, KeyError):
        print __doc__

    ipath = os.path.join(ROOT, 'AristaLibrary', 'Expect.py')
    opath = os.path.join(ROOT, 'docs', 'Expect.html')
    try:
        libdoc(ipath, opath)
    except (IndexError, KeyError):
        print __doc__
