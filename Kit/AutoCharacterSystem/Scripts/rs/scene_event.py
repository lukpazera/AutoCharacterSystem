

import time

import lx
import modo
import modox

from . import sys_component
from . import const as c
from .log import log
from .component_setup import ComponentSetup
from .item_utils import ItemUtils
from .util import run
from .core import service


class SceneEvent(sys_component.SystemComponent):
    
    descIdentifier = ''
    descUsername = ''
    
    def process(self, arguments):
        pass

    @classmethod
    def sysType(cls):
        return c.SystemComponentType.SCENE_EVENT
    
    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
    
    @classmethod
    def sysUsername(cls):
        return cls.descUsername + 'Scene Event'
    
    @classmethod
    def sysSingleton(cls):
        return True


class event_RootSelected(SceneEvent):
    
    descIdentifier = 'rootSel'
    descUsername = 'Root Item Selected'
    
    def process(self, arguments):
        lx.eval('rs.rig.edit {%s}' % arguments[0])


class event_ModuleRootSelected(SceneEvent):
    
    descIdentifier = 'moduleSel'
    descUsername = 'Module Root Item Selected'
    
    def process(self, arguments):
        run('rs.module.edit {%s}' % arguments[0])


class event_ItemParented(SceneEvent):
    """ Item was parented under the rig hierarchy.
    """
    
    descIdentifier = 'itemParent'
    descUsername = 'Item Parented'
    
    def process(self, arguments):
        """ Processes item parented event.
        
        Parameters
        ----------
        arguments : list of str
            0: identifier of the item that was parented.
            1: identifier of the rig root item
        """
        s = time.time()
    
        scene = modo.Scene()
        try:
            itemToAdd = scene.item(arguments[0])
        except LookupError:
            return False

        hrchSetup = ComponentSetup.getSetupFromItemInSetupHierarchy(itemToAdd)
        if hrchSetup is None:
            return False
        hrchSetup.addItem(itemToAdd, addHierarchy=True)

        # Refresh all added item names, if they're rig items.
        hierarchy = modox.ItemUtils.getHierarchyRecursive(itemToAdd, includeRoot=True)
        for item in hierarchy:
            try:
                rigItem = ItemUtils.getItemFromModoItem(item)
            except TypeError:
                pass
            else:
                rigItem.renderAndSetName()

        log.out('Items added to rig event processing time: %f' % (time.time() - s))
