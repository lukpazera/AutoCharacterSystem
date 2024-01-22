

import os
import shutil
import collections

import rs


def cleanPyc(paths):
    if paths is None or not paths:
        return
    
    files = []
    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for f in filenames:
                files.append(os.path.join(dirpath, f))

    pycFiles = []
    for filename in files:
        if filename.endswith('.pyc'):
            rs.log.out('Removing pyc file: %s' % filename)
            os.remove(filename)


