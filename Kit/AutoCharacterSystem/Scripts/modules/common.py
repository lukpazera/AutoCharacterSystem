

import lx
import modox

import rs


class PropEnableTransformSet(rs.base_ModuleProperty):
    """
    This property makes it possible to enable/disable pos/rot/scale transforms ona given item within module.
    """

    descIdentifier = 'pmove'
    descUsername = 'Enable Translation'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    controllerIdent = rs.c.KeyItem.CONTROLLER
    channelSet = modox.c.TransformChannels.PositionAll

    def onQuery(self):
        """ Queries whether first controller can be translated.

        Returns
        -------
        bool
        """
        items = self.items
        ctrlIF = rs.Controller(items[0])

        animChans = ctrlIF.animatedChannels
        chanNames = [chan.name for chan in animChans]
        ch = self.channelSet
        result = True
        for name in ch:
            if name not in chanNames:
                result = False
                break
        return result

    def onSet(self, state):
        """
        Parameters
        ----------
        bool
        """
        if state:
            chanState = rs.Controller.ChannelState.ANIMATED
        else:
            chanState = rs.Controller.ChannelState.LOCKED

        for ctrlItem in self.items:
            try:
                ctrlIF = rs.Controller(ctrlItem)
            except TypeError:
                continue

            for chanName in self.channelSet:
                ctrlIF.setChannelState(chanName, chanState)

        return True

    @property
    def items(self):
        """
        Reimplement this if you want different set of items.
        """
        itemIdents = self.controllerIdent
        if type(itemIdents) not in (list, tuple):
            itemIdents = [itemIdents]

        items = []
        for ident in itemIdents:
            try:
                items.append(self.module.getKeyItem(ident))
            except KeyError:
                continue

        return items


class PropEnableControllerAndTransformSet(PropEnableTransformSet):
    """
    This is the same as Toggle transforms but it also hides/unhides
    the controller that is being affected.

    Attributes
    ----------
    descEnableArray : [bool]
        Can be used to choose with controllers should be enabled/disabled on toggle.
        If array is empty (default) all controllers will be enabled/disabled.
    """
    descRefreshContext = True
    descEnableArray = []

    def onSet(self, state):
        PropEnableTransformSet.onSet(self, state)

        if type(self.controllerIdent) not in (list, tuple):
            ctrlIdents = [self.controllerIdent]
        else:
            ctrlIdents = self.controllerIdent

        x = -1
        for ident in ctrlIdents:
            x += 1
            if len(self.descEnableArray) == len(ctrlIdents) and not self.descEnableArray[x]:
                continue
            ctrl = self.module.getKeyItem(ident)
            ctrl.hidden = not state


        if state:
            self.onEnabled()
        else:
            self.onDisabled()

        return True

    def onEnabled(self):
        """ Implement to perform extra actions when deformation is enabled.
        """
        pass

    def onDisabled(self):
        """ Implement to perform extra actions when deformation is disabled.
        """
        pass


class PropRotationOrder(rs.base_ModuleProperty):
    """
    This property makes it possible to set rotation order on a given item
    """

    descIdentifier = 'protorder'
    descUsername = 'Rotation Order'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    itemIdent = rs.c.KeyItem.CONTROLLER
    rotationOrder = modox.c.RotationOrders.Default

    def onQuery(self):
        """ Queries whether first controller can be translated.

        Returns
        -------
        bool
        """
        rigItem = self.module.getKeyItem(self.itemIdent)
        currentOrder = modox.LocatorUtils.getPrimaryRotationOrder(rigItem.modoItem)
        return currentOrder == self.rotationOrder

    def onSet(self, state):
        """ Sets new number of segments for this module.

        Parameters
        ----------
        bool
        """
        rigItem = self.module.getKeyItem(self.itemIdent)
        currentOrder = modox.LocatorUtils.getPrimaryRotationOrder(rigItem.modoItem)
        if currentOrder != self.rotationOrder:
            modox.LocatorUtils.setPrimaryRotationOrder(rigItem.modoItem, self.rotationOrder)


class PropEnableSpaceSwitchingTemplate(rs.base_ModuleProperty):
    """
    Enables/disables space switching by changing arrangement of the rig controller and its properties.
    """

    descIdentifier = 'pspaces'
    descUsername = 'enableSpaceSwitch'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descApplyGuide = True
    descRefreshContext = True
    descTooltipMsgTableKey = 'enableSpaceSwitch'

    descDynaSpaceControllers = 'ctrlTarget'
    descPlugRigSpace = 'plugRigSpace'
    descPlugLocalSpace = 'plugMain'

    descDynaSpaceControllerRefGuides = 'refgdTargetCtrl'
    descLocalSpacePlugRefGuide = 'refgdPlugMain'

    def onQuery(self):
        ctrlItem = self.module.getKeyItem(self.descDynaSpaceControllers)
        parent = ctrlItem.modoItem.parent
        parentRigItem = rs.Item.getFromOther(parent)
        return parentRigItem.identifier == self.descPlugRigSpace

    def onSet(self, state):
        currentState = self.onQuery()
        if state == currentState:
            return

        ctrlItem = self.module.getKeyItem(self.descDynaSpaceControllers)
        ctrlModoItem = ctrlItem.modoItem
        plugRigSpace = self.module.getKeyItem(self.descPlugRigSpace)
        plugMain = self.module.getKeyItem(self.descPlugLocalSpace)
        ctrlRefGuide = self.module.getKeyItem(self.descDynaSpaceControllerRefGuides)

        # Changing set involves:
        # - parenting controller to different plug
        # - reparenting controller ref guide to reflect change in hierarchy above
        # - changing controller's animation space between fixed/dynamic.
        if state:
            guideFolder = self.module.getKeyItem(rs.c.KeyItem.GUIDE_FOLDER)
            ctrlModoItem.setParent(plugRigSpace.modoItem, 0)
            ctrlRefGuide.modoItem.setParent(guideFolder.modoItem, -1)
            rs.run('rs.controller.animSpace space:dynamic item:{%s}' % ctrlModoItem.id)
            self.onEnabled()
        else:
            mainPlugRefGuide = self.module.getKeyItem(self.descLocalSpacePlugRefGuide)
            ctrlModoItem.setParent(plugMain.modoItem, 0)
            ctrlRefGuide.modoItem.setParent(mainPlugRefGuide.modoItem)
            rs.run('rs.controller.animSpace space:fixed item:{%s}' % ctrlModoItem.id)
            self.onDisabled()

        return True

    def onEnabled(self):
        """ Implement to perform extra actions when space switching is enabled.
        """
        pass

    def onDisabled(self):
        """ Implement to perform extra actions when space switching is disabled.
        """
        pass


class PropHolderJoint(rs.base_ModuleProperty):

    descIdentifier = 'holder'
    descUsername = 'Holder Joint'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descApplyGuide = True
    descRefreshContext = True

    descHolderJointPieceIdentifier = 'holder'
    descHolderJointInfluenceIdentifier = rs.c.KeyItem.GENERAL_INFLUENCE
    descHolderBindLocatorIdentifier = rs.c.KeyItem.BIND_LOCATOR
    descLowerDriverBindLocatorIdentifier = 'lower'
    descUpperDriverPieceIdentifier = None  # When not None it should be identifier of a piece the input comes from
    descUpperDriverOutputChannelName = ''  # Rig assembly output channel for the upper driver
    descUpperDriverInputChannelName = ''  # Holder Piece

    def onQuery(self):
        try:
            self.module.getFirstPieceByIdentifier(self.descHolderJointPieceIdentifier)
        except LookupError:
            return False
        return True

    def onSet(self, state):
        currentState = self.onQuery()
        if state == currentState:
            return False

        refresh = False

        try:
            holderPiece = self.module.getFirstPieceByIdentifier(self.descHolderJointPieceIdentifier)
        except LookupError:
            holderPiece = None

        if state:
            # Bail out if knee is already installed
            if holderPiece is not None:
                return

            self._addHolderJoint()
            refresh = True  # To refresh the context after root motion piece was added

        else:
            if holderPiece is None:
                return False
            self.module.removePiece(self.descHolderJointPieceIdentifier)

        return refresh

    # -------- Private methods

    def _addHolderJoint(self):
        newPiece = self.module.addPiece(self.descHolderJointPieceIdentifier, updateItemNames=True)

        # Put holder joint influence in the right place
        moduleDeformFolder = modox.DeformFolder(self.module.getKeyItem(rs.c.KeyItem.DEFORM_FOLDER).modoItem)
        influence = newPiece.getKeyItem(self.descHolderJointInfluenceIdentifier)
        moduleDeformFolder.addDeformer(influence.modoItem)

        self._refreshUpperDriverInput(newPiece)

        # Parenting order for holder joint bind locator is not right when piece is added so we need to
        # set parent again with order set to last.
        lowerDriverBindLoc = self.module.getKeyItem(self.descLowerDriverBindLocatorIdentifier)
        holderBindLoc = newPiece.getKeyItem(self.descHolderBindLocatorIdentifier)
        holderBindLoc.modoItem.setParent(None)
        holderBindLoc.modoItem.setParent(lowerDriverBindLoc.modoItem, -1)

    def _refreshUpperDriverInput(self, holderPiece):
        if not self.descUpperDriverOutputChannelName or not self.descUpperDriverInputChannelName:
            return

        # When using twist joints it might be necessary to set linking between
        # last twist joint and lower driver joint.
        inChan = holderPiece.assemblyModoItem.channel(self.descUpperDriverInputChannelName)
        modox.ChannelUtils.removeAllReverseConnections(inChan)

        if self.descUpperDriverPieceIdentifier is not None:
            inputPiece = self.module.getFirstPieceByIdentifier(self.descUpperDriverPieceIdentifier)
            outChan = inputPiece.assemblyModoItem.channel(self.descUpperDriverOutputChannelName)
            outChan >> inChan
        else:
            outChan = self.module.rigSubassembly.modoItem.channel(self.descUpperDriverOutputChannelName)
            outChan >> inChan


class PropEnableJointDeformation(rs.base_ModuleProperty):
    """
    Adds/removes deformation setup for a single joint module.
    """

    descIdentifier = 'pdeform'
    descUsername = 'enableDfrm'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descApplyGuide = True
    descRefreshContext = True
    descTooltipMsgTableKey = 'enableDfrm'
    descDeformPieceIdentifier = 'deform'
    descDeformFolderKey = rs.c.KeyItem.DEFORM_FOLDER
    descBindJointKey = rs.c.KeyItem.BIND_LOCATOR
    descJointInfluenceKey = rs.c.KeyItem.GENERAL_INFLUENCE
    descJointGuideKey = rs.c.KeyItem.CONTROLLER_GUIDE
    descTipJointGuideKey = rs.c.KeyItem.TIP_CONTROLLER_GUIDE
    descAimAtJointType = False

    def onQuery(self):
        try:
            self.module.getFirstPieceByIdentifier(self.descDeformPieceIdentifier)
        except LookupError:
            return False

        return True

    def onSet(self, state):
        currentState = self.onQuery()
        if state == currentState:
            return False

        result = False
        if not state:
            # remove
            self.module.removePiece(self.descDeformPieceIdentifier)
            # We want to switch controller shape to box when there's no deformation setup.
            self.onDisabled()
            result = True
        else:
            piece = self._addDeformationSetup()
            if piece is not None:
                self.onEnabled(piece)
                result = True
        return result

    def onEnabled(self, piece):
        """ Implement to perform extra actions when deformation is enabled.
        """
        pass

    def onDisabled(self):
        """ Implement to perform extra actions when deformation is disabled.
        """
        pass

    # -------- Private methods

    def _addDeformationSetup(self):
        piece = self.module.addPiece(self.descDeformPieceIdentifier, updateItemNames=True)
        if piece is None:
            return None

        # Add deformers to folder
        deformFolder = piece.getKeyItem(self.descDeformFolderKey)
        deformStack = rs.DeformStack(self.module.rigRootItem)
        deformStack.addToStack(deformFolder, order=rs.DeformStack.Order.NORMALIZED)

        # Set bind locator as effector
        bindloc = self.module.getKeyItem(self.descBindJointKey)
        genInf = piece.getKeyItem(self.descJointInfluenceKey)
        modox.GeneralInfluence(genInf.modoItem).effector = bindloc.modoItem

        # Get the link between main and tip guides working
        # We either create new link, if tip guide is given in description attribute
        # or we re-enable existing one otherwise.
        mainGuide = self.module.getKeyItem(self.descJointGuideKey)
        if not self.descAimAtJointType:
            tipGuide = piece.getKeyItem(self.descTipJointGuideKey)
            rs.run('rs.item.drawLink toItem:{%s} item:{%s}' % (tipGuide.modoItem.id, mainGuide.modoItem.id))
        else:
            tipCtrlGuide = self.module.getKeyItem(self.descTipJointGuideKey)
            tipCtrlGuide.hidden = False

        return piece

