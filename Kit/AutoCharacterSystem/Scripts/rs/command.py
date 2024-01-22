
""" Base implementation of Rigging System commands.

    Use this class for all Rigging System commands.
"""


import lxu
import modo
import modox
from modox.command import bless
from modox.command import Argument
from modox.command import ArgumentItemsContent
from modox.command import ArgumentPopupContent
from modox.command import ArgumentPopupEntry
from modox.command import ArgumentValuesListType
from .items.root_item import RootItem
from .items.module_root import ModuleRoot
from .module_op import ModuleOperator
from .context_op import ContextOperator
from .rig import Rig
from .module import Module
from .item import Item
from .item_feature_op import ItemFeatureOperator
from .item_feature import ItemFeature
from .scene import Scene
from .core import service
from .log import log
from . import const as c


class Command(modox.Command):
    
    def notifiers(self):
        return [('rs.ui.general',''),
                ('graphs.event', 'rs.metaRig +d'),
                ('graphs.event', 'parent +d'),
                ('select.event', 'cinema +d')]

    def enable(self, msg):
        v = Scene.anyRigsInSceneFast()
        if not v:
            msg.set(c.MessageTable.DISABLE, c.MessageKey.NO_RIGS)
        return v

    def stopListeners(self):
        """ Stops rigging system listeners for the execution of the command.
        
        This is true by default and should be True in most cases.
        Leaving listeners on while rs command is being executed can really mess
        things up so use this with caution.
        """
        return True

    def executeStart(self):
        if self.stopListeners():
            self._bkpListenToScene = service.listenToScene
            service.listenToScene = False

        self._setContext(self.setContextPre())
        
    def executeEnd(self):
        if self.stopListeners():
            service.listenToScene = self._bkpListenToScene

    def setContextPre(self):
        """ Allows for setting specific context before command execution.
        
        Returns
        -------
        str, None
            Either context identifier or None if command does not affect context.
        """
        return None

    # -------- Private methods
    
    def _setContext(self, contextIdent):
        if contextIdent is None:
            return

        currentContextIdent = ContextOperator.getContextIdentFast()
        if contextIdent == currentContextIdent:
            return
        
        try:
            ContextOperator(Scene()).current = contextIdent
        except TypeError:
            pass


class RigCommand(Command):
    """ Base class for commands that apply to rig(s).
    
    Note that this command requires the rootItem argument that it defines.
    Be sure to include it in the list of arguments.
    The order doesn't matter although you probably want that argument to be last one.
    Here's an example of how arguments() can work:
    
        superArgs = rs.RigCommand.arguments(self)
        args = [arg1, arg2]
        return args + superArgs
    """
    
    ARG_ROOT_ITEM = 'rootItem'

    def arguments(self):        
        root = Argument(self.ARG_ROOT_ITEM, '&item')
        root.flags = ['optional', 'hidden']
        return [root]

    @property
    def rigToQuery(self):
        """ Gets single rig the query should be based on.
        
        Returns
        -------
        Rig
        """
        # If rig root item is set directly - use that.
        if self.isArgumentSet(self.ARG_ROOT_ITEM):
            rootIdent = self.getArgumentValue(self.ARG_ROOT_ITEM)
            return Rig(rootIdent)
            
        # If not, find rig in selection
        rawItem = modox.ItemSelection().getLastOfTypeRaw(RootItem.descModoItemType)
        if rawItem is not None:
            try:
                rootItem = RootItem(rawItem)
                return Rig(rootItem)
            except TypeError:
                pass

        # If not, try current edit rig.
        editRig = Scene().editRig
        if editRig is not None:
            return editRig
    
        return None
    
    @property
    def firstRigToEdit(self):
        """ Gets first rig to edit.
        
        Use this if the command can work on a single edit rig and does not support multiselection.
        
        Returns
        -------
        Rig
        """
        return self.rigToQuery

    @property
    def rigsToEdit(self):
        """ Gets a list of modules the command should operate on.
        
        Returns
        -------
        list of Rig
        """
        # If rig root item is set directly - use that.
        if self.isArgumentSet(self.ARG_ROOT_ITEM):
            rootIdent = self.getArgumentValue(self.ARG_ROOT_ITEM)
            return [Rig(rootIdent)]
            
        # If not, find rig in selection
        rawItems = modox.ItemSelection().getOfTypeRaw(RootItem.descModoItemType)
        if rawItems:
            rigs = []
            for rawItem in rawItems:
                try:
                    rigs.append(Rig(rawItem))
                except TypeError:
                    pass
    
            return rigs
            
        # If not, try current edit rig.
        editRig = Scene().editRig
        if editRig is not None:
            return [editRig]
    
        return []
        

class base_OnModuleCommand(Command):
    """ Base class for commands that apply to module(s).
    
    Note that this command requires the rootItem argument that it defines.
    Be sure to include it in the list of arguments.
    The order doesn't matter although you probably want that argument to be last one.
    Here's an example of how arguments() can work:
    
        superArgs = rs.base_OnModuleCommand.arguments(self)
        args = [arg1, arg2]
        return args + superArgs
    """
    
    ARG_ROOT_ITEM = 'rootItem'

    def arguments(self):        
        root = Argument(self.ARG_ROOT_ITEM, '&item')
        root.flags = ['optional', 'hidden']
        
        return [root]

    @property
    def moduleToQuery(self):
        """ Gets single module the query should be based on.
        
        Returns
        -------
        Module
        """
        # If rig root item is set directly - use that.
        if self.isArgumentSet(self.ARG_ROOT_ITEM):
            rootIdent = self.getArgumentValue(self.ARG_ROOT_ITEM)
            return Module(rootIdent)
            
        # If not, find rig in selection
        rawItem = modox.ItemSelection().getLastOfTypeRaw(ModuleRoot.descModoItemType)
        if rawItem is not None:
            try:
                rootItem = ModuleRoot(rawItem)
                return Module(rootItem)
            except TypeError:
                pass

        # If not, try current edit module.
        editRoot = Scene.getEditRigRootItemFast()
        if editRoot is None:
            return None

        modulesOp = ModuleOperator(editRoot)
        editModule = modulesOp.editModule
        if editModule is not None:
            return editModule
    
        return None

    @property
    def firstModuleToEdit(self):
        """ Gets first module to edit.

        Use this if the command can work on a single edit module and does not support multiselection.

        Returns
        -------
        Rig
        """
        return self.moduleToQuery

    @property
    def modulesToEdit(self):
        """ Gets a list of modules that should be edited.
        
        Returns
        -------
        list of Module
        """
        # If rig root item is set directly - use that.
        if self.isArgumentSet(self.ARG_ROOT_ITEM):
            rootIdent = self.getArgumentValue(self.ARG_ROOT_ITEM)
            return [Module(rootIdent)]
            
        # If not, find rig in selection
        rawItems = modox.ItemSelection().getOfTypeRaw(ModuleRoot.descModoItemType)
        if rawItems:
            modules = []
            for rawItem in rawItems:
                try:
                    modules.append(Module(rawItem))
                except TypeError:
                    pass
    
            return modules
            
        # If not, try current edit module.
        editRoot = Scene.getEditRigRootItemFast()
        if editRoot is None:
            return 0

        modulesOp = ModuleOperator(editRoot)
        editModule = modulesOp.editModule
        if editModule is not None:
            return [editModule]

        return []


class base_OnItemCommand(Command):
    """ Base class for commands that apply to item(s).
    
    Note that this command requires the rootItem argument that it defines.
    Be sure to include it in the list of arguments.
    The order doesn't matter although you probably want that argument to be last one.
    Here's an example of how arguments() can work:
    
        superArgs = rs.base_OnItemCommand.arguments(self)
        args = [arg1, arg2]
        return args + superArgs
        
    Attributes
    ----------
    descItemClassOrIdentifier : Item class, str
        If command can work on specific type of item only define this attribute.
        The attribute can be the item class directly or its type identifier.
    """
    
    # -------- Attributes
    
    descItemClassOrIdentifier = None

    # -------- Interface
    
    ARG_ITEM = 'item'
        
    def arguments(self):        
        itemArg = Argument(self.ARG_ITEM, '&item')
        itemArg.flags = 'optional'
        
        return [itemArg]

    @property
    def itemToQuery(self):
        """ Gets single item the query should be based on.
        
        It will get either a first available rig item or first
        rig item of a given type if descItemClassOrIdentifier is set.

        Returns
        -------
        Item, None
        """
        # If item ident is set directly - use that.
        if self.isArgumentSet(self.ARG_ITEM):
            return self._getItemFromArgument()
            
        # If not, find rig in selection.
        # We take last compatible item from selection.
        itemSel = modox.ItemSelection()
        selCount = itemSel.size

        cls = self._getItemClass()
        for x in range(selCount - 1, -1, -1):
            rawItem = itemSel.getRawByIndex(x)

            if cls is None:
                # get item type dynamically from raw item.
                try:
                    return Item.getFromOther(rawItem)
                except TypeError:
                    continue
            else:
                try:
                    return cls(rawItem)
                except TypeError:
                    continue
    
        return None
    
    @property
    def itemsToEdit(self):
        """ Gets a list of items that should be edited.
        
        Returns
        -------
        list of Item
        """
        # If rig root item is set directly - use that.
        if self.isArgumentSet(self.ARG_ITEM):
            item = self._getItemFromArgument()
            if item is None:
                return []
            else:
                return [item]

        items = []
        cls = self._getItemClass()
        if cls is not None:
            # We want specific items only.
            if cls.descModoItemType is not None:
                rawItems = modox.ItemSelection().getOfTypeRaw(cls.descModoItemType)
            else:
                rawItems = modox.ItemSelection().getRaw()
            for rawItem in rawItems:
                try:
                    items.append(cls(rawItem))
                except TypeError:
                    continue
        else:
            # all rig items really.
            for item in modox.ItemSelection().getRaw():
                try:
                    items.append(Item.getFromOther(item))
                except TypeError:
                    continue

        return items
    
    # -------- Private methods
    
    def _getItemFromArgument(self):
        itemIdent = self.getArgumentValue(self.ARG_ITEM)
        scene = lxu.select.SceneSelection().current()
        try:
            item = scene.ItemLookup(itemIdent)
        except LookupError:
            return None
        cls = self._getItemClass()
        if cls is None:
            return None
        try:
            return cls(item)
        except TypeError:
            return None 
        return None

    def _getItemClass(self):
        classOrIdentifier = self.descItemClassOrIdentifier
        if classOrIdentifier is None:
            return None
        elif isinstance(classOrIdentifier, str):
            try:
                return service.systemComponent.get(c.SystemComponentType.ITEM, classOrIdentifier)
            except LookupError:
                return None
        elif issubclass(classOrIdentifier, Item):
            return classOrIdentifier
        return None


class base_OnItemFeatureCommand(Command):
    """ Base class for commands that apply to item feature(s).
    
    Note that this command requires the item argument that it defines.
    Be sure to include it in the list of arguments.
    The order doesn't matter although you probably want that argument to be last one.
    Here's an example of how arguments() can work:
    
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
        args = [arg1, arg2]
        return args + superArgs
        
    Attributes
    ----------
    descIFClassOrIdentifier : Item class, str
        Set this attribute to either item feature identifier or its class.
        The command will work on this feature only when attribute is set.
    """
    
    # -------- Attributes
    
    descIFClassOrIdentifier = None

    # -------- Interface
    
    ARG_ITEM = 'item'
        
    def arguments(self):        
        itemArg = Argument(self.ARG_ITEM, '&item')
        itemArg.flags = 'optional'
        
        return [itemArg]

    @property
    def itemFeatureOperatorToQuery(self):
        return self._getObjectToQuery(ItemFeatureOperator)

    @property
    def itemFeatureToQuery(self):
        """ Gets single item feature the query should be based on.
        
        It will get either a first available rig item or first
        rig item of a given type if descItemClassOrIdentifier is set.

        Returns
        -------
        Item, None
        """
        objectClass = self._getItemFeatureClass()
        return self._getObjectToQuery(objectClass)
    
    @property
    def itemFeaturesToEdit(self):
        """ Gets a list of items that should be edited.
        
        Returns
        -------
        list of ItemFeature
        """
        cls = self._getItemFeatureClass()
        if cls is None:
            return []
        
        # If rig root item is set directly - use that.
        if self.isArgumentSet(self.ARG_ITEM):
            item = self._getItemFromArgument()
            if item is None:
                return []
            try:
                return [cls(item)]
            except TypeError:
                return []

        items = []

        rawItems = modox.ItemSelection().getRaw()
        for rawItem in rawItems:
            try:
                items.append(cls(rawItem))
            except TypeError:
                continue

        return items
    
    @property
    def itemsToEdit(self):
        """ Gets a list of items that should be edited.
        """
        # If item is set directly - use that.
        if self.isArgumentSet(self.ARG_ITEM):
            item = self._getItemFromArgument()
            if item is None:
                return []
            else:
                return [item]
        
        # TODO: This should really filter out items that are not compatible with the feature.
        return modox.ItemSelection().getRaw()
        
    # -------- Private methods

    def _getObjectToQuery(self, objectClass):
        """ Gets first object from argument or selection that has the objectClass interface.
        
        Parameters
        ----------
        objectClass : ItemFeature, ItemFeatureOperator
        
        Returns
        -------
        Object, None
        """
        # If item ident is set directly - use feature from that item.
        if self.isArgumentSet(self.ARG_ITEM):
            item = self._getItemFromArgument()
            if item is None:
                return None
            try:
                return objectClass(item)
            except TypeError:
                return None

        # If not, find item in selection.
        # We take last compatible item from selection.
        itemSel = modox.ItemSelection()
        selCount = itemSel.size
        
        for x in range(selCount - 1, -1, -1):
            rawItem = itemSel.getRawByIndex(x)

            try:
                return objectClass(rawItem)
            except TypeError:
                continue

        return None

    def _getItemFromArgument(self):
        """ Gets raw item from argument if one was set.
        
        Returns
        -------
        lxu.object.Item
        """
        
        itemIdent = self.getArgumentValue(self.ARG_ITEM)
        scene = lxu.select.SceneSelection().current()
        try:
            return scene.ItemLookup(itemIdent)
        except LookupError:
            pass
        return None

    def _getItemFeatureClass(self):
        """ Gets item feature class based on the descIFClassOrIdentifier attribute.
        """
        classOrIdentifier = self.descIFClassOrIdentifier
        if classOrIdentifier is None:
            return None
        if isinstance(classOrIdentifier, str):
            try:
                return service.systemComponent.get(c.SystemComponentType.ITEM_FEATURE, classOrIdentifier)
            except LookupError:
                return None
        elif ItemFeature in classOrIdentifier.__mro__: # __mro__ gets a tuple with all the parent classes for a given class
            return classOrIdentifier
        return None