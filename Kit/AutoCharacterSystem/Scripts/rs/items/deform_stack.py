
""" Deformers stack root deform folder module.
"""


import lx
import modo

from ..item import Item
from ..const import RigItemType


class DeformStackRootItem(Item):
    
    descType = RigItemType.DEFORM_ROOT
    descUsername = 'Deformers Stack Root'
    descModoItemType = 'deformFolder'
    descDefaultName = 'DeformStack'
    descPackages = ['rs.pkg.generic']


class NormalizingFolderItem(Item):
    
    descType = RigItemType.NORMALIZING_FOLDER
    descUsername = 'Normalizing Folder'
    descModoItemType = 'deformGroup'
    descDefaultName = 'NormalizingFolder'
    descPackages = ['rs.pkg.generic']


class PostCorrectiveMorphsFolderItem(Item):
    descType = RigItemType.POST_CORRECTIVE_MORPHS_FOLDER
    descUsername = 'Post Corrective Morphs Folder'
    descModoItemType = 'deformFolder'
    descDefaultName = 'PostCorrectiveMorphsFolder'
    descPackages = ['rs.pkg.generic']
