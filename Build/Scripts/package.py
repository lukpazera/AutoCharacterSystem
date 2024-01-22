#!/usr/bin/env python

""" Creates ACS3 package inside a given folder.
"""

import os
import shutil
import collections


# SRC defines all the folders for the package together with extensions of compatible files
# or even specific files directly.
# Subfolders are not scanned by default so all subfolders have to be added manually.

# Syntax:
#
# SRC[folder_name] = [file_extension, filename]
# You can either put file_extension like '.pyc' to get all files with this extension or put full filename
# to get particular files copied over only.
# If the value list for SRC entry is empty this folder will simply be skipped.
#
# SRC[folder_name/subfolder_name] = [file_extension, filename]
# You can add subfolders but you have to add parent folder as separate entry first.
# This is because if parent folder does not exist the subfolder will not be created correctly.
# Parent folder can added using empty value entry if there are no files to copy in parent folder:
# SRC[parent_folder] = []
#
# SRC['Temp_Template'] = {'Temp': ['.txt']}
# If value is a dictionary rathen then list a source folder will be renamed to the name of the first
# key in the dictionary. The value is then parsed in the same way (file extension or file name).
# This allows for renaming the copied folder on the fly.

# SRC[foldername] = ['emptyDir.txt']
# If you want to have an empty folder in the installed kit (such as Temp folder) then
# put a file in the folder named exactly as above.
# When creating packing contents into lpk all folders with emptyDir.txt in them will be
# added as empty folders, the emptyDir.txt file will not be copied.


def initData():
    SRC = collections.OrderedDict()
    SRC['_main'] = ['.cfg'] # kit index file
    SRC['Configs'] = ['.CFG', '.disabled'] # disabled is for disabled config files that can be enabled from within MODO.
    SRC['Configs/icons'] = ['.png']

    # This is required to create empty folder.
    SRC['ExtraStartup'] = ['.cfg']

    SRC['ExtraStartup/Extra'] = []
    SRC['ExtraStartup/Extra/mac'] = ['.lx']
    SRC['ExtraStartup/Extra/win64'] = ['.lx']

    SRC['ExtraStartup/ExtraPre17'] = []
    SRC['ExtraStartup/ExtraPre17/mac'] = ['.lx']
    SRC['ExtraStartup/ExtraPre17/win64'] = ['.lx']

    SRC['Scripts'] = []
    SRC['Scripts/drop'] = ['.py']
    SRC['Scripts/lxserv'] = ['.py']
    SRC['Scripts/modox'] = ['.py']
    SRC['Scripts/modules'] = ['.py']
    SRC['Scripts/rigs'] = ['.py']

    SRC['Scripts/rs'] = ['.py']
    SRC['Scripts/rs/color_schemes'] = ['.py']
    SRC['Scripts/rs/component_setups'] = ['.py']
    SRC['Scripts/rs/components'] = ['.py']
    SRC['Scripts/rs/contexts'] = ['.py']
    SRC['Scripts/rs/element_sets'] = ['.py']
    SRC['Scripts/rs/event_handlers'] = ['.py']
    SRC['Scripts/rs/events'] = ['.py']
    SRC['Scripts/rs/item_features'] = ['.py']
    SRC['Scripts/rs/items'] = ['.py']
    SRC['Scripts/rs/meta_groups'] = ['.py']
    SRC['Scripts/rs/naming_schemes'] = ['.py']
    SRC['Scripts/rs/notifiers'] = ['.py']
    SRC['Scripts/rs/preset_thumbs'] = ['.py']
    SRC['Scripts/rs/xfrm_link_setups'] = ['.py']

    SRC['Scripts/servers'] = ['.py']

    # Presets
    SRC['Presets'] = []
    SRC['Presets/Armature Shapes'] = ['Rex_Rig.lxp', 'Rex_Sample.lxp',
                                      'Bolo.lxp', 'Bolo_Retarget.lxp',
                                      'Dog.lxp',
                                      'Biped.lxp', 'Biped_Retarget.lxp',
                                      'Quadruped.lxp',
                                      'Car.lxp']

    SRC['Presets/Modules'] = ['.lxp']
    SRC['Presets/Actions'] = []
    SRC['Presets/Guides'] = ['Biped.lxp', 'Biped_Retargeting.lxp',
                             'Quadruped.lxp',
                             'Bolo.lxp', 'Bolo_Retarget.lxp', 
                             'Dog.lxp',
                             'Car.lxp',
                             'Rex_Rig.lxp', 'Rex_Sample.lxp']
    SRC['Presets/Poses'] = []
    SRC['Presets/Poses/Dog'] = ['.lxp']
    SRC['Presets/Poses/Bolo'] = ['.lxp']
    SRC['Presets/Poses/Bolo/Hands'] = ['.lxp']
    SRC['Presets/Poses/Bolo/Advanced'] = ['.lxp']
    SRC['Presets/Poses/Rex'] = ['.lxp']
    SRC['Presets/Poses/Biped'] = ['.lxp']

    SRC['Presets/Rigs'] = ['Quadruped.lxp',
                           'Biped.lxp', 'Biped_Adv.lxp', 'Biped_Game.lxp', 'Biped_Unreal.lxp',
                           'Retarget_Biped.lxp', 'Retarget_Biped_Game.lxp', 'Retarget_Biped_Unreal.lxp', 
                           'Car.lxp',
                           'Rex.lxp']
    SRC['Presets/Skeleton Bake'] = ['.lxp']

    # Internal Presets
    SRC['Presets_Internal'] = []
    SRC['Presets_Internal/Modules'] = ['Base.lxp',
                                       'Path Car Front Axle.lxp',
                                       'Path Car Rear Axle.lxp',
                                       'Eyelids.lxp']
    SRC['Presets_Internal/Pieces'] = ['.lxp']

    # Samples
    SRC['Samples'] = ['Bolo_Start.lxo', 'Bolo_Rigged.lxo',
                      'Bolo_Retarget_Start.lxo', 'Bolo_Retarget_Rigged.lxo',
                      'Bolo_Adv_Start.lxo', 'Bolo_Adv_Rigged.lxo',
                      'Dog_Start.lxo', 'Dog_Rigged.lxo',
                      'Car_Start.lxo', 'Car_Rigged.lxo',
                      'Bolo_SpaceSwitching_Start.lxo', 'Bolo_SpaceSwitching_Done.lxo',
                      'Rex_Start.lxo', 'Rex_Rigged.lxo'
                      ]

    # Temporary folder
    SRC['Temp'] = ['emptyDir.txt']

    # Add filenames for files that we do not want to include.
    # This is global namespace, these files can be in any folder.
    # We don't want to include the dev tools.
    SKIP_FILES = ['_rs_cmd_dev.py', 'form_devToolbar.CFG']

    # These files will be renamed. Again - global namespace.
    RENAME_FILES = {'ovr_layout_timeline.CFG': 'ovr_layout_timeline.CFG.disabled'}

    return SRC, SKIP_FILES, RENAME_FILES

def makePackage(srcPath, dstPath):
    """ Makes a pacakge.
    
    Parameters:
    -----------
    srcPath : str
        Path to the kit folder that contains all the files for the kit.
        It'll be Kit/AutoCharacterSystem one in repo.
    
    dstPath : str
        Path to where the package should be created in.
    """

    SRC, SKIP_FILES, RENAME_FILES = initData()

    # Clean up destination folder.
    if os.path.isdir(dstPath):
        contents = os.listdir(dstPath)
        for element in contents:
            fullPath = os.path.join(dstPath, element)
            if os.path.isdir(fullPath):
                shutil.rmtree(fullPath, ignore_errors=True)
                print('Clearing directories: %s' % fullPath)
            else:
                os.remove(fullPath)
                print('Clearing file: %s' % fullPath)
    else:
        os.mkdir(dstPath)

    for folderKey in SRC.keys():
        print(folderKey)
               
        if folderKey == '_main':
            srcFolderName = ''
        else:
            srcFolderName = folderKey

        # Processing entries that are dictionaries.
        if srcFolderName and SRC[srcFolderName] and isinstance(SRC[folderKey], dict):
            dstFolderName = SRC[folderKey].keys()[0]
            filesToCopy = SRC[folderKey][SRC[folderKey].keys()[0]]
        # Processing entries that are lists.
        else:
            dstFolderName = srcFolderName
            filesToCopy = SRC[folderKey]
            
        srcFld = os.path.join(srcPath, srcFolderName)
        dstFld = os.path.join(dstPath, dstFolderName)

        if not os.path.isdir(dstFld):
            os.mkdir(dstFld)
        
        # Skip empty files list immediately.
        if not filesToCopy:
            continue

        files = _getDirectoryFiles(srcFld)
        
        for fullPath in files:
            if not os.path.isfile(fullPath):
                continue

            path, name = os.path.split(fullPath) # splits into head and tail, tail is the last component after last slash.

            if name in SKIP_FILES:
                print('Skipping file: %s' % name)
                continue
            
            try:
                name = RENAME_FILES[name]
            except KeyError:
                pass

            # Copy will happen only if at least one extension for files to copy was provided.
            # Or if filename was provided.
            for extension in filesToCopy:
                if not extension:
                    continue
                # Handling extensions
                if extension.startswith('.'):
                    if str(name).endswith(extension):
                        dstFile = os.path.join(dstFld, name)
                        shutil.copy2(fullPath, dstFile)
                        print('Copying: %s --> %s' % (fullPath, dstFile))
                # Handling specific filenames
                else:
                    if str(name) == extension:
                        dstFile = os.path.join(dstFld, name)
                        shutil.copy2(fullPath, dstFile)
                        print('Copying: %s --> %s' % (fullPath, dstFile))                        

def _getDirectoryFiles(path):
    """ Gets a list of files in a given directory.
    """
    dirContents = os.listdir(path) # gets all files and folders in a given dir
    files = []
    for element in dirContents:
        f = os.path.join(path, element)
        if os.path.isfile(f):
            files.append(f)
    return files
    
def _walkDirectory(path):
    """ Walks given directory and all its subdirectories and returns a list of files.
    
    Files are full filenames together with a path.
    """
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for filename in f:
            files.append(os.path.join(r, filename))
    
    print (files)
    
    return files
