

import lx
import modo
import modox

from .item import Item
from .items.root_item import RootItem
from .items.deform_stack import DeformStackRootItem
from .items.deform_stack import NormalizingFolderItem
from .items.deform_stack import PostCorrectiveMorphsFolderItem
from . import const as c


class StackOrder(object):
    POST = 'post'
    PRE = 'pre'
    NORMALIZED = 'norm'
    OOO = 'ooo'
    POST_MORPHS = 'mpost'


class DeformStack(object):
    """ Deform stack represents entire deformers stack for a rig.
    """

    Order = StackOrder
    
    GRAPH_DEFORM_STACK = 'rs.deformStack'
    
    SETTINGS_GROUP = 'dfrms'
    SETTING_ORDER = 'order'

    SINGLETONS = [c.RigItemType.POST_CORRECTIVE_MORPHS_FOLDER,
                  c.RigItemType.NORMALIZING_FOLDER]
    SINGLETON_TO_ORDER = {c.RigItemType.NORMALIZING_FOLDER: Order.NORMALIZED,
                          c.RigItemType.POST_CORRECTIVE_MORPHS_FOLDER: Order.POST_MORPHS}

    @classmethod
    def new(cls, rigRootItem):
        """
        Parameters
        ----------
        rigRootItem : RootItem
        """
        deformRoot = DeformStackRootItem.new()

        # Link bind setup root folder with the root item
        rootGraph = deformRoot.modoItem.itemGraph(cls.GRAPH_DEFORM_STACK)
        rigGraph = rigRootItem.modoItem.itemGraph(cls.GRAPH_DEFORM_STACK)
        rootGraph >> rigGraph

        ## Set up deform folders structure.
        # post corrective morphs folder
        # normalizing folder
        postMorphsFolder = PostCorrectiveMorphsFolderItem.new()
        lx.eval('!deformer.setGroup deformer:{%s} group:{%s}' % (postMorphsFolder.modoItem.id, deformRoot.modoItem.id))
        normFolder = NormalizingFolderItem.new()
        lx.eval('!deformer.setGroup deformer:{%s} group:{%s}' % (normFolder.modoItem.id, deformRoot.modoItem.id))

        return cls(rigRootItem)

    @property
    def rootItem(self):
        """ Gets deformers stack root item.
        
        Returns
        -------
        DeformStackRootItem, None
        """
        graph = self._rigRoot.modoItem.itemGraph(self.GRAPH_DEFORM_STACK)
        try:
            root = graph.reverse(0)
        except LookupError:
            return None
        
        return DeformStackRootItem(root)

    @property
    def postCorrectiveMorphsFolder(self):
        """ Gets post corrective morphs folder item.

        Returns
        -------
        Item

        Raises
        ------
        LookupError
        """
        normItem = self._getSingleton(c.RigItemType.POST_CORRECTIVE_MORPHS_FOLDER)
        if normItem is None:
            raise LookupError
        return normItem

    @property
    def normalizingFolder(self):
        """ Gets normalizing folder item.

        Returns
        -------
        Item

        Raises
        ------
        LookupError
        """
        normItem = self._getSingleton(c.RigItemType.NORMALIZING_FOLDER)
        if normItem is None:
            raise LookupError
        return normItem

    @property
    def modoItems(self):
        """ Gets all the deformer stack items, including root.
        """
        return self._tree
    
    def addToStack(self, deformFolder, order):
        """ Adds given deform folder to the stack.
        
        Paramters
        ---------
        deformFolder : modo.Item, Item
            Either modo.Item or rig item class inheriting from Item.

        order : DeformStack.Order.XXX
            Defines whether deform folder should be added to normalized folder,
            pre normalization stack or post normalization stack.
        
        Raises
        ------
        TypeError
            When item of wrong type was passed. Only DeformFolderItem items are allowed.
        """
        if not issubclass(deformFolder.__class__, Item):
            try:
                deformFolder = Item.getFromModoItem(deformFolder)
            except TypeError:
                raise

        if order == self.Order.NORMALIZED:
            try:
                normFolder = self._getSingleton(c.RigItemType.NORMALIZING_FOLDER)
            except LookupError:
                return

            lx.eval('!deformer.setGroup deformer:{%s} group:{%s}' % (deformFolder.modoItem.id, normFolder.modoItem.id))

        elif order == self.Order.POST_MORPHS:
            try:
                postMorphFolder = self._getSingleton(c.RigItemType.POST_CORRECTIVE_MORPHS_FOLDER)
            except LookupError:
                return

            lx.eval('!deformer.setGroup deformer:{%s} group:{%s}' % (deformFolder.modoItem.id, postMorphFolder.modoItem.id))

    def storeStackOrder(self):
        """ Stores the order of deform folders in the stack.
        
        Each deform folder is identified and its order in a stack is stored
        on the item itself. The order really means storing under which singleton
        in the deformers tree given deform folder is.
        If deform folder is not directly under any of singletons it is skipped.
        """
        for item in self._tree:
            if item.type != 'deformFolder':
                continue
            try:
                rigItem = Item.getFromModoItem(item)
            except TypeError:
                continue
            singleton = self._getParentSingleton(rigItem.modoItem)
            if singleton is None:
                continue
            order = self.SINGLETON_TO_ORDER[singleton.type]
            rigItem.settings.setInGroup(self.SETTINGS_GROUP, self.SETTING_ORDER, order)

    def restoreStackOrder(self, deformFolders):
        """ Restores stack order for given deform folders.
        
        Paramters
        ---------
        deformFolders : list of modo.Item, Item
        """
        if type(deformFolders) not in (list, tuple):
            deformFolders = [deformFolders]
        
        for deformFolder in deformFolders:
            if not issubclass(deformFolder.__class__, Item):
                try:
                    deformFolder = Item.getFromModoItem(deformFolder)
                except TypeError:
                    raise
            
            order = deformFolder.settings.getFromGroup(self.SETTINGS_GROUP, self.SETTING_ORDER)
            if order is not None:
                self.addToStack(deformFolder, order)

    def clearStackOrder(self):
        for item in self._tree:
            if item.type != 'deformFolder':
                continue
            try:
                rigItem = Item.getFromModoItem(item)
            except TypeError:
                continue
            rigItem.settings.deleteGroup(self.SETTINGS_GROUP)

    # -------- Private methods

    @property
    def _tree(self):
        """ Gets deformers tree for this stack.
        """
        root = self.rootItem
        if root is None:
            return []
        return modox.DeformersStack.getDeformTree(root.modoItem, includeRoot=True)

    def _getSingleton(self, identifier):
        """ Gets a key item with a given identifier from the stack.
        
        Always use this method to get a key item.

        Parameters
        ----------
        identifier : str
            One of singleton item types defined in self.SINGLETONS.

        Returns
        -------
        Item

        Raises
        ------
        LookupError
        """
        if self.__singletons is None:
            self._cacheSingletons()
        try:
            return self.__singletons[identifier]
        except KeyError:
            raise LookupError

    def _cacheSingletons(self):
        if self.__singletons is not None:
            return

        self.__singletons = {}
        for item in self.modoItems:
            try:
                rigItem = Item.getFromModoItem(item)
            except TypeError:
                continue
            if rigItem.type in self.SINGLETONS:
                self.__singletons[rigItem.type] = rigItem

    def _getParentSingleton(self, modoItem):
        """ Gets singleton parent to the given item.
        
        If there is no parent or parent is not a singleton None is returned.
        
        Returns
        -------
        Singleton, None
        """
        parentSingleton = modox.DeformersStack.getParent(modoItem)

        try:
            rigItem = Item.getFromModoItem(parentSingleton)
        except TypeError:
            return None
        
        if rigItem.type in self.SINGLETONS:
            return rigItem
        return None

    def __init__(self, rigRootItem):
        if not isinstance(rigRootItem, RootItem):
            try:
                rigRootItem = RootItem(rigRootItem)
            except TypeError:
                raise
        self._rigRoot = rigRootItem
        self.__singletons = None