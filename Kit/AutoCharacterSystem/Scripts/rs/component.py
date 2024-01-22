

import modo
from .const import SystemComponentType
from .items.generic import GenericItem
from .item import Item
from .item_utils import ItemUtils
from .component_setup import ComponentSetup
from .core import service


class Component(object):
    """ Rig component is a piece of a rig that has a purpose in the rig.
    
    Rig component is tightly coupled with rig component setup.
    Component setup is the actual construction that is part of MODO scene
    and is not aware of rigging system in any way. It's at the generic MODO level.
    Component wraps around component setup and is part of rigging system.
    
    Parameters
    ----------
    componentRootItem : Item, modo.Item ,str

    Raises
    ------
    TypeError
        When trying to initialise with wrong item.

    Attributes
    ----------
    descIdentifier : str
        Unique component identifier.

    descRootItemClass : Item, None
        Class of rig item the root item should be. If set to None the root item
        will be just modo group locator and generic rig item type.

    descAssemblyItemClass : Item, None
        Rig item class of an assembly group that will be container for the component.
        When set to None, a generic rig item type is used.

    descComponentSetupClass : ComponentSetup, None
        This has to be the component setup class that is created for this component.
        Right now it's possible to pass None to get default (base) component setup but
        I don't think that's going to work. None should probably be removed as an option.

    descRootItemSelectable : str
        When False component root item will not be selectable which is probably desired
        in most cases. False is the default.

    descLookupGraph : str
        When set the component will be linked via this graph to the rig root item.
        It makes looking up all components of this type very easy and direct.
    """
    
    TAG_COMPONENT = 'RSCM'
    
    # -------- Attributes
    
    descIdentifier = ''
    descUsername = ''
    descRootItemClass = None
    descAssemblyItemClass = None
    descRootItemName = None
    descAssemblyItemName = None
    descRootItemSelectable = False
    descComponentSetupClass = None
    descLookupGraph = None

    # -------- System component attributes, do not touch.

    @classmethod
    def sysType(cls):
        return SystemComponentType.COMPONENT
    
    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
   
    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Component'
    
    # -------- Public methods
    
    @classmethod
    def autoInitialiseRootItem(cls, initObject):
        """ Automatically initialises root item for a component.
        
        Paramters
        ---------
        initObject : modo.Item, str, Item
            When Item is passed it has to be of a type that is defined in component description
            (descRootItemClass).
        """
        if initObject is None:
            raise TypeError

        if isinstance(initObject, str):
            try:
                initObject = modo.Scene().item(initObject)
            except LookupError:
                raise TypeError

        root = None

        # If item class is known try to use it
        if cls.descRootItemClass is not None:
            if isinstance(initObject, cls.descRootItemClass):
                root = initObject
            else:
                try:
                    root = cls.descRootItemClass(initObject)
                except TypeError:
                    raise

        # If class is unknown see if it's generic item.
        # If it's not, try to cast it to generic item.
        # Here we assume that is the root class was not defined
        # it is GenericItem by default.
        else:
            if isinstance(initObject, GenericItem):
                root = initObject
            else:
                try:
                    root = GenericItem(initObject)
                except TypeError:
                    raise 
        
        if root is None:
            raise TypeError

        return root

    @classmethod
    def new(cls, rootModoItem=None, assemblyModoItem=None):
        """ Spawns new rig component into the scene.
        
        Note that at this point component does not belong to any rig and has no rig context.

        Parameters
        ----------
        rootModoItem : modo.Item
            An existing modo item can be passed to serve as root item of a component.
            Note that this item has to be of an appropriate type.

        assemblyModoItem : modo.Item
            An existing assembly item can be passed to serve as module assembly.
            This allows for creating modules off existing setups contained within
            module.

        Returns
        -------
        RigComponent object
        """
        scene = modo.Scene()
    
        if cls.descRootItemClass is None:
            if rootModoItem is None:
                modoItem = scene.addItem('groupLocator', name=cls.descRootItemName)
                rootItem = GenericItem.newFromExistingItem(modoItem, name=cls.descRootItemName)
            else:
                rootItem = GenericItem.newFromExistingItem(rootModoItem, name=cls.descRootItemName)
        else:
            if rootModoItem is None:
                rootItem = cls.descRootItemClass.new()
            else:
                rootItem = cls.descRootItemClass.newFromExistingItem(rootModoItem)

        if cls.descAssemblyItemClass is None:
            if assemblyModoItem is None:
                modoItem = scene.addGroup(cls.descAssemblyItemName, gtype='assembly')
                assemblyItem = GenericItem.newFromExistingItem(modoItem, name=cls.descAssemblyItemName)
            else:
                assemblyItem = GenericItem.newFromExistingItem(rootModoItem, name=cls.descAssemblyItemName)
        else:
            if assemblyModoItem is None:
                assemblyItem = cls.descAssemblyItemClass.new()
            else:
                assemblyItem = cls.descAssemblyItemClass.newFromExistingItem(assemblyModoItem)

        if cls.descComponentSetupClass is None:
            setupClass = ComponentSetup
        else:
            setupClass = cls.descComponentSetupClass
        setup = setupClass.new(rootItem.modoItem, assemblyItem.modoItem)

        rootItem.modoItem.setTag(cls.TAG_COMPONENT, cls.descIdentifier)
        assemblyItem.modoItem.setTag(cls.TAG_COMPONENT, cls.descIdentifier)
        
        if not cls.descRootItemSelectable:
            rootItem.setChannelProperty('select', 2) # 2 = off

        newComponent = cls(rootItem)
        newComponent.onNew()

        return newComponent
    
    @classmethod
    def getFromModoItem(cls, modoItem):
        """ CLASSMETHOD: Gets component from one of its items.
        
        Paramters
        ---------
        modoItem : modo.Item
        
        Returns
        -------
        Component
        
        Raises
        ------
        TypeError
            When item does not belong to any components.
        """
        setup = ComponentSetup.getSetupFromModoItem(modoItem)
        if setup is None:
            raise TypeError

        identifier = cls._readTypeFromTag(setup.rootModoItem)
        if identifier is None:
            raise TypeError
        
        try:
            componentClass = service.systemComponent.get(SystemComponentType.COMPONENT, identifier)
        except LookupError:
            raise TypeError
        
        return componentClass(setup.rootModoItem)

    def onNew(self):
        """ Gets called when new rig component is created.
        
        This should be overriden by inheriting class.
        """
        pass

    @property
    def rootItem(self):
        """ Gets component's root item.
        
        Returns
        -------
        Item
        """
        return self._root
    
    @property
    def rootModoItem(self):
        """ Gets component's root modo item.
        
        This will be standard MODO item.

        Returns
        -------
        modo.Item
        """
        return self._root.modoItem

    @property
    def assemblyModoItem(self):
        """ Gets component's assembly item.
        
        Returns
        -------
        modo.Item
        """
        return self._setup.rootAssembly

    @property
    def assemblyItem(self):
        """ Gets component's assembly item as rig item.

        Returns
        -------
        Item
        """
        modoItem = self.assemblyModoItem
        return ItemUtils.getItemFromModoItem(modoItem)

    @property
    def rigRootItem(self):
        """ Gets component's rig root item.
        
        Returns
        -------
        RootItem
            Or None if component is not attached to any rig.
        """
        return self._root.rigRootItem

    @property
    def sceneIdentifier(self):
        """ Returns scene identifier of a component.
        
        This is simply an ident of component's root item.
        
        Returns
        -------
        str
        """
        return self.rootModoItem.id

    @property
    def setup(self):
        """ Gets component setup for this component.
        
        Returns
        -------
        ComponentSetup
        """
        return self._setup

    @property
    def visible(self):
        return self._setup.visible
    
    @visible.setter
    def visible(self, visState):
        """ Changes visibility of the entire component hierarchy.
        
        Parameters
        ----------
        visState : rs.c.ItemVisible, bool
            When bool is passed True means default visibility and False means
            hidden with children.
        """
        self._setup.visible = visState

    def updateItemNames(self):
        """ Updates names of all items in the component.
        
        This is used mainly after component was added to the rig
        to refresh all its item names.
        """
        self._setup.iterateOverItems(self._renderItemName)

    @property
    def type(self):
        """ Gets component type string identifier.
        
        Returns
        -------
        str
        """
        return self._readTypeFromTag(self._root.modoItem)
        
    # -------- Private methods
    
    @classmethod
    def _readTypeFromTag(cls, modoItem):
        try:
            return modoItem.readTag(cls.TAG_COMPONENT)
        except LookupError:
            pass
        return None

    def _renderItemName(self, itemToRename):
        try:
            rigItem = ItemUtils.getItemFromModoItem(itemToRename)
        except TypeError:
            return

        rigItem.renderAndSetName()

    def __init__(self, componentRootItem):
        try:
            self._root = self.autoInitialiseRootItem(componentRootItem)
        except TypeError:
            raise

        try:
            self._setup = self.descComponentSetupClass(self._root.modoItem)
        except TypeError:
            raise
        
        
       