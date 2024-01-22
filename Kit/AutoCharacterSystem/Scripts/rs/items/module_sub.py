
""" Module sub items.
"""


import lx
from ..item import Item
from ..const import *
from ..component_setups.module import ModuleComponentSetup
from ..items.module_root import ModuleRoot


class GuideAssembly(Item):
    """
    This is an assembly within which all module guide should be enclosed.
    """
    descType = RigItemType.GUIDE_ASSM
    descUsername = 'Guide Assembly'
    descModoItemType = 'group'
    descModoItemSubtype = 'assembly'
    descDefaultName = 'Main'
    descPackages = ['rs.pkg.generic']

    # -------- Public interface

    def onAdd(self, subtype):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor blue')


class ModuleRigAssembly(Item):
    """
    This is an assembly within which main module rigging should be enclosed.
    """
    descType = RigItemType.MODULE_RIG_ASSM
    descUsername = 'Module Rig Assembly'
    descModoItemType = 'group'
    descModoItemSubtype = 'assembly'
    descDefaultName = 'Rig'
    descPackages = ['rs.pkg.generic']

    # -------- Public interface

    def onAdd(self, subtype):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor yellow')


class MirrorChannelsGroup(Item):
    
    descType = RigItemType.MIRROR_CHAN_GROUP
    descUsername = 'Mirror Channels Group'
    descModoItemType = 'group'
    descDefaultName = 'Main'
    descPackages = ['rs.pkg.generic']

    # -------- Public interface

    def onAdd(self, subtype):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor ultramarine')
