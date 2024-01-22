
""" The rig.
"""


import time

import lx
import lxu
import modo
import modox

from .log import log as log
from .debug import debug
from .core import service
from .items.root_item import RootItem
from .items.root_assm import RootAssembly
from .item_utils import ItemUtils
from .const import EventTypes as e
from . import const as c
from . import item
from . import module_op
from .component_setups.rig import RigComponentSetup
from . import meta_rig_factory
from . import meta_rig
from . import deform_stack
from .preset_thumbs.rig import RigPresetThumbnail
from .resolutions import Resolutions
from .item_feature_op import ItemFeatureOperator
from .rig_assm_op import RigAssemblyOperator
from .util import getTime


class RigAccessLevel(object):
    DEVELOPMENT  = 0
    EDIT = 1
    ANIMATE = 2


class Rig(object):
    """ Represents the entire rig.
        
    Parameters
    ----------
    rootModoItem : RootItem, modo.Item, str
    """

    AccessLevel = RigAccessLevel

    # -------- Class methods
    
    @classmethod
    def getFromOther(cls, other):
        """ Gets rig from other type of object.
        
        Parameters
        ----------
        other : Rig, str, RootItem
            Rig, the string ident of its root item or the root item itself.
            
        Returns
        -------
        Rig
        
        Raises
        ------
        TypeError
            When rig cannot be initialised with the other object.
        """
        if isinstance(other, cls):
            return other
        try:
            return cls(other)
        except TypeError:
            raise
        raise TypeError

    # -------- Public properties and methods

    @property
    def name(self):
        return self._root.name

    @name.setter
    def name(self, newName):
        """ Set new name for the rig.
        """
        oldName = self._root.name
        self._root.name = newName
        self._rigSetup.iterateOverItems(self._renderRigItemName)
        self._rigMeta.renderNames()
        service.events.send(c.EventTypes.RIG_NAME_CHANGED, rig=self, oldName=oldName, newName=newName)

    @property
    def identifier(self):
        """
        Gets rig identifier (if any).

        Returns
        -------
        str
        """
        return self.rootItem.identifier
    
    @property
    def sceneIdentifier(self):
        """ Returns rig's scene identifier.

        Returns
        -------
        str
            This in fact is rig's root modo item ident.
        """
        return self._root.modoItem.id

    @property
    def namingScheme(self):
        """ Returns name scheme object for this rig.
        """
        return self._root.namingScheme

    @namingScheme.setter
    def namingScheme(self, nameScheme):
        """ Setting new name scheme needs to rebuild all rig names.
        """
        self._root.namingScheme = nameScheme
        self.name = self.name

    @property
    def colorScheme(self):
        """ Returns color scheme object for this rig.
        
        Returns
        -------
        ColorScheme or None if color scheme is not set.
        """
        return self._root.colorScheme

    @colorScheme.setter
    def colorScheme(self, colorScheme):
        """ Sets new color scheme for a rig.
        
        Parameters
        ----------
        colorScheme : ColorScheme or str
            Color scheme object to set or its string identifier.
        """
        self._root.colorScheme = colorScheme
        service.events.send(c.EventTypes.RIG_COLOR_SCHEME_CHANGED, rig=self)

    @property
    def selected(self):
        """ Gets rig selected state.
        
        Returns
        -------
        bool
        """
        return self._root.selected

    @selected.setter
    def selected(self, state):
        """ Sets rig selected state.
        
        Parameters
        ----------
        state : bool
        """
        self._root.selected = state

    @property
    def rootItem(self):
        return self._root

    @property
    def rootModoItem(self):
        return self._root.modoItem

    @property
    def metaRig(self):
        return self._rigMeta

    @property
    def setup(self):
        """ Gets rig's component setup.
        
        Returns
        -------
        RigComponentSeutp
        """
        return self._rigSetup

    @property
    def visible(self):
        return self._rigSetup.visible
    
    @visible.setter
    def visible(self, visState):
        """ Changes visibility of the entire rig hierarchy.
        
        It can be used to show/hide entire rig.
        
        Parameters
        ----------
        visState : rs.c.ItemVisible or bool
        """
        self._rigSetup.visible = visState

    @property
    def accessLevel(self):
        """ Access level tells what can be done with a rig.
        """
        return self._root.accessLevel

    @accessLevel.setter
    def accessLevel(self, level):
        self._root.accessLevel = level

    @property
    def actor(self):
        """ Gets rig's actor.
        
        Returns
        -------
        modo.Actor, None
        """
        try:
            actorGroup = self._rigMeta.getGroup(c.MetaGroupType.ACTOR).modoGroupItem
        except LookupError:
            return None
        return modo.Actor(actorGroup)
        
    def getElements(self, setIdentifier):
        """ Gets elements of from an element set.
        
        Parameters
        ----------
        setIdentifier : str
            Element set identifier as defined in const.ElementSetType.
            
        Returns
        -------
        [modo.Item]
        
        Raises
        ------
        LookupError
            When given element set cannot be found.
        """
        elementSet = self.getElementSet(setIdentifier)
        return elementSet.elements

    def getElementSet(self, setIdentifier):
        """ Gets elements set object by its identifier.
        
        Parameters
        ----------
        setIdentifier : str
            Element set identifier as defined in const.ElementSetType.
            
        Returns
        -------
        ElementSet
        """
        try:
            elsetClass = service.systemComponent.get(c.SystemComponentType.ELEMENT_SET, setIdentifier)
        except LookupError:
            raise
        
        return elsetClass(self.rootItem)

    def selfDelete(self):
        """ Remove the rig from scene.
        
        When this is done the rig is gone completely.
        """
        self._rigMeta.selfDelete()
        self._rigSetup.selfDelete()

    def selfValidate(self):
        self._rigSetup.selfValidate()

    def iterateOverItems(self, callback):
        self._rigSetup.iterateOverItems(callback)

    def iterateOverHierarchy(self, callback):
        self._rigSetup.iterateOverHierarchy(callback)

    def removeSetup(self):
        """ Removes the entire rig schematic setup from scene.
        
        This makes the scene file much smaller but it also freezes the rig
        so it cannot be modified in any way. You can only use the rig
        for animation.
        """
        RigAssemblyOperator(self).clearAll()
        
    def standardize(self):
        """ Standardises the rig so it can be opened in vanilla MODO.
        """
        service.events.send(c.EventTypes.RIG_STANDARDIZE_PRE, rig=self)

        self._allRigItems = {}
        self._rigSetup.iterateOverItems(self._collectItemToStandardise)
        
        monitorTicks = len(self._allRigItems) * 10
        monitor = modox.Monitor(monitorTicks, 'Standardise Rig')

        # Standardization happens in two stages.
        # The first stage calls onStandardize() on item features and items
        # so any preparation work that has to be done on these before the actual
        # standradization happens can be done with still full rig context.
        # Second stage is standardization itself.

        # Monitor updates every 40 items.
        updateMonitorCycle = 40

        for item in list(self._allRigItems.values()):
            ItemUtils.preStandardize(item)

            updateMonitorCycle -= 1
            if updateMonitorCycle == 0:
                updateMonitorCycle = 40
                monitor.tick(2 * updateMonitorCycle)

        # Monitor updates every 40 items here too.
        updateMonitorCycle = 40
        for item in list(self._allRigItems.values()):
            ItemUtils.standardize(item)

            updateMonitorCycle -= 1
            if updateMonitorCycle == 0:
                updateMonitorCycle = 40
                monitor.tick(8 * updateMonitorCycle)

        monitor.release()
        
        del self._allRigItems

    # -------- Modules

    @property
    def modules(self):
        return self._moduleOp

    # --- Items
    
    def newItem(self, itemType, itemSubtype=None, itemName=None):
        """ Adds new item to the rig.
        
        The item will be added to current edit module or right under the rig
        if there are no modules yet.

        Returns
        -------
        Item
            
        """
        try:
            itemClass = service.systemComponent.get(c.SystemComponentType.ITEM, itemType)
        except LookupError:
            raise TypeError

        newRigItem = itemClass.new(itemName, itemSubtype, self._rigSetup)
        self.addItem(newRigItem)
        return newRigItem

    def addItem(self, itemToAdd, module=None):
        """ Adds existing modoItem to the rig.
        
        The item will be added to specific module, edit module
        if module is not specified or under the rig if there
        are no modules yet.
        
        Parameters
        ----------
        item : Item, modo.Item
            Either rig item or modo item that will be added to rig/module.
        
        Raises
        ------
        TypeError
            When item to add is of invalid type.
        """
        editModule = self.modules.editModule
        if editModule is not None:
            editModule.addItem(itemToAdd)
        else:
            if issubclass(itemToAdd.__class__, item.Item):
                self._rigSetup.addItem(itemToAdd.modoItem)
                itemToAdd.renderAndSetName()
            elif isinstance(itemToAdd, modo.Item):
                self._rigSetup.addItem(itemToAdd)
            else:
                raise TypeError

    def rebuildMeta(self):
        """ Forces rebuild all meta data.
        """
        rebuildStart = getTime()

        self._buildMeta(self)

        rebuildEnd = getTime()
        if debug.output:
            log.out("Meta rig rebuilt in: %f s." % (rebuildEnd - rebuildStart))

    def save(self, filename, captureThumb=False):
        """ Saves rig preset out to the given filename.
        
        Paramters
        ---------
        filename : str
            Complete path to a preset file the rig will be saved to.
        """
        if captureThumb:
            thumb = RigPresetThumbnail()
            thumb.capture()

        self.rootItem.setSystemVersion()
        self._rigSetup.save(filename)

        if captureThumb:
            thumb.setOnPreset(filename)

    # -------- Private methods

    def _renderRigItemName(self, itemToRename):
        try:
            rigItem = item.Item.getFromModoItem(itemToRename)
        except TypeError:
            return

        rigItem.renderAndSetName()

    @property
    def _rigSetup(self):
        """ Gets access to RigComponentSetup of the rig.
        
        ALWAYS use this property to access the setup.
        
        Returns
        -------
        RigComponentSetup
        """
        if self.__rigSetupObj is None:
            self.__rigSetupObj = RigComponentSetup(self.rootModoItem)
        return self.__rigSetupObj

    @property
    def _rigMeta(self):
        if self.__rigMetaObj is None:
            self.__rigMetaObj = meta_rig.MetaRig(self._root)
        return self.__rigMetaObj

    @property
    def _moduleOp(self):
        if self.__moduleOpObj is None:
            self.__moduleOpObj = module_op.ModuleOperator(self._root)
        return self.__moduleOpObj

    def _collectItemToStandardise(self, modoItem):
        try:
            rigItem = ItemUtils.getItemFromModoItem(modoItem)
        except TypeError:
            return
        
        self._allRigItems[modoItem.id] = rigItem

    def __init__(self, rootItem, name=""):
        if rootItem is None:
            raise TypeError

        try:
            self._root = RootItem.getFromOther(rootItem)
        except TypeError:
            raise

        self.__rigSetupObj = None
        self.__rigMetaObj = None
        self.__moduleOpObj = None

    def __str__(self):
        return self.name + ' : ' + self.sceneIdentifier

    def __eq__(self, other):
        if isinstance(other, str):
            return self.rootModoItem.id == other
        elif isinstance(other, Rig):
            return self.rootModoItem.id == other.rootModoItem.id
        elif isinstance(other, RootItem):
            return self.rootModoItem == other.modoItem
        elif isinstance(other, modo.Item):
            return self.rootModoItem.id == other.id
        elif type(other) in [lx.object.Item, lxu.object.Item]:
            return self.rootModoItem.id == other.Ident()
        else:
            return False

    def __ne__(self, other):
        """ != """
        return not self.__eq__(other)

    def __getitem__(self, identifier):
        """ Gets element set with a given identifier.
        """
        return self.getElementSet(identifier)

    @classmethod
    def new (cls,
             name,
             namingScheme='standard',
             colorScheme='rbstd',
             modoScene=None):
        """ Creates new rig.
        
        Parameters
        ----------
        name : str
            Name of the rig to create.
        
        namingScheme : str, optional
            Identifier of the default naming scheme.
        
        colorScheme : str, optional
            Identifier of the default color scheme.
        
        modoScene : modo.Scene
            Optional scene to spawn rig to.
        """
        if modoScene is None:
            modoScene = modo.Scene()

        root = RootItem.new(name)
        assembly = RootAssembly.new(name)
       
        # Root cannot be selectable in viewport.
        root.setChannelProperty('select', 2) # 2 = off
        
        root.name = name
        root.namingScheme = namingScheme
        root.colorScheme = colorScheme

        rigSetup = RigComponentSetup.new(root.modoItem, assembly.modoItem)
        
        deformStack = deform_stack.DeformStack.new(root)
        rigSetup.addItem(deformStack.modoItems)

        # Add one standard mesh resolution
        resolutions = Resolutions(root)
        resolutions.addResolution('High')
        
        return cls.fromSetupInScene(root.modoItem)

    @classmethod
    def fromSetupInScene(cls, rootModoItem):
        """ Creates rig from setup that is already in scene.
        """
        rig = cls(rootModoItem)
        metaRig = cls._buildMeta(rig)
        service.events.send(e.RIG_DROPPED, rig=rig)

        # Setting rig name is an operation on the rig so it has to be
        # performed when the rig is already fully ready.
        rig.name = rig.name

        modox.Item(rootModoItem.internalItem).autoFocusInItemList()

        return rig

    @classmethod
    def _sendItemAddedEvent(cls, modoItem):
        service.events.send(c.EventTypes.ITEM_ADDED, item=modoItem)
    
    @classmethod
    def _buildMeta(cls, rig):
        """ Spawns meta rig into the scene.
        
        If meta rig existed previously it's deleted first.
        
        Parameters
        ----------
        rig : Rig
            Rig for which meta data needs to be built.
        """
        try:
            metaRig = meta_rig.MetaRig(rig.rootItem)
        except TypeError:
            pass
        else:
            metaRig.selfDelete()

        metaFactory = meta_rig_factory.MetaRigFactory()
        metaRig = metaFactory.new(rig.rootItem)
        metaRig.renderNames()

        # Go through all rig items and send item added event.
        # This will force meta rig to populate its contents.
        rig.iterateOverItems(cls._sendItemAddedEvent)

        return metaRig