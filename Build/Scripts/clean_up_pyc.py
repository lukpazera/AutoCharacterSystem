#!/usr/bin/env python

""" This script cleans up given folders from .pyc files that do not have .py counterparts.

    It goes through all subdirectiories too.
"""


import os


def cleanUpPyc(path, folders):
    filesToScan = []

    # Init folders to scan.
    for folder in folders:
        fullFolderPath = os.path.join(path, folder)
        if not os.path.isdir(fullFolderPath):
            continue
        folderContent = os.listdir(fullFolderPath)
        for folderElement in folderContent:
            filesToScan.append(os.path.join(fullFolderPath, folderElement))

    count = 0
    
    print('-------- Scanning for leftover .pyc files --------')
    
    # Go through the contents.
    for element in filesToScan:
        if os.path.isdir(element):
            folderContent = os.listdir(element)
            for subfolderElement in folderContent:
                filesToScan.append(os.path.join(element, subfolderElement))

        if os.path.isfile(element):
            count += 1
            if str(element).endswith('.pyc'):
                pySourceFile = element[:-1]
                if not os.path.isfile(pySourceFile):
                    print('No equivalent py source. Deleting: %s' % element)
                    os.remove(element)           

    print('Files scanned: %d' % count)
    print(' ')
