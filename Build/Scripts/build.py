#!/usr/bin/env python

""" Main script that builds ACS3 installation package.
"""


import sys
import os.path

import clean_up_pyc
import package

import os
import zipfile


# IMPORTANT
# Variables marked with !!! are mandatory and need to be set correctly before building.
# Other variables are optional.

# The kit will packaged into a folder with the name below.
# The name does not affect the kit name, it's only a a name for a folder with ACS3 installation.
FOLDER_NAME = 'AutoCharacterSystem3'

# !!! Local path to the Kit/AutoCharacterSystem folder inside Auto Character System reposityory.
# Installation will be built from this folder.
KIT_PATH = 'LocalPathToRepository\\AutoCharacterSystem\\Kit\\AutoCharacterSystem'

# !!! Path in which the ACS3 installation package will be built.
# The package is temporary, contents of that folder are deleted before each build.
# By default you can create Package folder inside Build folder of the repository as a folder with 'Package' name
# will be ignored by Github and will not be added to the repository.
PACKAGE_PATH = 'LocalPathToRepository\\RiggingSystem\\Build\\Package'

# !!! When the packaging process is complete the contents of the Package folder are zipped up and copied to that location.
# This is the final result of the build process.
DESTINATION_PATH = "LocalPath\\Release"

# Name of the ACS3 installation zip file.
ZIP_FILENAME = 'AutoCharacterSystem3.zip'


def zipdir(path, ziph):
    basepathLength = len(os.path.join(PACKAGE_PATH, FOLDER_NAME))
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            ziph.write(filepath, filepath[basepathLength:]) # zipped file will have full source file path embedded by default, we don't want that so we cut off everything before main kit folder path and pass as 2nd argument

def zipPackage():
    zipf = zipfile.ZipFile(os.path.join(DESTINATION_PATH, ZIP_FILENAME), 'w', zipfile.ZIP_DEFLATED)
    zipdir(os.path.join(PACKAGE_PATH, FOLDER_NAME), zipf)
    zipf.close()

def main():
    clean_up_pyc.cleanUpPyc(KIT_PATH, ['Scripts'])
    package.makePackage(KIT_PATH, os.path.join(PACKAGE_PATH, FOLDER_NAME))
    zipPackage()

if __name__ == '__main__':
    main()
