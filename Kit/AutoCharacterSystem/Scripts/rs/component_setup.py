
""" Rig Component Setup.
"""


import time

import lx
import modo
import modox

from .core import service
from .log import log as log
from .debug import debug
from . import const as c
from .sys_component import SystemComponent


class ComponentSetup(SystemComponent):
    """ The component setup is an actual construction from items and modifiers.
    
    This construction represents a component of the rig such as module, a set of bind
    or rigid meshes, etc. 
    
    Component setup is enclosed in a single assembly and consists of:
    - locator type root item of the setup,
    - hierarchy of items under this root,
    - other items (such as modifiers) that are not part of hierarchy.
      These need to be in the setup assembly.

    Component setup works on MODO item level, it knows nothing about its purpose
    within the rig, it has no knowledge of rigging system at all.
     
    It's possible to nest component setups.
    The rig itself is the root level component setup.
    You can use component setup to operate on entire setups hierarchy (rig),
    for example iterativng over hierarchy doesn't just iterate through items in
    current setup, it'll also go through items from all subsetups.
    
    Assemblies are parented to other assemblies using both parent graph and itemGroups graph
    whjch is the same as what MODO does when adding a subassembly to existing assembly.

    ---
    REVISE THIS: 
    The setup for the item will be initialised as long as an item is simply in a setup hierarchy.
    The item doesn't need to have the actual graph connections required for the setup.
    This needs to be checked down the line because this way it's possible for an item that isn't
    really part of setup to be recognised as one.
    
    This certainly leads to a case where in scene remove item event for example the setup gets
    initialised and clearItem() gets called on an item that isn't part of the setup but just parented to it.
    This is harmless in this case but see if that's a potential trouble in some other situations.
    
    Parameters
    ----------
    modoItem : modo.Item
        Valid item that is in the setup. It can be any item in the setup, it does
        not need to be root item. It can also be setup's root assembly or one of its
        subassemblies.
        
    Raises
    ------
    TypeError
        If modoItem does not belong to any setup.
        
    Attributes
    ----------
    descLookupGraph : str
        When set the setup will be linked on this graph to the root of its parent setup.
        This happens when this setup is added to another one via parent't addSetup method.

    descOnCreateDropScript : str
        When set the drop script will be added to the setup on save so it's within the saved preset.
        It will be removed afterwards so the script is not there if the setup is in the scene.
        So the script is only within saved component setup preset and possibly after
        the preset is dropped back to the scene if it's not removed.

    descPresetDescription : str
        Sets the description for an assembly preset that this setup can be saved to.
        
    descSelfDestroyWhenEmpty : bool
        When True setup will destroy itself when an item is removed from it and this
        item is the last item in the setup (not counting root item and the assembly).
    """

    TAG_IDENTIFIER = 'RSST'
    GRAPH_SETUP = 'rs.rigSetup'
    GRAPH_ASSMROOT = 'assemblyRoot'

    # --- Public interface
    
    descIdentifier = ''
    descUsername = ''
    descLookupGraph = ''
    descPresetDescription = ''
    descOnCreateDropScript = None
    descSelfDestroyWhenEmpty = False

    # -------- System Component
    
    @classmethod
    def sysType(cls):
        return c.SystemComponentType.COMPONENT_SETUP
    
    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
    
    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Component Setup'
    
    @classmethod
    def sysSingleton(cls):
        return False

    # -------- Public methods
    
    @classmethod
    def new(cls, rootItem, assembly, contextSetup=None):
        """ Creates new rig component setup.
        
        The minimal setup consists of the root item (that contains entire
        setup hierarchy) and main assembly.
        Root item is automatically added to the assembly and linked with it
        using MODO's standard assembly root graph and a custom setup graph.
        
        Parameters
        ----------
        rootItem : modo.Item
            The item that will be root of the setup hierarchy.

        assembly : modo.Item
            The assembly item that will contain the entire setup.

        contextSetup : ComponentSetup, optional
            Component setup to which new attachment set will be added to
            as a subsetup.

        Raises
        ------
        TypeError
            when root item or assembly are invalid.
        """
        if not assembly or not rootItem:
            raise TypeError

        assembly.addItems(rootItem)
        # standard assembly root graph link
        rootAssmGraph = assembly.itemGraph(cls.GRAPH_ASSMROOT)
        rootItemGraph = rootItem.itemGraph(cls.GRAPH_ASSMROOT)
        rootItemGraph >> rootAssmGraph

        # setup graph link
        rootRigGraph = rootItem.itemGraph(cls.GRAPH_SETUP)
        assmRigGraph = assembly.itemGraph(cls.GRAPH_SETUP)
        rootRigGraph >> assmRigGraph

        # set identifier on both root and an assembly
        rootItem.setTag(cls.TAG_IDENTIFIER, cls.descIdentifier)
        assembly.setTag(cls.TAG_IDENTIFIER, cls.descIdentifier)

        newSetup = cls(rootItem)
        if contextSetup:
            contextSetup.addSetup(newSetup)

        return newSetup

    @classmethod
    def getSetupFromItemInSetupHierarchy(cls, modoItem):
        """ Gets setup from an item that is in its hierarchy.
        
        This is useful for getting setup for an item that is in setup hierarchy
        but is not part of the setup and you can't initialise setup with this item.
        This happens when user drags an item under setup hierarchy in item
        list for example.
        
        Parameters
        ----------
        modoItem : modo.Item
        
        Returns
        -------
        ComponentSetup or None
        """
        # TODO: This should really work on locator super type items only?
        while modoItem is not None:
            if cls._isSetupRoot(modoItem):
                break
            modoItem = modoItem.parent
        if modoItem is None:
            return None
        
        identInTag = cls._getSetupIdentifierFromModoItem(modoItem)

        # Get the right setup interface from service.
        try:
            setupClass = service.systemComponent.get(c.SystemComponentType.COMPONENT_SETUP, identInTag)
        except LookupError:
            return None
        return setupClass(modoItem)

    @classmethod
    def getSetupFromModoItem(cls, modoItem):
        """ Gets the setup in which given item is.
        
        When used on the base component setup class it will
        get any component setup the item is in.
        The returned interface will be of correct type.
        Otherwise, the setup will be returned only if an item
        is in setup that matches the class from which this
        method was called.
        
        Returns
        -------
        ComponentSetup or None
        """
        rootModoItem = cls._findSetupRootItem(modoItem)
        if rootModoItem is None:
            return None
        identInTag = cls._getSetupIdentifierFromModoItem(rootModoItem)
        
        # An inheriting class with identifier asks for a setup.
        if identInTag == cls.descIdentifier:
            return cls(rootModoItem)
        
        # Get the right setup interface from service.
        try:
            setupClass = service.systemComponent.get(c.SystemComponentType.COMPONENT_SETUP, identInTag)
        except LookupError:
            return None
        return setupClass(rootModoItem)

    @classmethod
    def isModoItemInSetup(cls, modoItem):
        """ Tests if given modo item is within a setup of a class from which this method is called.
        
        Returns
        -------
        bool
        """
        try:
            cls(modoItem)
        except TypeError:
            return False
        return True
        
    @property
    def rootModoItem(self):
        """ Returns setup root modo item.
        
        Returns
        -------
        modo.Item
        """
        return self._rootItem

    @property
    def rootAssembly(self):
        """ Gets the assembly item that is container for entire setup.
        
        Returns
        -------
        modo.Item or None
        """
        assmRootGraph = self._rootItem.itemGraph(self.GRAPH_SETUP)
        try:
            return assmRootGraph.forward(0)
        except LookupError:
            return None

    @property
    def parentSetup(self):
        """ Gets setup that is parent to this one.
                
        Returns
        -------
        RigComponentSetup
            None if there is no parent setup.
        """
        parentAssembly = self.rootAssembly.parent
        if parentAssembly is None:
            return None

        parentSetupRootItem = self._findSetupRootItemFromGroup(parentAssembly)

        try:
            return RigComponentSetup(parentSetupRootItem)
        except TypeError:
            return None

    @property
    def rootSetup(self):
        """ Returns root setup or the setup itself if this setup has no root.
        
        Root setup is a setup that has no setups above it.
        Typically this will be the rig itself.
        
        Returns
        -------
        RigComponentSetup
        """
        rootSetup = self.parentSetup
        while rootSetup is not None:
            nextSetupInHierarchy = rootSetup.parentSetup
            if nextSetupInHierarchy is None:
                break
            rootSetup = nextSetupInHierarchy
        if rootSetup is None:
            return self
        return rootSetup

    @property
    def isEmpty(self):
        """ Checks if the setup is empty.
        
        Setup is empty either when it has no items in assembly or if the only
        item in the assembly is the root.
        
        Returns
        -------
        bool
        """
        rootAssm = self.rootAssembly
        if rootAssm.itemCount == 0:
            return True
        elif rootAssm.itemCount == 1:
            if rootAssm.items[0] == self.rootModoItem:
                return True

        return False

    @property
    def identifier(self):
        """ Optional identifier for the setup.
        """
        try:
            return self._rootItem.readTag(self.TAG_IDENTIFIER)
        except LookupError:
            pass
        return None
    
    @property
    def visible(self):
        return self._rootItem.channel('visible').get(time=0.0, action=lx.symbol.s_ACTIONLAYER_EDIT)

    @visible.setter
    def visible(self, value):
        """ Toggles visibility of the component setup hierarchy.
        
        Paramters
        ---------
        value : c.ItemVisible.XXX, bool
            Either item visible state as used in MODO or a bool.
            Bool is converted such that True means default visibility value
            and False means hide with children.
        """
        if type(value) == bool:
            if value:
                value = c.ItemVisible.DEFAULT
            else:
                value = c.ItemVisible.NO_CHILDREN
        self._rootItem.channel('visible').set(value, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

    def addItem(self, modoItem, assemblyItem=None, addHierarchy=False):
        """ Add existing modo item to the setup.

        If the item belongs to another setup already it's removed
        from that setup first.

        Parameters
        ----------
        modoItem : modo.Item or list(modo.Item)
            Existing item that will be added to the setup.
            If this item is not part of setup hierarchy (is not under setup's
            root item) and is of the XfrmCore supertype it will be parented
            to the setup root item.
            
        assemblyItem : modoItem, optional
            Assembly to which this item should be added to. This assembly
            should be child of the main setup assembly.
            When not set the item will be added to setup's main assembly.
        """           
        if not isinstance(modoItem, list) and not isinstance(modoItem, tuple):
            modoItems = [modoItem]
        else:
            modoItems = modoItem
        
        for modoItem in modoItems:
            modoxItem = modox.Item(modoItem.internalItem)

            # If item is a group we need to add it as subassembly.
            if modoxItem.typeRaw == modox.const.ItemType.GROUP:
                self.addSubAssembly(modoItem)
                continue

            # Xfrmcore super type items (locators) need to be in the setup
            # hierarchy in item list.
            # If they're in the hierarchy already they are not being reparented.
            if modoxItem.isOfXfrmCoreSuperType:
                if not modoxItem.isInHierarchy(self.rootModoItem):
                    modoItem.setParent(self.rootModoItem, index=-1)
    
            # If an item is already in root assembly or one of its child assemblies
            # we assume the item is already in the setup and we do not need to readd it.
            if self._findSetupRootItem(modoItem) == self.rootModoItem:
                if debug.output:
                    log.out('Item %s is already in the rig setup %s.' % (modoItem.name, self.rootModoItem.name))
                continue
            
            # Grab hierarchy
            if addHierarchy:
                hrchItems = modox.ItemUtils.getHierarchyRecursive(modoItem, includeRoot=True)
            else:
                hrchItems = [modoItem]
                
            # Now we see if the item is in any other setup.
            # If it is, it needs to be cleared from that setup.
            assmSetup = ComponentSetup.getSetupFromModoItem(modoItem)
            if assmSetup is not None:
                assmSetup.clearItem(hrchItems)
    
            # Determine to which assembly the item should be added.
            # By default it's setup's root assembly but if assemblyItem
            # argument is set to a child assembly of the setup's root assembly
            # we will add item to this child assembly instead.
            if assemblyItem is not None:
                modoxAssm = modox.Item(assemblyItem.internalItem)
                if not modoxAssm.isInHierarchy(self.rootAssembly):
                    assemblyItem = self.rootAssembly
            else:
                assemblyItem = self.rootAssembly
            assemblyItem.addItems(hrchItems)
        
            for item in hrchItems:
                self._sendItemAddedEvent(item)

    def removeItem(self, modoItems):
        """ Removes given item from the setup.
        
        This includes removing an item from setup's hierarchy.

        Paramters
        ---------
        modoItem : modo.Item, list of modo.Item
            Item to remove from the setup.
        """
        if type(modoItems) not in (list, tuple):
            modoItems = [modoItems]
        
        self.clearItem(modoItems)
        
        for modoItem in modoItems:
            modoItem.setParent(None)
        
        #if self.descSelfDestroyWhenEmpty and self.isEmpty:
            #self.selfDelete()

    def clearItem(self, modoItems):
        """ Clears an item from any association with the rig.
        
        Item(s) are removed from assembly but parenting relationship
        is not changed.
        
        Parameters
        ----------
        modoItems : modo.Item, list of modo.Item
        """
        if type(modoItems) not in (list, tuple):
            modoItems = [modoItems]
        
        for modoItem in modoItems:
            service.events.send(c.EventTypes.ITEM_REMOVED, item=modoItem)
            self._removeFromAssembly(modoItem)

        if self.descSelfDestroyWhenEmpty and self.isEmpty:
            self.selfDelete()
    
    def addSubAssembly(self, assmModoItems):
        """ Adds entire assemblies to setup as-is.
        
        This is for standard assemblies that are not component setups.
        
        Parameters
        ----------
        assmModoItems : modo.Item, list of modo.Item
        """
        if type(assmModoItems) not in (list, tuple):
            assmModoItems = [assmModoItems]
    
        for assm in assmModoItems:
            modox.Assembly.addSubassembly(assm, self.rootAssembly)
            modox.Assembly.iterateOverItems(assm, self._sendItemAddedEvent)

    def addSetup(self, setup):
        """ Adds another rig component setup to this setup.
        
        What it means in practice is that child setup's root item will be child
        of this setup root and child's setup assembly will be child of this
        setup assembly.
        
        Parameters
        ----------
        setup : ComponentSetup
            The setup to add to this setup.
        
        customGraph : str, optionsl
            When set the child setup will be linked to parent setup
            on this custom graph.
        """
        rootModoxItem = modox.Item(self.rootModoItem.internalItem)
        if not rootModoxItem.isInHierarchy(setup.rootModoItem):
            setup.rootModoItem.setParent(self.rootModoItem, index=-1)

        modox.Assembly.addSubassembly(setup.rootAssembly, self.rootAssembly)
        
        if setup.descLookupGraph:
            childSetupGraph = setup.rootModoItem.itemGraph(setup.descLookupGraph)
            parentSetupGraph = self.rootModoItem.itemGraph(setup.descLookupGraph)
            childSetupGraph >> parentSetupGraph

        self.iterateOverItems(self._sendItemAddedEvent)

    def _sendItemAddedEvent(self, modoItem):
        service.events.send(c.EventTypes.ITEM_ADDED, item=modoItem)

    def getSubsetupsOfType(self, setupClass):
        """ Gets all setups of a given type that are linked to this setup.
        
        Parameters
        ----------
        setupClass: ComponentSetup class, str
            Either setup class or setup string identifier.
        
        Returns
        -------
        list of ComponentSetup
            Empty list is returned when there are no subsetups.
        """
        if isinstance(setupClass, str):
            try:
                setupClass = service.systemComponent.get(c.SystemComponentType.COMPONENT_SETUP, setupClass)
            except LookupError:
                return []
        
        subsetups = []
        for modoItem in self.rootAssembly.children():
            try:
                setup = setupClass(modoItem)
            except TypeError:
                continue
            subsetups.append(setup)
        
        return subsetups

    @property
    def subsetups(self):
        """ Gets all the first level child subsetups of this setup.
        
        Returns
        -------
        list of ComponentSetup
            Subsetups are returned as proper setup classes.
        """
        subsetups = []
        for modoItem in self.rootAssembly.children():
            if not self._isSetupAssembly(modoItem):
                continue
            
            setupId = self._getSetupIdentifierFromModoItem(modoItem)
            if not setupId:
                continue
            try:
                setupClass = service.systemComponent.get(c.SystemComponentType.COMPONENT_SETUP, setupId)
            except LookupError:
                continue

            try:
                setup = setupClass(modoItem)
            except TypeError:
                continue
            subsetups.append(setup)
        
        return subsetups
    
    def getSubsetupsByGraph(self, graphName):
        """ Gets all subsetups that are linked to this setup via given graph.
        
        Parameters
        ----------
        graphName : str
        
        Returns
        -------
        list of ComponentSetup
        """
        graph = self._rootItem.itemGraph(graphName)
        connectedItems = graph.reverse()
        subsetups = []
        for item in connectedItems:
            subsetup = ComponentSetup.getSetupFromModoItem(item)
            if subsetup is not None:
                subsetups.append(subsetup)
        return subsetups
        
    def selfValidate(self):
        """ Validates itself to make sure the component setup has integrity.
        
        All locator items in the setup have to be both part of the assembly
        and the hierarchy under setup root.
        """
        log.startChildEntries()
        self.iterateOverItems(self._validateAssemblyItem)
        self.iterateOverHierarchy(self._validateHierarchyItem)
        log.stopChildEntries()

    def save(self, filename, thumbObject=None):
        """ Saves component setup as an assembly preset.
        
        Preset description will be taken from descPresetDescription attribute.

        Parameters
        ----------
        filename : str
            Complete filename (with path) for the assembly preset.
        
        Returns
        -------
        boolean
            True if preset was saved, False otherwise.
        """
        result = True

        if thumbObject is not None:
            thumbObject.capture()

        if self.descOnCreateDropScript is not None:
            modox.ItemUtils.setCreateDropScript(self.rootModoItem, self.descOnCreateDropScript)

        self.rootAssembly.select(replace=True)
        cmd = '!item.selPresetSave type:locator filename:{%s}' % filename
        if self.descPresetDescription:
            cmd += (' desc:{%s}' % self.descPresetDescription)

        try:
            lx.eval(cmd)
        except RuntimeError:
            result = False

        if thumbObject is not None:
            thumbObject.setOnPreset(filename)

        # Remove drop script after save.
        modox.ItemUtils.clearCreateDropScript(self.rootModoItem)

        return result

    def iterateOverSubassemblies(self, callback, recursive=True):
        """ Iterates over component setup subassemblies.

        Parameters
        ----------
        callback : function
            Function that will be called on each subassembly.
            This function should take modo.Item as its first and only argument.
            Callback can return True to terminate iteration at any step.
            Don't return any value to keep going through entire loop.
        """
        modox.Assembly.iterateOverSubassemblies(self.rootAssembly, callback, recursive)

    def iterateOverItems(self, callback, includeSubassemblies=True, assmTestCallback=None):
        """ Performs an operation on every component setup item.
        
        This includes root item and the assembly.

        Parameters
        ----------
        callback : function
            Function that will be called on each item.
            This function should take modo.Item as its first and only argument.
            Callback can return True to terminate iteration at any step.
            Don't return any value to keep going through entire loop.

        includeSubassemblies : bool, optional
            When True subassemblies will be included in iteration.
        
        assmTestCallback : function, optional
            Only relevant when includeSubassemblies is True.
            Pass callback if you want to test subassemblies before including their items in iteration.
            Callback needs to take single argument which is assembly modo item and return True or False.
            
            Parameters:
            assmModoItem : modo.Item
            
            Returns:
            bool : True to include subassembly, False otherwise.
        """
        modox.Assembly.iterateOverItems(self.rootAssembly,
                                        callback,
                                        includeSubassemblies=includeSubassemblies,
                                        assmTestCallback=assmTestCallback)

    def iterateOverHierarchy(self, callback, includeRoot=False):
        """ Iterates through xfrmcore supertype items that form the setup hierarchy.
        
        Root item is NOT included.
        
        Parameters
        ----------
        callback : function
            Function that will be called on each item.
            This function should take modo.Item as its first and only argument.
            Callback can return True to terminate iteration at any step.
            Don't return any value to keep going through entire loop.
        """
        items = modox.ItemUtils.getHierarchyRecursive(self.rootModoItem, includeRoot)
        for item in items:
            result = callback(item)
            if result:
                break

    @property
    def hierarchyItems(self):
        """ Returns a list of items that form setup hierarchy.
        """
        return modox.Item(self.rootModoItem).getOrderedHierarchy()

    def selfDelete(self):
        """ Deletes rig setup from scene.
        
        Do not use setup after it is deleted.
        """
        modox.Assembly.delete(self.rootAssembly)

    # -------- Private methods

    def _validateAssemblyItem(self, modoItem):
        """ Makes sure locator type items in assembly are also in the setup hierarchy.
        
        If an item that is in assembly is parented to an item outside of the assembly
        it is pulled into the assembly hierarchy.
        The exception is the root item of the setup itself.
        """
        modoxItem = modox.Item(modoItem.internalItem)
        if not modoxItem.isOfXfrmCoreSuperType:
            return

        # We need to skip setup root item, this one is not under the setup because
        # it's the setup root after all. Bad error happens if root item is processed.
        if modoItem == self.rootModoItem:
            return
        
        addToSetup = False
        parent = modoItem.parent
        if parent is None:
            addToSetup = True
        else:
            parentItemSetupRootItem = self._findSetupRootItem(parent)
            if parentItemSetupRootItem is None or parentItemSetupRootItem != self.rootModoItem:
                addToSetup = True
        
        if addToSetup:
            self.addItem(modoItem, addHierarchy=False)
            if debug.output:
                log.out("%s and its hierarchy were consolidated and parented under the setup root." % modoItem.name)

    def _validateHierarchyItem(self, modoItem):
        """ Validates item in rig hierarchy.
        
        Item needs to be in the hierarchy and assembly of the same setup.
        If it's not - it's added to the assembly of a setup in which hierarchy it's in.
        """
        if modoItem == self.rootModoItem:
            return

        addToSetup = False
        setupRootModoItem = self._findSetupRootItem(modoItem)
        if setupRootModoItem is None or setupRootModoItem != self.rootModoItem:
            addToSetup = True

        if addToSetup:
            setup = ComponentSetup.getSetupFromItemInSetupHierarchy(modoItem)
            if setup is not None:
                setup.addItem(modoItem, addHierarchy=True)
                if debug.output:
                    log.out("%s item was part of hierarchy but not in setup assembly. Fixed." % (modoItem.name))

    def _removeFromAssembly(self, modoItem):
        """ The assembly is not necessarily root assembly.
        It can be a child assembly as well.
        We need to check all the assemblies the item is connected to.
        Disconnect item from any assemblies that are part of this setup
        assemblies hierarchy.
        """
        itemGroupsGraph = modoItem.itemGraph('itemGroups')
        connectedGroups = itemGroupsGraph.reverse()
        for group in connectedGroups:
            mxGroup = modox.Item(group.internalItem)
            rootAssm = self.rootAssembly
            if group == rootAssm or mxGroup.isInHierarchy(rootAssm):
                group.removeItems(modoItem)

    @classmethod
    def _findSetupRootItem(self, modoItem):
        """ Finds setup root item starting from given item.
        
        The item has to be part of setup assembly (or one of its
        subassemblies) or a setup assembly or its subassembly.
        The item is not considered to be a part of rig otherwise.
        
        Returns
        -------
        modo.Item
            None if setup root could not be found.
        """

        # Check if the item passed is either setup root or a group that
        # is either setup assembly or some other group within the setup.
        if self._isSetupRoot(modoItem):
            return modoItem
        modoxItem = modox.Item(modoItem.internalItem)
        if modoxItem.typeRaw == 'group':
            return self._findSetupRootItemFromGroup(modoItem)
        
        rootItem = None
        connectedGroups = modoItem.connectedGroups # this will be None when there are no groups connected
        if connectedGroups is not None:
            for itemGroup in modoItem.connectedGroups:
                rootItem = self._findSetupRootItemFromGroup(itemGroup)
                if rootItem is not None:
                    break

        return rootItem

    @classmethod
    def _findRootItemByHierarchy(self, modoItem):
        """ Finds setup root item for a given item by looking up its hierarchy.
        """
        while modoItem is not None:
            if self._isSetupRoot(modoItem):
                return modoItem
            modoItem = modoItem.parent

    @classmethod
    def _isSetupRoot(self, modoItem):
        """ Tests if given item is this setup root.
        
        For base class the test will be true for a root item of any component setup.
        When setup has identifier - the test will only be true if the item
        is root of a setup with that identifier.
        """
        try:
            setupGraph = modoItem.itemGraph(self.GRAPH_SETUP)
            assembly = setupGraph.forward(0)
        except LookupError:
            return False
        
        if not self.descIdentifier:
            return True
        
        identInTag = self._getSetupIdentifierFromModoItem(modoItem)
        return identInTag == self.descIdentifier

    @classmethod
    def _getSetupIdentifierFromModoItem(self, rootModoItem):
        """ Returns value of the setup identifier tag on a modo item.
        
        Returns
        -------
        str
            The identifier string or empty string if item has no
            identifier.
        """
        try:
            return rootModoItem.readTag(self.TAG_IDENTIFIER)
        except LookupError:
            pass
        return ''

    @classmethod
    def _isSetupAssembly(self, modoItem):
        """ Tests whether given item is setup assembly.
        
        The test is passed when assembly item has a link
        on setup graph.
        """
        if modoItem.type != 'assembly':
            return
        try:
            setupGraph = modoItem.itemGraph(self.GRAPH_SETUP)
            assembly = setupGraph.reverse(0)
        except LookupError:
            return False
        return True

    @classmethod
    def _findSetupRootItemFromGroup(self, modoGroup):
        """ Given group item find its assembly root item for the setup.
        """
        thisSetupRoot = None
        while modoGroup is not None:
            try:
                setupGraph = modoGroup.itemGraph(self.GRAPH_SETUP)
                setupRoot = setupGraph.reverse(0)
            except LookupError:
                setupRoot = None
            
            if setupRoot is not None:
                result = self._isSetupRoot(setupRoot)
                if result:
                    thisSetupRoot = setupRoot
                    break

            modoGroup = modoGroup.parent
            continue

        return thisSetupRoot

    def __init__ (self, modoItem):
        rootModoItem = self._findSetupRootItem(modoItem)
        if rootModoItem is None:
            raise TypeError
        self._rootItem = rootModoItem
        
    def __str__ (self):
        return "Rig Component Setup: " + self.descUsername + " on item: " + self.rootModoItem.name

    def __eq__(self, other):
        """ Setups are equal if their root items are the same.
        """
        if other is None:
            return False
        return ((self.rootModoItem == other.rootModoItem) and 
                (self.rootAssembly == other.rootAssembly))