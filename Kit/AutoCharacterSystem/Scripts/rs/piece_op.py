

import lx
import modo
import modox

from .item_features.item_link import ItemLinkFeature
from .item import Item
from . import const as c
from .log import log


class PieceOperator(object):
    """
    Piece operator allows for performing operations on pieces within given module.

    Parameters
    ----------
    module : Module
        Module the operator will work on.
    """

    def installSerialPieces(self, count, piecesSetupClass):
        """
        Installs given number of serial pieces inside the module.

        If count is larger then number of pieces with the same identifier new pieces will be added.
        If it's lower - extra pieces will be removed.

        IMPORTANT: Serial pieces indexing starts from 1!!!!
        """
        serialPieceIdentifier = piecesSetupClass.descSerialPieceClass.descIdentifier
        existingPiecesByIndex = self._module.getPiecesByIdentifier(serialPieceIdentifier)
        currentCount = len(existingPiecesByIndex)

        if count == currentCount:
            return False

        if count < 0:
            count = 0

        if count > currentCount:
            newPiecesCount = count - currentCount
            if newPiecesCount > 0:
                self._addPieces(newPiecesCount, piecesSetupClass, existingPiecesByIndex)
        else:
            piecesToRemoveCount = currentCount - count
            if piecesToRemoveCount > 0:
                self._removePieces(piecesToRemoveCount, piecesSetupClass, existingPiecesByIndex)

        self._storeCount(count, piecesSetupClass)
        return True

    def installIndividualPiece(self, identifier):
        """
        Installs individual piece in the module.
        """
        pass

    @property
    def module(self):
        return self._module

    # -------- Private methods

    def _addPieces(self, count, serialSetupClass, existingPiecesByIndex):
        serialSetup = serialSetupClass(self._module)
        for x in range(count):
            newPiece = self._module.addPiece(serialSetupClass.descSerialPieceClass.descIdentifier)
            newPieceIndex = newPiece.index
            newPieceKeyItems = newPiece.keyItems

            # Add this piece to the list so it's available for subsequent loop iterations.
            existingPiecesByIndex[newPieceIndex] = newPiece

            serialPieceObject = serialSetupClass.descSerialPieceClass(newPiece.assemblyItem)
            self._setupChainHierarchy(newPieceIndex, existingPiecesByIndex, serialPieceObject)
            self._integrateDeformers(newPiece, serialSetupClass.descSerialPieceClass)
            self._updatePieceNames(newPiece, serialSetupClass)
        self._clearConnections(existingPiecesByIndex)
        self._setUpConnections(existingPiecesByIndex)
        self._setupModuleHierarchy(existingPiecesByIndex, serialSetupClass)
        self._fitGuideChain(existingPiecesByIndex, serialSetupClass)
        self._setEditGuidesLinksDrawing(existingPiecesByIndex, serialSetupClass)
        self._onSerialPieceAdded(existingPiecesByIndex, serialSetup)

    def _onSerialPieceAdded(self, piecesByIndex, serialSetup):
        serialPiecesCount = len(piecesByIndex)
        for x in range(serialPiecesCount):
            index = x + 1
            prevPiece = None
            nextPiece = None
            piece = piecesByIndex[index]
            if index > 1:
                prevPiece = piecesByIndex[index - 1]
            if index < serialPiecesCount:  # Since pieces are indexed from 1, I don't have to do -1 here.
                nextPiece = piecesByIndex[index + 1]
            serialSetup.onSerialPieceAdded(piecesByIndex[index], prevPiece, nextPiece)

    def _removePieces(self, piecesToRemoveCount, serialSetupClass, piecesByIndex):
        pieceToRemoveIndex = len(piecesByIndex) # Piece indexing is from 1 so no need to substract 1 here.
        for x in range(piecesToRemoveCount):
            piecesByIndex[pieceToRemoveIndex].selfDelete()
            del piecesByIndex[pieceToRemoveIndex]
            pieceToRemoveIndex -= 1
        self._clearConnections(piecesByIndex)
        self._setUpConnections(piecesByIndex)
        self._setupModuleHierarchy(piecesByIndex, serialSetupClass)
        self._fitGuideChain(piecesByIndex, serialSetupClass)
        self._setEditGuidesLinksDrawing(piecesByIndex, serialSetupClass)

    def _setupChainHierarchy(self, pieceIndex, piecesByIndex, serialPieceObject):
        """
        Sets up piece within rig hierarchy.

        Parameters
        ----------
        serialPieceObject : SerialPiece
            This is the actual piece object but not generic SerialPiece but the actual
            class that implements particular serial piece.
            # TODO: This is really crap, I should just have pieceByIndex have
            proper class rather then just generic SerialPiece.
        """
        parentedItemIds = []
        pieceKeyItems = piecesByIndex[pieceIndex].keyItems

        # Set up parenting between this and previous pieces in the chain.
        # If this is first piece, try to parent using the same keys to module instead.
        if pieceIndex > 1:
            prevKeyItems = piecesByIndex[pieceIndex - 1].keyItems
        else:
            prevKeyItems = self._module.keyItems

        for parentKey in serialPieceObject.descPieceHierarchy:
            try:
                parentRigItem = prevKeyItems[parentKey]
            except KeyError:
                continue
            parent = parentRigItem.modoItem

            itemKeys = serialPieceObject.descPieceHierarchy[parentKey]
            if type(itemKeys) not in (tuple, list):
                itemKeys = [itemKeys]

            for key in itemKeys:
                try:
                    mitem = pieceKeyItems[key].modoItem
                    mitem.setParent(parent)
                    parentedItemIds.append(mitem.id)
                except KeyError:
                    continue

        # TODO: Parent piece key items to module items.
        # Note that this is done ONLY if piece item was not parented to previous piece already.
        parentItems = self._module.keyItems
        for parentKey in serialPieceObject.descModuleHierarchy:
            try:
                parentRigItem = parentItems[parentKey]
            except KeyError:
                continue
            parent = parentRigItem.modoItem

            itemKeys = serialPieceObject.descModuleHierarchy[parentKey]
            if type(itemKeys) not in (tuple, list):
                itemKeys = [itemKeys]

            for key in itemKeys:
                try:
                    mitem = pieceKeyItems[key].modoItem
                except KeyError:
                    continue

                # Skip items that were already parented to a piece.
                if mitem.id in parentedItemIds:
                    continue
                mitem.setParent(parent)

    def _setupModuleHierarchy(self, piecesByIndex, serialSetupClass):
        """
        Sets up module hierarchy to added serial pieces.

        This is really used to parent module items to last piece
        or if there are no pieces - to equivalent items from module itself.
        """
        if len(piecesByIndex) > 0:
            parentKeyItems = piecesByIndex[len(piecesByIndex)].keyItems
        else:
            parentKeyItems = self._module.keyItems

        childKeyItems = self._module.keyItems

        serialSetup = serialSetupClass(self._module)
        for parentKey in serialSetup.descModuleHierarchy:
            try:
                parentRigItem = parentKeyItems[parentKey]
            except KeyError:
                continue
            parent = parentRigItem.modoItem

            itemKeys = serialSetup.descModuleHierarchy[parentKey]
            if type(itemKeys) not in (tuple, list):
                itemKeys = [itemKeys]

            for key in itemKeys:
                try:
                    mitem = childKeyItems[key].modoItem
                    mitem.setParent(parent)
                except KeyError:
                    continue

    def _integrateDeformers(self, piece, serialPieceClass):
        pieceKeyItems = piece.keyItems
        for moduleDeformerKey in serialPieceClass.descDeformersHierarchy:
            try:
                dfrm = modox.DeformFolder(self._module.getKeyItem(moduleDeformerKey).modoItem)
            except LookupError:
                log.out("Bad module deformer item key!", log.MSG_ERROR)
                continue

            itemKeys = serialPieceClass.descDeformersHierarchy[moduleDeformerKey]
            if type(itemKeys) not in (tuple, list):
                itemKeys = [itemKeys]
            for key in itemKeys:
                try:
                    dfrm.addDeformer(pieceKeyItems[key].modoItem)
                except KeyError:
                    pass

    def _clearConnections(self, piecesByIndex):
        """
        Clears all the connections between pieces and module.
        """
        for index in piecesByIndex:
            modoItem = piecesByIndex[index].assemblyModoItem
            inputs, outputs = modox.Assembly.getInputOutputChannels(modoItem)
            modox.ChannelUtils.removeAllReverseConnections(inputs)
            modox.ChannelUtils.removeAllForwardConnections(outputs)

    def _setUpConnections(self, piecesByIndex):
        """
        Sets up connections between serial pieces themselves or between pieces and module.

        The rule here is that we only plug inputs so we scan inputs and find their connections.
        Inputs are on pieces but also on rig and module assemblies so we have to process all of these.

        Naming of inputs is crucial:
        - for module output channels that will feed into pieces they can't have underscores in
        channel names. Everything before first underscore is considered prefix and is cut off when
        matching channels.
        - You need to add proper prefix for piece input channels:
        gd_ - channel is linked to guide subassembly
        rig_ - channel is linked to rig subassembly
        next_ - channel is linked to next piece
        - You need ot add proper prefix for rig and guide subassemblies inputs if you want
        to connect them to pieces
        first_ - input connects to first piece
        last_ - input connects to last piece
        """
        modGuide = self.module.getFirstSubassemblyOfItemType(c.RigItemType.GUIDE_ASSM).modoItem
        modRig = self.module.getFirstSubassemblyOfItemType(c.RigItemType.MODULE_RIG_ASSM).modoItem
        modRoot = self.module.rootModoItem

        guideInputs, guideOutputs = modox.Assembly.getInputOutputChannels(modGuide)
        rigInputs, rigOutputs = modox.Assembly.getInputOutputChannels(modRig)

        # For guide and rig outputs we cut off any prefix
        # User can use prefix to label channel better but name matching will not
        # take first '_' prefix into consideration.
        guideOutputsByUsername = {}
        for channel in guideOutputs:
            chanUsername = modox.ChannelUtils.getChannelUsername(channel)
            guideOutputsByUsername[chanUsername.rpartition('__')[2]] = channel

        rigOutputsByUsername = {}
        for channel in rigOutputs:
            chanUsername = modox.ChannelUtils.getChannelUsername(channel)
            rigOutputsByUsername[chanUsername.rpartition('__')[2]] = channel

        moduleOutputsByUsername = {}
        for channel in modRoot.channels():
            chanUsername = modox.ChannelUtils.getChannelUsername(channel)
            moduleOutputsByUsername[chanUsername] = channel

        sequenceLength = len(piecesByIndex)

        # Cache all piece inputs for easy access
        pieceInputsByIndexAndUsername = {}
        for index in piecesByIndex:
            pieceInputs = modox.Assembly.getInputChanels(piecesByIndex[index].assemblyModoItem)
            inputsByUsername = {}
            for channel in pieceInputs:
                chanUsername = modox.ChannelUtils.getChannelUsername(channel)
                inputsByUsername[chanUsername] = channel
            pieceInputsByIndexAndUsername[index] = inputsByUsername

        # Cache all piece outputs for easy access
        pieceOutputsByIndexAndUsername = {}
        for index in piecesByIndex:
            pieceOutputs = modox.Assembly.getOutputChannels(piecesByIndex[index].assemblyModoItem)
            outputsByUsername = {}
            for channel in pieceOutputs:
                chanUsername = modox.ChannelUtils.getChannelUsername(channel)
                outputsByUsername[chanUsername] = channel
            pieceOutputsByIndexAndUsername[index] = outputsByUsername

        # Process inputs for pieces
        for index in piecesByIndex:

            # process inputs
            for channel in list(pieceInputsByIndexAndUsername[index].values()):
                chanUsername = modox.ChannelUtils.getChannelUsername(channel)

                # Input from guide
                if chanUsername.startswith('gd__'):
                    try:
                        outChannel = guideOutputsByUsername[chanUsername[4:]]
                    except KeyError:
                        continue
                    outChannel >> channel

                # Input from module
                elif chanUsername.startswith('mod__'):
                    try:
                        outChannel = moduleOutputsByUsername[chanUsername[5:]]
                    except KeyError:
                        continue
                    outChannel >> channel

                # Input from rig
                elif chanUsername.startswith('rig__'):
                    try:
                        outChannel = rigOutputsByUsername[chanUsername[5:]]
                    except KeyError:
                        continue
                    outChannel >> channel

                # Input from next piece
                elif chanUsername.startswith('next__'):
                    if index < sequenceLength:
                        try:
                            outChannel = pieceOutputsByIndexAndUsername[index + 1][chanUsername[6:]]
                        except KeyError:
                            continue
                        outChannel >> channel
                    else:
                        outChannel = None
                        # If this is last piece there may be relevant connection on rig
                        # or guide assembly item.
                        # Look for matching channel in guide or rig assembly outputs.
                        try:
                            outChannel = rigOutputsByUsername[chanUsername[6:]]
                        except KeyError:
                            pass

                        if outChannel is None:
                            try:
                                outChannel = guideOutputsByUsername[chanUsername[6:]]
                            except KeyError:
                                pass

                        if outChannel is not None:
                            outChannel >> channel

                # Input from previous piece
                elif chanUsername.startswith('prev__'):
                    if index > 1:  # Remember that serial piece indexing starts from 1
                        try:
                            outChannel = pieceOutputsByIndexAndUsername[index - 1][chanUsername[6:]]
                        except KeyError:
                            continue
                        outChannel >> channel
                    else:
                        outChannel = None
                        # This is first piece there may be relevant connection on rig
                        # or guide assembly item.
                        # Look for matching channel in guide or rig assembly outputs.
                        try:
                            outChannel = rigOutputsByUsername[chanUsername[6:]]
                        except KeyError:
                            pass

                        if outChannel is None:
                            try:
                                outChannel = guideOutputsByUsername[chanUsername[6:]]
                            except KeyError:
                                pass

                        if outChannel is not None:
                            outChannel >> channel

        # It could be that rig and guide assemblies need some inputs from pieces.
        if len(piecesByIndex) > 0:
            for channel in rigInputs:
                chanUsername = modox.ChannelUtils.getChannelUsername(channel)
                # We need input from first and last piece connected
                if chanUsername.startswith('first__'):
                    try:
                        outChannel = pieceOutputsByIndexAndUsername[1][chanUsername[7:]]
                        outChannel >> channel
                    except KeyError:
                        pass
                elif chanUsername.startswith('last__'):
                    try:
                        outChannel = pieceOutputsByIndexAndUsername[sequenceLength][chanUsername[6:]]
                        outChannel >> channel
                    except KeyError:
                        pass

            for channel in guideInputs:
                chanUsername = modox.ChannelUtils.getChannelUsername(channel)
                # We need input from first and last piece connected
                if chanUsername.startswith('first__'):
                    try:
                        outChannel = pieceOutputsByIndexAndUsername[1][chanUsername[7:]]
                        outChannel >> channel
                    except KeyError:
                        pass
                elif chanUsername.startswith('last__'):
                    try:
                        outChannel = pieceOutputsByIndexAndUsername[sequenceLength][chanUsername[6:]]
                        outChannel >> channel
                    except KeyError:
                        pass

    def _fitGuideChain(self, piecesByIndex, serialSetupClass):
        """ Readjusts the guide between base and tip.

        We're going to reset the chain to be a line from base to tip.

        Parameters
        ----------
        tipGuideItem : Item

        serialPieces : {index: Piece}
        """
        if not serialSetupClass.descFitGuide:
            return
        if not serialSetupClass.descGuideChainEnd:
            return

        chainGuideKey = serialSetupClass.descSerialPieceClass.descChainGuide
        if not chainGuideKey:
            return

        tipGuideItem = self.module.getKeyItem(serialSetupClass.descGuideChainEnd)

        tiploc = modo.LocatorSuperType(tipGuideItem.modoItem.internalItem)
        tippos = modo.Vector3()
        tippos[0] = tiploc.position.x.get(0.0, lx.symbol.s_ACTIONLAYER_EDIT)
        tippos[1] = tiploc.position.y.get(0.0, lx.symbol.s_ACTIONLAYER_EDIT)
        tippos[2] = tiploc.position.z.get(0.0, lx.symbol.s_ACTIONLAYER_EDIT)

        pieceCount = len(piecesByIndex)
        factor = 1.0 / (float(pieceCount + 1))

        for x in range(pieceCount):
            index = x + 1
            scalar = index * factor
            pieceGuidePos = tippos * scalar
            loc = modo.LocatorSuperType(piecesByIndex[index].keyItems[chainGuideKey].modoItem.internalItem)
            loc.position.set(pieceGuidePos.values, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_EDIT)

    def _setEditGuidesLinksDrawing(self, piecesByIndex, serialSetupClass):
        """
        Sets item link drawing between edit guides.

        This is going to work provided start, end guide identifiers are set on guides
        that are beginning and end of chain and belong to module itself.
        Also, piece guide needs to have identifier.

        Parameters
        ----------
        piecesByIndex : {index: Piece}
        """
        if not serialSetupClass.descGuideItemLinks:
            return

        # If the chain is 0 - connect start and end guides from the module itself.
        if not piecesByIndex:
            # Link from first edit guide to first piece guide.
            rootItemLink = ItemLinkFeature(self._module.getKeyItem(serialSetupClass.descGuideChainStart))
            rootItemLink.linkedItem = self._module.getKeyItem(serialSetupClass.descGuideChainEnd).modoItem
        # Connect root to first piece, each piece to another and then last piece to chain end item.
        else:
            chainGuideKey = serialSetupClass.descSerialPieceClass.descChainGuide

            # Root to first piece link
            rootItemLink = ItemLinkFeature(self._module.getKeyItem(serialSetupClass.descGuideChainStart))
            rootItemLink.linkedItem = piecesByIndex[1].getKeyItem(chainGuideKey).modoItem

            # Link pieces to one another
            for x in range(len(piecesByIndex) - 1):
                index = x + 1
                itemLink = ItemLinkFeature(piecesByIndex[index].getKeyItem(chainGuideKey))
                itemLink.linkedItem = piecesByIndex[index + 1].getKeyItem(chainGuideKey).modoItem

            # Link last piece to end guide from module.
            itemLink = ItemLinkFeature(piecesByIndex[len(piecesByIndex)].getKeyItem(chainGuideKey))
            itemLink.linkedItem = self.module.getKeyItem(serialSetupClass.descGuideChainEnd).modoItem

    def _updatePieceNames(self, piece, serialPieceSetup):
        self._tmpSerialPieceSetup = serialPieceSetup
        self._tmpIndex = piece.index
        piece.iterateOverItems(self._updateSerialPieceName, includeSubassemblies=True)
        del self._tmpSerialPieceSetup
        del self._tmpIndex

    def _updateSerialPieceName(self, modoItem):
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            return

        nameBefore = rigItem.name
        newName = rigItem.name

        serialNameTokens = self._tmpSerialPieceSetup.descSerialPieceClass.descSerialNameToken
        if type(serialNameTokens) not in (list, tuple):
            serialNameTokens = [serialNameTokens]

        for serialNameToken in serialNameTokens:
            tokenToReplace = serialNameToken + str(self._tmpSerialPieceSetup.descSequenceStart)
            indexString = str(self._tmpIndex - 1 + self._tmpSerialPieceSetup.descSequenceStart)
            newToken = serialNameToken + indexString
            newName = newName.replace(tokenToReplace, newToken)

        if newName != nameBefore:
            rigItem.name = newName

    def _storeCount(self, rawCount, pieceSetupClass):
        try:
            rigAssm = self.module.getFirstSubassemblyOfItemType(c.RigItemType.MODULE_RIG_ASSM)
        except LookupError:
            return

        if pieceSetupClass.descRawCountChannel:
            chan = rigAssm.modoItem.channel(pieceSetupClass.descRawCountChannel)
            if chan:
                chan.set(rawCount, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
        if pieceSetupClass.descCountChannel:
            count = -1 + pieceSetupClass.descSequenceStart + rawCount
            chan = rigAssm.modoItem.channel(pieceSetupClass.descCountChannel)
            if chan:
                chan.set(count, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

    def __init__(self, module):
        self._module = module