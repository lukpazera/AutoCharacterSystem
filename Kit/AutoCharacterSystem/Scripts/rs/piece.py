

import lx
import modo
import modox

from . import const as c
from .util import run
from .core import service
from .log import log
from .item import Item
from .transmit import ConnectionsCache
from .items.module_sub import GuideAssembly


class PieceAssembly(Item):
    
    descType = 'pieceassm'
    descUsername = 'Piece Assembly Item'
    descModoItemType = 'group'
    descModoItemSubtype = 'assembly'
    descDefaultName = 'Piece'
    descPackages = ['rs.pkg.piece', 'rs.pkg.generic']
    descDropScriptCreate = 'rs_drop_piece'
       
    def onAdd(self, subtype):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor orange')

    @property
    def inputChannels(self):
        """ Gets input channels for the piece assembly.
        
        This property is required for ConnectionsCache to work.
        ConnectionsCache will call this to get the input channels to cache.
        
        Returns
        -------
        list of modo.Channel
        """
        return modox.Assembly.getInputChanels(self.modoItem)
    
    @property
    def outputChannels(self):
        """ Gets output channels for the piece assembly.
        
        This property is required for ConnectionsCache to work.
        ConnectionsCache will call this to get the output channels to cache.

        Returns
        -------
        list of modo.Channel
        """        
        return modox.Assembly.getOutputChannels(self.modoItem)


class Piece(object):
    """ Piece is an assembly within module that can be added/removed from module dynamically.
    
    Pieces can be either singletons (only one piece of a given type can be in module)
    or serial pieces which can be added many times.
    
    Serial pieces have all the same identifier by they get unique index assigned.
    Indexing pieces starts from 1.
    
    Singleton piece will have index of 1 by default.

    Parameters
    ----------
    initialiser : PieceAssembly
    """
    
    _SETTING_INDEX = 'ix'
    _CHAN_CACHE_ON_SAVE = 'rspcCache'
    _SEPARATOR = '_'
    _SETTING_REFERENCE_SIZE = 'refsize'

    # -------- Public interface
    
    @classmethod
    def new(cls, name, module=None):
        """ Spawns new piece into the scene.
        
        This really adds just the piece assembly item.
        
        Parameters
        ----------
        name : str
        
        module : Module, None, optional
        """
        # Adds new piece assembly item.
        pieceAssm = PieceAssembly.new(name)
        
        # Add assembly manually to module setup.
        # This should be covered by ComponentSetup.addItem but it's not...
        if module is not None:
            modox.Assembly.addSubassembly(pieceAssm.modoItem, module.setup.rootAssembly)
        
        return Piece(pieceAssm)
        
    @classmethod
    def load(cls, identifier, moduleIdentifier, componentSetup, updateNames=False):
        """ Loads piece from assembly preset into the scene.
        
        Parameters
        ----------
        identifier : str
            Identifier of piece to load.
        
        moduleIdentifier : str
            Identifier of the module the piece belongs to.

        componentSetup : modo.Item
            Pieces cannot exist on their own. You have to pass component setup
            which the piece will be part of.
        """
        moduleIdentifier = moduleIdentifier.replace(".", cls._SEPARATOR)
        identifier = identifier.replace(".", cls._SEPARATOR)
        filename = moduleIdentifier + cls._SEPARATOR + identifier
        lowFilename = filename.lower()
        if not lowFilename.endswith('.lxp'):
            filename += '.lxp'
        
        try:
            fullFilename = service.path.getFullPathToFile(c.Path.PIECES, filename)
        except LookupError:
            raise

        run('preset.do {%s}' % fullFilename)
        try:
            pieceAssmId = service.buffer.take('pieceId')
        except LookupError:
            log.out("Piece: {%s} was not loaded, check if it's a valid file!" % fullFilename, log.MSG_ERROR)
            raise
        try:
            piece = cls(modo.Scene().item(pieceAssmId))
        except TypeError:
            raise LookupError
        
        # Restore hierarchy and input/output connections if there's a cache.
        # Ugly code, needs rearranging.
        if piece.cacheOnSave:
            piece._restoreHierarchyFromCache(componentSetup)
            connections = ConnectionsCache(piece.assemblyItem)
            connections.restoreConnections(componentSetup)
            piece._clearCache()

        componentSetup.addSubAssembly(piece.assemblyModoItem)

        if updateNames:
            piece.updateNames()

        service.events.send(c.EventTypes.PIECE_LOAD_POST, piece=piece)

        return piece
    
    @property
    def identifier(self):
        """ Gets piece identifier.
        
        It really is just taking the identifier of the piece main assembly item.
        """
        return self._assmItem.identifier

    @property
    def index(self):
        return self.settings.get(self._SETTING_INDEX, 1) # default 1 means the pieces is not indexed yet.

    @index.setter
    def index(self, value):
        """ Gets/sets module piece index.
        
        Index is used for numbering pieces when there are multiple instances of the same piece
        within the module. By default, pieces have an index of 1.

        Parameters
        ----------
        value : int
        
        Returns
        -------
        int
        """
        self.settings.set(self._SETTING_INDEX, value)
    
    @property
    def cacheOnSave(self):
        return self.assemblyItem.getChannelProperty(self._CHAN_CACHE_ON_SAVE)
    
    @cacheOnSave.setter
    def cacheOnSave(self, state):
        self.assemblyItem.setChannelProperty(self._CHAN_CACHE_ON_SAVE, state)
        
        if not state:
            self._clearCache()
        
    @property
    def keyItems(self):
        """ Gets a all key items of a piece as a dictionary.
        
        Returns
        -------
        dict{str identifier:Item}
        """
        if self._keyItems is None:
            self._keyItems = {}
            modox.Assembly.iterateOverItems(self._assmItem.modoItem, self._scanKeyItem, includeSubassemblies=True)
        return self._keyItems
    
    def getKeyItem(self, keyItemIdent):
        """ Gets key item with a given identifier.
        
        Returns
        -------
        Item
        
        Raises
        ------
        LookupError
        """
        try:
            return self.keyItems[keyItemIdent]
        except KeyError:
            raise LookupError
        raise LookupError

    def getKeyChannel(self, keyItemIdent, channelName):
        """ Gets a channel from a key item.
        
        Parameters
        ----------
        keyItemIdent : str
            identifier of the key item.
            
        channelName : str
        
        Returns
        -------
        modo.Channel
        
        Raises
        ------
        LookupError
            When channel cannot be found.
        """
        try:
            chan = self.keyItems[keyItemIdent].modoItem.channel(channelName)
        except KeyError:
            raise LookupError
        if chan is None:
            raise LookupError
        return chan
    
    @property
    def assemblyItem(self):
        """ Gets piece's assembly item as PieceAssembly.
        
        Returns
        -------
        Piece Assembly
        """
        return self._assmItem

    @property
    def assemblyModoItem(self):
        """ Gets piece's assembly modo item.
        
        Returns
        -------
        modo.Item
        """
        return self._assmItem.modoItem

    @property
    def guideAssembly(self):
        """
        Gets piece's guide assembly.

        We assume there's only one in each piece and it's parented right under the piece assembly.
        It cannot be nested deeper.

        Returns
        -------
        GuideAssembly, None
        """
        # TODO: This can be made potentially faster when iterating and stopping iteration when guide assm is found.
        subassms = modox.Assembly.getSubassemblies(self.assemblyModoItem, recursive=False)
        for assm in subassms:
            try:
                return GuideAssembly(assm)
            except TypeError:
                pass
        return None

    @property
    def settings(self):
        """ Gives access to piece item settings.
        """
        return self._assmItem.settings

    @property
    def moduleRootItem(self):
        return self._assmItem.moduleRootItem
    
    @property
    def rigRootItem(self):
        return self._assmItem.rigRootItem

    @property
    def referenceSize(self):
        """
        Gets piece reference size.

        Returns
        -------
        float
            When no reference size is set, default value is returned.
        """
        return self._assmItem.settings.get(self._SETTING_REFERENCE_SIZE, c.DefaultValue.REFERENCE_SIZE)

    @referenceSize.setter
    def referenceSize(self, newSize):
        """
        Sets piece reference size.

        Parameters
        ----------
        newSize : float
        """
        self._assmItem.settings.set(self._SETTING_REFERENCE_SIZE, newSize)

    def iterateOverItems(self, callback, includeSubassemblies=True, assmTestCallback=None):
        """ Iterates over all piece items.
        """
        modox.Assembly.iterateOverItems(self._assmItem.modoItem,
                                        callback,
                                        includeSubassemblies=includeSubassemblies,
                                        assmTestCallback=assmTestCallback)

    def updateNames(self):
        """
        Updates names of all piece items.

        Typically you want to do this when piece is loaded into scene.
        """
        self.iterateOverItems(self._updateItemName, includeSubassemblies=True, assmTestCallback=None)

    def save(self, filename=None):
        """ Saves piece to given filename or to default pieces location.
        
        Piece filename is generated from this pattern:
        module_identifier.parent_piece_identifier.piece.identifier
        
        When there is no parent piece this token is skipped.

        Raises
        ------
        RuntimeError
            When piece cannot be saved.
        """
        if self.cacheOnSave:
            self._cache()
        else:
            # clear cache here.
            self._clearCache()
        
        if filename is None:
            ident = self.identifier
            if not ident:
                return False
            try:
                modIdent = self.moduleRootItem.identifier
            except AttributeError:
                log.out("Piece is not part of any module and it cannot be saved correctly!", log.MSG_ERROR)
                raise RuntimeError

            # Get parent piece, if any.
            parentPieceIdent = None
            parentPiece = self.parentPiece
            if parentPiece is not None:
                parentPieceIdent = parentPiece.identifier

            filename = modIdent
            if parentPieceIdent is not None:
                filename += self._SEPARATOR + parentPieceIdent
            filename += self._SEPARATOR + ident
            filename = filename.replace(".", self._SEPARATOR) # dots not allowed in piece file name!!!
            filename += '.lxp'
            filename = service.path.generateFullFilenamePath(c.Path.PIECES, filename)

        service.events.send(c.EventTypes.PIECE_SAVE_PRE, piece=self)
        modox.Assembly.save(self.assemblyModoItem, filename, 'ACS Piece')
        
        if self.cacheOnSave:
            self._clearCache()
    
    @property
    def parentPiece(self):
        """ Gets parent piece of this piece - if any.
        
        Returns
        -------
        Piece, None
            None is returned if this piece has no parent piece.
        """
        parent = self.assemblyModoItem.parent
        if parent is None:
            return None
        try:
            return Piece(parent)
        except TypeError:
            pass
        return None
        
    def selfDelete(self):
        """ Piece deletes itself.
        
        Don't use its object afterwards.
        """
        modox.Assembly.delete(self._assmItem.modoItem)
        
    # -------- Private methods

    def _updateItemName(self, modoItem):
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            return
        rigItem.renderAndSetName()

    def _cache(self):
        ConnectionsCache(self.assemblyItem).cacheConnections()
        self._cacheHierarchy()
        
    def _clearCache(self):
        ConnectionsCache(self.assemblyItem).clearCache()
        self.assemblyItem.settings.deleteGroup('hrchcnnct')
        
    def _scanKeyItem(self, modoItem):
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            return
        try:
            identifier = modoItem.readTag('RSID')
        except LookupError:
            return
        self._keyItems[identifier] = rigItem
    
    def _cacheHierarchy(self):
        self._parentsCache = {}
        self.iterateOverItems(self._storeParents)
        
        self.assemblyItem.settings.setInGroup('hrchcnnct', 'parent', self._parentsCache)
        
        self._childrenCache = {}
        self.iterateOverItems(self._storeChildren)
        
        self.assemblyItem.settings.setInGroup('hrchcnnct', 'child', self._childrenCache)
        
    def _storeParents(self, modoItem):
        if not modox.Item(modoItem.internalItem).isOfXfrmCoreSuperType:
            return
        
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            return

        parentItem = modoItem.parent
        
        # We need to check if parent belongs to Piece.
        if modox.Assembly.isItemInAssemblyHierarchy(parentItem, self.assemblyModoItem):
            return
        
        # parent is outside of piece so store it.
        # It has to be a rig item though.
        try:
            parentRigItem = Item.getFromModoItem(parentItem)
        except TypeError:
            return
        
        rigItemIdent = rigItem.identifierOrNameType
        parentItemIdent = parentRigItem.identifierOrNameType
        
        if not rigItemIdent or not parentItemIdent:
            return
        
        self._parentsCache[rigItemIdent] = parentItemIdent

    def _storeChildren(self, modoItem):
        if not modox.Item(modoItem.internalItem).isOfXfrmCoreSuperType:
            return
        
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            return
        
        rigItemIdent = rigItem.identifierOrNameType
        if not rigItemIdent:
            return
        
        childIdents = []
        
        children = modoItem.children(recursive=False)
        for childModoItem in children:
            if modox.Assembly.isItemInAssemblyHierarchy(childModoItem, self.assemblyModoItem):
                continue
            try:
                childRigItem = Item.getFromModoItem(childModoItem)
            except TypeError:
                continue
            
            childIdent = childRigItem.identifierOrNameType
            if not childIdent:
                continue
            
            childIdents.append(childIdent)
        
        if childIdents:
            self._childrenCache[rigItemIdent] = childIdents
    
    def _restoreHierarchyFromCache(self, componentSetup):
        """ Restores hierarchy based on existing cache and component setup the piece is in.
        """
        # Check if cache is here first.
        parentsCache = self.assemblyItem.settings.getFromGroup('hrchcnnct', 'parent', None)
        if parentsCache is not None:
            self._restoreParents(parentsCache, componentSetup)
    
        childrenCache = self.assemblyItem.settings.getFromGroup('hrchcnnct', 'child', None)
        if childrenCache is not None:
            self._restoreChildren(childrenCache, componentSetup)

    def _restoreParents(self, parentsCache, componentSetup):
        emptyParentsDict = self._initParentIdentsDictFromCache(parentsCache)
        parentsDict = self._findParentsStoredInCache(emptyParentsDict, componentSetup)
        
        emptyItemsDict = self._initItemIdentsDictFromCache(parentsCache)
        itemsDict = self._findItemsStoredInCache(emptyItemsDict)
        
        # Go through the cache and restored parenting for all items that
        # were matched in the scene.
        for pieceItemIdent in list(parentsCache.keys()):
            item = itemsDict[pieceItemIdent]
            parent = parentsDict[parentsCache[pieceItemIdent]]
            if item is None or parent is None:
                continue
            item.modoItem.setParent(parent.modoItem)
            
    def _restoreChildren(self, childrenCache, componentSetup):
        emptyChildrenDict = self._initChildrenIdentsDictFromCache(childrenCache)
        childrenDict = self._findParentsStoredInCache(emptyChildrenDict, componentSetup)
        
        emptyItemsDict = self._initItemIdentsDictFromCache(childrenCache)
        itemsDict = self._findItemsStoredInCache(emptyItemsDict)
        
        # Go through the cache and restored parenting for all items that
        # were matched in the scene.
        for pieceItemIdent in list(childrenCache.keys()):
            item = itemsDict[pieceItemIdent]
            if item is None:
                continue
            
            childIdents = childrenCache[pieceItemIdent]

            for childIdent in childIdents:
                childItem = childrenDict[childIdent]
                if childItem is None:
                    continue
                
                childItem.modoItem.setParent(item.modoItem)
    
    def _initParentIdentsDictFromCache(self, parentsCache):
        parentIdents = {}
        for pieceItemIdent in list(parentsCache.keys()):
            if parentsCache[pieceItemIdent] in parentIdents:
                continue
            parentIdents[parentsCache[pieceItemIdent]] = None
        return parentIdents

    def _initChildrenIdentsDictFromCache(self, childrenCache):
        childIdents = {}
        for pieceItemIdent in list(childrenCache.keys()):
            for childIdent in childrenCache[pieceItemIdent]:
                if childIdent in childIdents:
                    continue
                childIdents[childIdent] = None
        return childIdents

    def _initItemIdentsDictFromCache(self, parentsCache):
        itemIdents = {}
        for pieceItemIdent in list(parentsCache.keys()):
            if pieceItemIdent in itemIdents:
                continue
            itemIdents[pieceItemIdent] = None
        return itemIdents
    
    def _findParentsStoredInCache(self, emptyParentsDict, componentSetup):
        self._cacheParentsDict = emptyParentsDict
        componentSetup.iterateOverHierarchy(self._matchComponentItemToIdent)
        return self._cacheParentsDict

    def _findItemsStoredInCache(self, emptyItemsDict):
        self._cacheItemsDict = emptyItemsDict
        self.iterateOverItems(self._matchPieceItemToIdent)
        return self._cacheItemsDict
    
    def _matchComponentItemToIdent(self, modoItem):
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            return
        
        ident = rigItem.identifierOrNameType
        if not ident:
            return
        
        if ident in self._cacheParentsDict:
            self._cacheParentsDict[ident] = rigItem

    def _matchPieceItemToIdent(self, modoItem):
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            return
        
        ident = rigItem.identifierOrNameType
        if not ident:
            return
        
        if ident in self._cacheItemsDict:
            self._cacheItemsDict[ident] = rigItem
            
    def __init__(self, initialiser):
        try:
            assm = Item.getFromOther(initialiser)
        except TypeError:
            raise TypeError
        if not isinstance(assm, PieceAssembly):
            raise TypeError
        
        self._assmItem = assm
        self._keyItems = None

    def __getitem__(self, identifier):
        """ [] operator gets key item.
        
        Raises
        ------
        LookupError
        """
        return self.getKeyItem(identifier)

