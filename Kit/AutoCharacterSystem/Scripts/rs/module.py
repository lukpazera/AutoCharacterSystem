
""" Module object.
"""


import os.path

import lx
import modo
import modox

from . import const as c
from . import item
from .log import log as log
from .component import Component
from .items.module_root import ModuleRoot
from .items.module_assm import ModuleAssembly
from .items.module_sub import *
from .items.plug import PlugItem
from .items.socket import SocketItem
from .items.generic import GenericGroupLocator
from .item import Item
from .piece import Piece
from .component_setups.module import ModuleComponentSetup
from .preset_thumbs.module import ModulePresetThumbnail
from .item_features.identifier import IdentifierFeature
from .item_feature_op import ItemFeatureOperator
from .core import service
from .util import run


class Module(Component):
    """ Module is a self contained part of the rig.

    Module presents rig component interface which means that it's
    part of the rig setup and has physical presence in the rig.

    Parameters
    ----------
    rootModoItem : modo.Item or ModuleRoot
        Either module root item or root modo item.
    """
    
    GRAPH_SYMMETRY = 'rs.symmetricModule'
    GRAPH_IDENTIFIER = 'rs.identifier'
    GRAPH_SUBMODULES = 'rs.submodules'

    _SETTING_SUBMODULE_ID = 'submid'

    # -------- Rig Component Interface
    
    descIdentifier = c.ComponentType.MODULE
    descUsername = 'Module'
    descRootItemClass = ModuleRoot
    descAssemblyItemClass = ModuleAssembly
    descComponentSetupClass = ModuleComponentSetup
    descLookupGraph = 'rs.modules'

    # -------- Public interface

    def onNew(self):
        """ Extra work that needs to be done when new module is created.
        
        We add main guide assembly.
        
        We add most basic folders template:
        - group locator for guide folder.
        - group locator for edit guide folder that is child of the guide folder.
        - group locator for rig setup.
        - group locator for bind skeleton.
        """
        # Rig assembly
        rigAssm = ModuleRigAssembly.new("Rig", componentSetup=self.setup)
        guideAssm = GuideAssembly.new("Guide", componentSetup=self.setup)

        guideFolder = GenericGroupLocator.new("Guide", componentSetup=guideAssm.modoItem)
        editGuideFolder = GenericGroupLocator.new("EditGuide", componentSetup=guideAssm.modoItem)
        rigFolder = GenericGroupLocator.new("Rig", componentSetup=rigAssm.modoItem)
        bskelFolder = GenericGroupLocator.new("BindSkeleton", componentSetup=rigAssm.modoItem)
        
        guideFolderId = ItemFeatureOperator(guideFolder).addFeature(c.ItemFeatureType.IDENTIFIER)
        guideFolderId.identifier = c.KeyItem.GUIDE_FOLDER
        
        editGuideFolderId = ItemFeatureOperator(editGuideFolder).addFeature(c.ItemFeatureType.IDENTIFIER)
        editGuideFolderId.identifier = c.KeyItem.EDIT_GUIDE_FOLDER
        
        rigFolderId = ItemFeatureOperator(rigFolder).addFeature(c.ItemFeatureType.IDENTIFIER)
        rigFolderId.identifier = c.KeyItem.RIG_FOLDER
        
        bskelFolderId = ItemFeatureOperator(bskelFolder).addFeature(c.ItemFeatureType.IDENTIFIER)
        bskelFolderId.identifier = c.KeyItem.BIND_SKELETON_FOLDER
        
        editGuideFolder.modoItem.setParent(guideFolder.modoItem)
        
        modo.Scene().select([guideFolder.modoItem, editGuideFolder.modoItem, rigFolder.modoItem, bskelFolder.modoItem], add=False)
        run('item.editorColor grey')

    @property
    def identifier(self):
        """ Gets module identifier.
        
        Returns
        -------
        str
        """
        return self.rootItem.identifier
    
    @identifier.setter
    def identifier(self, newIdent):
        """ Sets module identifier.
        
        newIdent : str
        """
        self.rootItem.identifier = newIdent

    @property
    def side(self):
        """ Gets module's side.
        
        Returns
        -------
        str
            One of side constants rs.c.Side.XXX.
        """
        return self._root.side

    @side.setter
    def side(self, side):
        oldSide = self._root.side
        if side == oldSide:
            return
        self._root.side = side
        self.updateItemNames()
        service.events.send(c.EventTypes.MODULE_SIDE_CHANGED, module=self, oldSide=oldSide, newSide=side)

    @property
    def firstSide(self):
        """
        Get module's first side - a side it was built on.

        Knowing first side is crucial to see if module should be mirrored.

        Returns
        -------
        str
            rs.c.Side.XXX.
        """
        return self._root.firstSide

    @property
    def name(self):
        """ Gets module name.
        """
        return self._root.name

    @name.setter
    def name(self, newName):
        """ Sets new module name.
        """
        oldName = self._root.name
        self._root.name = newName
        self.updateItemNames()
        service.events.send(c.EventTypes.MODULE_NAME_CHANGED, module=self, oldName=oldName, newName=newName)

    @property
    def nameAndSide(self):
        """ Returns name with side added formatted according to rig's naming scheme.
        
        Returns
        -------
        str
            Rendered side+name string.
        """
        return self._root.nameAndSide

    @property
    def referenceName(self):
        """
        Gets reference name for module.

        This name include's module side and its name.
        It's NOT dependend on the naming scheme.
        The format is simply side concatenated with name:
        RightLeg

        Returns
        -------
        str
        """
        # refName = ''
        # sideString = {c.Side.CENTER: '', c.Side.LEFT: 'Left ', c.Side.RIGHT: 'Right '}
        # refName += sideString[self.side]
        # refName += self.name
        return self.renderReferenceNameFromTokens(self.side, self.name)

    @classmethod
    def renderReferenceNameFromTokens(cls, side, name):
        """
        Renders module reference name from given tokens.

        This allows for searching modules by their reference names.

        Parameters
        ----------
        side : str
            c.Side.XXX constant.

        name : str
        """
        refName = ''
        sideString = {c.Side.CENTER: '', c.Side.LEFT: 'Left ', c.Side.RIGHT: 'Right '}
        refName += sideString[side]
        refName += name
        return refName

    @property
    def filename(self):
        """ Gets filename for module preset.

        If filename developer property is not an empty string it will be returned.
        Module name will be returned otherwise.

        Returns
        -------
        str
        """
        fname = self._root.filename
        if fname:
            return fname
        return self.name

    @filename.setter
    def filename(self, filename):
        """
        Sets new module filename.

        When module is saved it'll be under this name.

        Parameters
        ----------
        filename : str
        """
        self._root.filename = filename

    @property
    def defaultThumbnailName(self):
        """ Gets default thumbnail name for module preset.

        Returns
        -------
        str
        """
        return self._root.defaultThumbnailName

    @defaultThumbnailName.setter
    def defaultThumbnailName(self, name):
        """
        Sets new default thumbnail name.

        Parameters
        ----------
        name : str
        """
        self._root.defaultThumbnailName = name

    @property
    def dropAction(self):
        """ Gets module's drop action setting.
        
        Returns
        -------
        str
            Drop action is returned as rs.c.ModuleDropAction string constant.
        """
        return self._root.dropAction
        
    @property
    def settings(self):
        """ Gets access to item settings on the module root item.
        
        Returns
        -------
        ItemSettings
        """
        return self._root.settings

    @property
    def symmetricModule(self):
        """ Gets module that is symmetry reference for this module.
        
        Returns
        -------
        Module, None
        """
        graph = self.rootModoItem.itemGraph(self.GRAPH_SYMMETRY)
        try:
            return Module(graph.forward(0))
        except LookupError:
            pass
        return None
    
    @symmetricModule.setter
    def symmetricModule(self, symmetryModule):
        """ Sets symmetry source module for a given module.

        Set this on a module that should be symmetric to some other module.
    
        Parameters
        ----------
        symmetryModule : Module, modo.Item, None
            Module to set as symmetry reference. Pass None to clear
            current symmetry link.
        """
        if symmetryModule is None:
            modox.ItemUtils.clearForwardGraphConnections(self.rootModoItem, self.GRAPH_SYMMETRY)
            return
        
        # Test symmetric module identifier here.
        # It has to be the same as this module.

        # Only sided module can have symmetric module set.
        if self.side not in (c.Side.LEFT, c.Side.RIGHT):
            return False
        
        # Only left module can be set for right one and vice versa.
        pairs = {c.Side.LEFT: c.Side.RIGHT,
                 c.Side.RIGHT: c.Side.LEFT}
        if pairs[self.side] != symmetryModule.side:
            return False
        
        modox.ItemUtils.clearForwardGraphConnections(self.rootModoItem, self.GRAPH_SYMMETRY)

        guideGraph = self.rootModoItem.itemGraph(self.GRAPH_SYMMETRY)
        driverGraph = symmetryModule.rootModoItem.itemGraph(self.GRAPH_SYMMETRY)
        guideGraph >> driverGraph

    @property
    def symmetryLinkedModules(self):
        """ Gets all modules that have symmetry link with this one.

        This concerns links in both directions. Use this to get symmetrical modules
        from both symmetry source module and from symmetrized ones.

        Returns
        -------
        [Module]
        """
        return self.getSymmetryLinkedModules(True, True)

    def getSymmetryLinkedModules(self, reference=True, driven=True):
        """ Gets modules that have symmetry link with this one.

        Parameters
        ----------
        reference : bool
            Check symmetry reference modules for this module.
            Equivalent of a module that is set in symmetry property for this module.

        driven : bool
            Check if this module serves as symmetry reference for any other module and if it does
            all these driven modules will be returned.

        Returns
        -------
        [Module]
        """
        symModoItems = []

        if driven:
            symModoItems.extend(modox.ItemUtils.getReverseGraphConnections(self.rootModoItem, self.GRAPH_SYMMETRY))
        if reference:
            symModoItems.extend(modox.ItemUtils.getForwardGraphConnections(self.rootModoItem, self.GRAPH_SYMMETRY))

        modules = []
        for modoItem in symModoItems:
            try:
                modules.append(Module(modoItem))
            except TypeError:
                pass
        return modules

    @property
    def plugs(self):
        """ Returns a list of plugs.
        
        Returns
        -------
        list of PlugItem
        """
        plugModoItems = self.getElementsFromSet(c.ElementSetType.PLUGS)
        plugs = [PlugItem(modoItem) for modoItem in plugModoItems]
        return plugs

    @property
    def plugsByNames(self):
        """
        Gets a list of plugs arranged in dictionary by their names.

        Returns
        -------
        {str : PlugItem}
        """
        plugModoItems = self.getElementsFromSet(c.ElementSetType.PLUGS)
        plugs = {}
        for modoItem in plugModoItems:
            plug = PlugItem(modoItem)
            plugs[plug.name] = plug
        return plugs

    @property
    def sockets(self):
        """ Returns a list of sockets.
        """
        socketModoItems = self.getElementsFromSet(c.ElementSetType.SOCKETS)
        sockets = [SocketItem(modoItem) for modoItem in socketModoItems]
        return sockets

    @property
    def socketsByNames(self):
        """ Gets a list of sockets arranged in dictionary by their names.

        Returns
        -------
        {str : SocketItem}
        """
        socketModoItems = self.getElementsFromSet(c.ElementSetType.SOCKETS)
        sockets = {}
        for modoItem in socketModoItems:
            socket = SocketItem(modoItem)
            sockets[socket.name] = socket
        return sockets

    @property
    def socketsByReferenceNames(self):
        """ Gets a list of sockets arranged in dictionary by their reference names.

        Reference name consists of a side letter (R, L, C) and item name.
        Reference names are useful for getting items that have the same name but different side within a module.
        
        Returns
        -------
        {str : SocketItem}
        """
        socketModoItems = self.getElementsFromSet(c.ElementSetType.SOCKETS)
        sockets = {}
        for modoItem in socketModoItems:
            socket = SocketItem(modoItem)
            sockets[socket.getReferenceName(side=True, moduleName=False, basename=True)] = socket
        return sockets

    def getSubassembliesOfItemType(self, identifier):
        """ Gets subassemblies that are of given rig item type.

        Subassemblies are direct children of main module assembly.
        The search is NOT recursive.

        Parameters
        ----------
        identifier : str
        
        Returns
        -------
        list
            List of subassemblies that are of a given rig item type.
            The list will be empty if no items of given type were found.
        """
        if self._assmsByItemType is None:
            self._scanKeySubassms()
        try:
            return self._assmsByItemType[identifier]
        except KeyError:
            pass
        return []

    def getFirstSubassemblyOfItemType(self, identifier):
        """ Gets first subassembly that is of given rig item type.

        Parameters
        ----------
        identifier : str

        Returns
        -------
        Item

        Raises
        ------
        LookupError
            When subassembly cannot be found.
        """
        try:
            return self.getSubassembliesOfItemType(identifier)[0]
        except IndexError:
            pass
        raise LookupError

    @property
    def rigSubassembly(self):
        """
        Gets the assembly item for the module rig.

        Returns
        -------
        ModuleRigAssembly, None
        """
        try:
            return self.getFirstSubassemblyOfItemType(c.RigItemType.MODULE_RIG_ASSM)
        except LookupError:
            return None

    @property
    def keySubassemblies(self):
        """ Gets a dictionary of key subassemblies.
        
        Key subassemblies are subassemblies that have identifier set and are direct children
        of the main module assembly. The search is NOT recursive.
        
        Returns
        -------
        dict of modo.Item
        """
        if self._keyAssms is None:
            self._scanKeySubassms()
        return self._keyAssms
    
    def mirrorKeyChannels(self):
        """ Mirrors values on all channels that are in the mirror subassembly.
        """
        mirrorAssms = self.getSubassembliesOfItemType(c.RigItemType.MIRROR_CHAN_GROUP)
        
        for mirrorAssm in mirrorAssms:
            for chan in mirrorAssm.modoItem.groupChannels:
                v = chan.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_SETUP)
                if modox.ChannelUtils.isBooleanChannel(chan):
                    v = 1 - v
                else:
                    v *= -1.0
                chan.set(v, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

    def disconnectFromModule(self, module=None):
        """ Disconnects this module from another module.
        
        Parameters
        ----------
        module : Module, None
            Module to disconnect from. Pass None to disconnect this module completely
            from any other module it's connected to.
            #TODO: Passing Module is not implemented yet, only None works!
        """
        plugModoItems = self.getElementsFromSet(c.ElementSetType.PLUGS)
        for plugModoItem in plugModoItems:
            try:
                plug = PlugItem(plugModoItem)
            except TypeError:
                continue
            plug.disconnectFromSocket()

    def cleanUpPlugConnections(self):
        """
        Cleans up plug connections. Orphaned connections will be removed, good ones will not be changed.
        """
        plugModoItems = self.getElementsFromSet(c.ElementSetType.PLUGS)
        for plugModoItem in plugModoItems:
            try:
                plug = PlugItem(plugModoItem)
            except TypeError:
                continue
            plug.cleanUpConnection()

    def updateItemNames(self):
        self.iterateOverItems(self._renameItem)

    def newItem(self, rigItemType, subtype=None, name=None):
        """ Adds new item to module.
        """
        try:
            itemClass = service.systemComponent.get(c.SystemComponentType.ITEM, rigItemType)
        except LookupError:
            raise TypeError

        newRigItem = itemClass.new(name, subtype)
        self.addItem(newRigItem)
        return newRigItem

    def addItem(self, itemToAdd):
        """ Adds existing item to module.
        """
        if issubclass(itemToAdd.__class__, item.Item):
            self._setup.addItem(itemToAdd.modoItem)
            itemToAdd.renderAndSetName()
        elif isinstance(itemToAdd, modo.Item):
            self._setup.addItem(itemToAdd)
        else:
            raise TypeError

    def getLocatorKeyItem(self, itemIdentifierOrName):
        """ Gets key item by its identifier or name.
        
        Returns
        -------
        Item
            Rig item or None if requested item was not found.
        
        Raises
        ------
        LookupError
            When item cannot be found.
        """
        self._keyItem = None
        self._key = itemIdentifierOrName
        self.iterateOverHierarchy(self._isKeyItemWithIdent)
        
        if self._keyItem is None:
            raise LookupError

        return self._keyItem

    def getRigItemsOfType(self, rigItemType):
        """
        Gets a list of rig items of a given type.

        Returns
        -------
        [Item]
        """
        self._tmpItems = []
        self._tmpType = rigItemType
        self.iterateOverItems(self._storeRigItemOfType)
        return self._tmpItems

    def getModoItemsOfType(self, modoItemType):
        """ Gets a list of modo items with a given type in a module.
        """
        self._tmpItems = []
        self._tmpType = modoItemType
        self.iterateOverItems(self._storeModoItemOfType)
        return self._tmpItems

    def getItemFeaturesByIdentifier(self, identifier):
        """
        Gets a list of item features with given identifier that are in the module.

        Returns
        -------
        [ItemFeature]
        """
        try:
            featureClass = service.systemComponent.get(c.SystemComponentType.ITEM_FEATURE, identifier)
        except LookupError:
            return []

        self._tmpFeatures = []
        self._tmpClass = featureClass

        self.iterateOverItems(self._storeItemFeaturesOfType)
        return self._tmpFeatures

    @property
    def keyItems(self):
        """ Gets module key items.
        
        Does not return key items belonging to module pieces.
        
        Returns
        -------
        dict {str ident : Item}
        """
        return self.getKeyItems()

    @property
    def keyItemsIncludingPieces(self):
        """ Gets module key items. Pieces are scanned too.

        Returns
        -------
        dict {str ident : Item}
        """
        return self.getKeyItems(includePieces=True)

    def getKeyItems(self, identifier=None, includePieces=False):
        """ Gets module key item by its identifier.
        
        Key item is an item that has identifier set via the identifier feature.
        
        Returns
        -------
        dict {str ident : Item}
        """
        if self._keyItems is None:
            assmCallback = None
            if not includePieces:
                assmCallback = self._testNotPiece
            
            self._keyItems = {}
            self._setup.iterateOverItems(self._isKeyItem, includeSubassemblies=True, assmTestCallback=assmCallback)
        return self._keyItems

    def getKeyItem(self, identifier, includePieces=False):
        """ Gets particular key item.

        Parameters
        ----------
        identifier : str

        Raises
        ------
        LookupError
        """
        if includePieces:
            try:
                return self.keyItemsIncludingPieces[identifier]
            except KeyError:
                raise LookupError
        else:
            try:
                return self.keyItems[identifier]
            except KeyError:
                raise LookupError
        raise LookupError

    def addSubmodule(self, module, identifier=None):
        """
        Adds another module as a submodule to this module.
        """
        modox.ItemUtils.addForwardGraphConnections(module.rootModoItem, self.rootModoItem, self.GRAPH_SUBMODULES)
        if identifier is not None:
            module.settings.set(self._SETTING_SUBMODULE_ID, identifier)

    def disconnectSubmodule(self, module):
        """
        Disconnect given submodule.
        """
        modox.ItemUtils.clearForwardGraphConnections(module.rootModoItem, self.GRAPH_SUBMODULES, [self.rootModoItem])
        module.settings.delete(self._SETTING_SUBMODULE_ID)

    @property
    def submodules(self):
        """
        Gets a list of all submodules.

        Returns
        -------
        [Module]
        """
        connected = modox.ItemUtils.getReverseGraphConnections(self.rootModoItem, self.GRAPH_SUBMODULES)
        return [Module(modoItem) for modoItem in connected]

    @property
    def submodulesByIdentifiers(self):
        """
        Gets all submodules as dictionary with keys being module identifiers.

        Returns
        -------
        {str : [Module]}
        """
        submods = self.submodules
        subById = {}
        for module in submods:
            ident = module.settings.get(self._SETTING_SUBMODULE_ID, None)
            if ident in subById:
                subById[ident].append(module)
            else:
                subById[ident] = [module]
        return subById

    def getSubmodulesWithIdentifier(self, identifier=None):
        """
        Gets list of modules that have given identifier.

        Returns
        -------
        [Module]
        """
        submods = self.submodules
        filtered = []
        for module in submods:
            ident = module.settings.get(self._SETTING_SUBMODULE_ID, None)
            if ident == identifier:
                filtered.append(module)
        return filtered

    @property
    def isSubmodule(self):
        """
        Tests whether this module is a submodule of another module.

        Returns
        -------
        bool
        """
        return modox.ItemUtils.getFirstForwardGraphConnection(self.rootModoItem, self.GRAPH_SUBMODULES) is not None

    @property
    def parentModule(self):
        """
        If this module is a submodule this gets the parent module this module is submodule of.
        """
        return modox.ItemUtils.getFirstForwardGraphConnection(self.rootModoItem, self.GRAPH_SUBMODULES)

    def addPiece(self, identifier, updateItemNames=False):
        """ Adds new piece from preset file to the module.
        
        The piece will be indexed.
        
        Parameters
        ----------
        identifier : str
            Identifier of the piece. It is piece filename at the same time.

        updateItemNames : bool
            Piece names will be updated when it's dropped into the scene.
            Typically, you want this, although for some reason default values is set to False.

        Returns
        -------
        pieceClass object
            Returned object will be of pieceClass (or generic Piece if custom class
            cannot be matched to identifier).
        """
        
        # need to set up index.
        piecesByIndex = self.getPiecesByIdentifier(identifier)
        newPieceIndex = len(piecesByIndex) + 1 # indexing pieces from 1
        
        # Load and index the piece
        piece = Piece.load(identifier, self.identifier, self.setup, updateItemNames)
        piece.index = newPieceIndex

        return piece

    def removePiece(self, identifier, index=1):
        """ Removes piece from module.
        
        Parameters
        ----------
        identifier : str
            Identifier of the piece to remove.
        
        index : int, optional
            Index of piece to remove. This only really matters with serial pieces.
            For singleton ones the index is set to 1 by default so you can skip
            that argument.
        
        Raises
        ------
        LookupError
        """
        try:
            p = self.getPiecesByIdentifier(identifier)[index]
        except (KeyError, IndexError):
            raise LookupError
        p.selfDelete()
        
    @property
    def pieces(self):
        """ Gets a list of module pieces - subassemblies easily accessible via code.
        
        The list is in random order and contains all the pieces.
        
        Returns
        -------
        list of Piece
        """
        self._pieces = []
        self._setup.iterateOverSubassemblies(self._testPieceSubassembly)
        return self._pieces

    def getPiecesByIdentifier(self, pieceIdent):
        """ Gets a dictionary of module pieces with specific identifier.
        
        Pieces will be returned as a dictionary where keys are index numbers of pieces.

        Parameters
        ----------
        pieceIdent : str
        
        Returns
        -------
        dict{int : PieceAssembly}
        """
        pieces = self.pieces
        idpieces = {}
        for piece in pieces:
            if piece.identifier == pieceIdent:
                index = piece.index
                idpieces[index] = piece
        return idpieces

    def getPiecesByIdentifierOrdered(self, pieceIdent):
        """
        Gets a list of module pieces ordered according to their index.

        Returns
        -------
        [Piece]
        """
        idpieces = self.getPiecesByIdentifier(pieceIdent)
        piecelist = []
        for x in range(len(idpieces)):
            piecelist.append(idpieces[x + 1]) # Remember, pieces are indexed from 1
        return piecelist

    def getFirstPieceByIdentifier(self, pieceIdent):
        """
        Gets first piece by its identifier.

        Use this for singleton pieces only!!! You will get random result otherwise.

        Parameters
        ----------
        pieceIdent : str

        Returns
        -------
        Piece

        Raises
        ------
        LookupError
            When piece could not be found.
        """
        pieces = self.pieces
        for piece in pieces:
            if piece.identifier == pieceIdent:
                return piece
        raise LookupError

    @property
    def guideAssembly(self):
        """
        Gets guide assembly for the module, it is assumed that there is only one.

        Returns
        -------
        GuideAssembly, None
        """
        guideAssms = self.getSubassembliesOfItemType(c.RigItemType.GUIDE_ASSM)
        for guideAssm in guideAssms:
            if guideAssm.modoItem.parent == self.assemblyModoItem:
                return guideAssm
        return None

    def iterateOverItems(self, callback):
        self._setup.iterateOverItems(callback)

    def iterateOverHierarchy(self, callback):
        """ Iterates through locator supertype items that form the module hierarchy.
        """
        self._setup.iterateOverHierarchy(callback)

    def getElementsFromSet(self, setIdentifier):
        """ Gets elements that belong to this module from a given set.
        
        NOTE: This only works properly for modules that are part of the rig already!
        
        Parameters
        ----------
        setIdentifier : str
            rs.c.ElementSetType constant.

        Returns
        -------
        [modo.Item]

        Raise
        -----
        LookupError
            When given element set could not be found.
        """
        try:
            elsetClass = service.systemComponent.get(c.SystemComponentType.ELEMENT_SET, setIdentifier)
        except LookupError:
            raise
        
        elset = elsetClass(self.rigRootItem)
        return elset.getElementsFilteredByModule(self)

    def setItemListOrder(self, index):
        """ Allows for positioning of the module in item list under its current parent.
        
        This is used to update modules order in item list when modules are attached to each other.
        """
        p = self.rootModoItem.parent
        self.rootModoItem.setParent(p, index)

    @property
    def autoPathAndFilename(self):
        """
        Gets full path and filename to module.

        The filename is generated automatically based on module filename property and default
        paths to modules.

        Returns
        -------
        str
        """
        name = self.filename + '.lxp'
        return os.path.join(service.path[c.Path.MODULES], name)

    def getInputChannel(self, chanName):
        """ Gets module's input channel of a given name.

        Parameters
        ----------
        chanName : str

        Returns
        -------
        modo.Channel

        Raises
        ------
        LookupError
            When channel does not exist on the module assembly or is not an input channel
        """
        chan = self.assemblyModoItem.channel(chanName)
        if chan is None:
            raise LookupError
        if modox.Assembly.isInputChannel(chan):
            return chan
        raise LookupError

    def save(self, filename=None, captureThumb=False):
        """ Saves module out as a preset.
        
        Parameters
        ----------
        filename : str, None
            String has to be full filename together with path.
            If None is used filename stored as module property will be used instead.
        
        captureThumb : bool, optional
        """
        if filename is None:
            filename = self.autoPathAndFilename

        if not filename:
            return

        if captureThumb:
            thumb = ModulePresetThumbnail()
            defaultThumbName = self.rootItem.defaultThumbnailName
            if defaultThumbName:
                thumb.setThumbnailDirectly(defaultThumbName)
        else:
            thumb = None

        service.events.send(c.EventTypes.MODULE_SAVE_PRE, module=self)
        self.rootItem.setSystemVersion()
        self._setup.save(filename, thumb)
        service.events.send(c.EventTypes.MODULE_SAVE_POST, module=self)

    def selfDelete(self):
        """ Self deletes the module.
        
        Module object should not be used afterwards.
        """
        service.events.send(c.EventTypes.MODULE_DELETE_PRE, module=self)
        self._setup.selfDelete()

    def onAddedToRig(self):
        """ Gets called when this module is added to rig.
        
        Use this to perform custom actions when module is added to the rig.
        """
        pass
        
    # -------- Private methods
    
    def _scanKeySubassms(self):
        self._keyAssms = {}
        self._assmsByItemType = {}
        self.setup.iterateOverSubassemblies(self._collectKeySubassm, recursive=False)

    def _collectKeySubassm(self, modoItem):
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            pass
        else:
            rigItemType = rigItem.type
            if rigItemType not in self._assmsByItemType:
                self._assmsByItemType[rigItemType] = []
            self._assmsByItemType[rigItemType].append(rigItem)
            
        try:
            feature = IdentifierFeature(modoItem)
        except TypeError:
            return
        ident = feature.identifier
        if not ident:
            return
        self._keyAssms[ident] = modoItem
        
    def _testPieceSubassembly(self, assmModoItem):
        try:
            piece = Piece(assmModoItem)
        except TypeError:
            return
        self._pieces.append(piece)
            
    def _testNotPiece(self, modoItem):
        try:
            piece = Piece(modoItem)
        except TypeError:
            return True
        return False
        
    def _isKeyItemWithIdent(self, modoItem):
        """ Use this to get first item with given identifier.
        """
        try:
            rigItem = item.Item.getFromModoItem(modoItem)
        except TypeError:
            return
        if rigItem.identifier == self._key:
            self._keyItem = rigItem
            return True
    
    def _isKeyItem(self, modoItem):
        """ Use this to get any key item.
        """
        try:
            rigItem = item.Item.getFromModoItem(modoItem)
        except TypeError:
            return
        identifier = rigItem.identifier
        if identifier:
            self._keyItems[identifier] = rigItem
        
    def _storeModoItemOfType(self, modoItem):
        if modoItem.type == self._tmpType:
            self._tmpItems.append(modoItem)

    def _storeRigItemOfType(self, modoItem):
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            return
        if rigItem.type == self._tmpType:
            self._tmpItems.append(rigItem)

    def _storeItemFeaturesOfType(self, modoItem):
        try:
            self._tmpFeatures.append(self._tmpClass(modoItem))
        except TypeError:
            pass

    def _renameItem(self, itemToRename):
        try:
            rigItem = item.Item.getFromModoItem(itemToRename)
        except TypeError:
            return
        rigItem.renderAndSetName()

    def __init__(self, componentRootItem):
        Component.__init__(self, componentRootItem)

        self._keyItems = None
        self._keyAssms = None
        self._assmsByItemType = None
        
    def __str__(self):
        return self.referenceName

    def __eq__(self, other):
        if isinstance(other, str):
            return self.sceneIdentifier == other
        elif isinstance(other, Module):
            return self.sceneIdentifier == other.sceneIdentifier
        elif isinstance(other, ModuleRoot):
            return self.sceneIdentifier == other.modoItem.id
        else:
            return False

    def __getitem__(self, identifier):
        """ Gets module elements from a given set.
        """
        return self.getElementsFromSet(identifier)
