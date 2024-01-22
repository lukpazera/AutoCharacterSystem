
""" Items that form layout of the rig hierarchy.
"""


import lx
from ..item import Item
from ..const import *


class ModulesFolder(Item):

    descType = RigItemType.MODULES_FOLDER
    descUsername = 'Modules Folder'
    descModoItemType = 'groupLocator'
    descDefaultName = 'Modules'
    descPackages = ['rs.pkg.generic']
    descSelectable = False
    
    def onAdd(self, subtype=None):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor white')

        
class GeometryFolder(Item):

    descType = RigItemType.GEOMETRY_FOLDER
    descUsername = 'Geometry Folder'
    descModoItemType = 'groupLocator'
    descDefaultName = 'Geometry'
    descPackages = ['rs.pkg.generic']
    descSelectable = False

    def onAdd(self, subtype=None):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor green')
