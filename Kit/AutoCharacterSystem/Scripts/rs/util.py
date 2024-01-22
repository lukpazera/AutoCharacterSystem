

import sys
import time

import modox
from .log import log


def getPythonMajorVersion():
    return sys.version_info[0]


def run(cmdString, logErrors=True):
    return modox.run(cmdString, logErrors, log)


def getTime():
    if getPythonMajorVersion() > 2:
        return time.perf_counter()
    else:
        return time.clock()

