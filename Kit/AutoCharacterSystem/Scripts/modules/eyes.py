

import lx
import modo
import modox

import rs
from .std_joint import PropEnableDeformation as EyeEnableDeformation
from .std_joint import PropRotationOrderYDominant
from .std_joint import PropEnableTranslation as EyeEnableTranslation
from .adv_joint import PropEnableDeformation as MainCtrlEnableDeformation


PIECE_ID_EYE_EYEBALLS_SETUP = 'eyeballsset'


class CmdSelfBuild(rs.base_ModuleCommand):

    descIdentifier = 'cmdsbuild'
    descUsername = 'Rebuild'
    descScope = rs.base_ModuleProperty.Scope.LOCAL
    descApplyGuide = True
    descRefreshContext = True
    descDeveloperAccess = True

    def run(self, arguments):
        self._new()
        return True

    @property
    def featuredModule(self):
        return EyesModule(super(CmdSelfBuild, self).module)

    # -------- Private methods

    def _new(self):
        self._clear()
        fmodule = self.featuredModule
        mainCtrlModule = fmodule.addMainControllerModule()
        fmodule.setup2eyes(mainCtrlModule)

    def _clear(self):
        # Get modules for clearing in correct order.
        # "Lowest" modules go first, parent one at the end and delete them in that order.
        submodules = self.module.getSubmodulesWithIdentifier(EyesModule.EYE_SUBMODULE_ID)
        submodules.extend(self.module.getSubmodulesWithIdentifier(EyesModule.MAIN_CTRL_SUBMODULE_ID))

        for module in submodules:
            module.selfDelete()


class PropEyelids(rs.base_ModuleProperty):
    """ Adds/removes eyelids.
    """

    descIdentifier = 'peyelids'
    descUsername = 'eyelids'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descApplyGuide = True
    descRefreshContext = True
    descTooltipMsgTableKey = 'eyesEyelids'

    _MAIN_CTRL_SUBMODULE_ID = 'mctrl'
    _EYELIDS_MODULE_ID = 'std.eyelids'
    _EYE_SUBMODULE_ID = 'eye'
    _CHAN_EYES_OPEN_GLOBAL = 'EyesOpenGlobalFactor'
    _PIECE_ID_EYEBALLS_SETUP = 'eyeballsset'

    def onQuery(self):
        """

        Returns
        -------
        bool
        """
        subModulues = self.module.getSubmodulesWithIdentifier(self._EYELIDS_MODULE_ID)
        if not subModulues:
            return False
        return True

    def onSet(self, state):
        currentState = self.onQuery()
        if currentState == state:
            return False

        if state:
            self._addEyelids()
        else:
            self._removeEyelids()

        return True

    # -------- Private methods

    def _addEyelids(self):
        moduleOp = rs.ModuleOperator(self.module.rigRootItem)
        rEyelidsModule = moduleOp.addModuleFromPreset(rs.c.ModulePresetFilename.EYELIDS)
        self.module.addSubmodule(rEyelidsModule, self._EYELIDS_MODULE_ID)
        rEyelidsModule.side = rs.c.Side.RIGHT
        lEyelidsModule = moduleOp.addModuleFromPreset(rs.c.ModulePresetFilename.EYELIDS)
        self.module.addSubmodule(lEyelidsModule, self._EYELIDS_MODULE_ID)
        lEyelidsModule.side = rs.c.Side.LEFT

        # Plug eyelids into eyes
        sockets = self.module.socketsByReferenceNames
        rsocket = sockets['REyelidSpace']
        lsocket = sockets['LEyelidSpace']

        rplugs = rEyelidsModule.plugsByNames
        rplugs["Main"].connectToSocket(rsocket)
        rplugs['Main'].hidden = True

        lplugs = lEyelidsModule.plugsByNames
        lplugs["Main"].connectToSocket(lsocket)
        lplugs['Main'].hidden = True

        # Set up symmetry between eyelid modules
        # This has to be done via module operator
        moduleOp = rs.ModuleOperator(self.module.rigRootItem)
        moduleOp.setSymmetry(lEyelidsModule, rEyelidsModule)

        # Now attach eyelid main guides to eye guides.
        # I'm not going to use regular attach because it attaches both world position and rotation.
        # I want to attach position only.
        eyeballModules = self.module.getSubmodulesWithIdentifier(self._EYE_SUBMODULE_ID)

        if eyeballModules[0].side == rs.c.Side.RIGHT:
            rEyeballModule = eyeballModules[0]
            lEyeballModule = eyeballModules[1]
        else:
            lEyeballModule = eyeballModules[0]
            rEyeballModule = eyeballModules[1]

        rRootGuide = rEyelidsModule.getKeyItem(rs.c.KeyItem.ROOT_CONTROLLER_GUIDE)
        lRootGuide = lEyelidsModule.getKeyItem(rs.c.KeyItem.ROOT_CONTROLLER_GUIDE)

        rEyeballGuide = rEyeballModule.getKeyItem(rs.c.KeyItem.CONTROLLER_GUIDE)
        lEyeballGuide = lEyeballModule.getKeyItem(rs.c.KeyItem.CONTROLLER_GUIDE)

        rEyeballWPosChan = modox.LocatorUtils.getItemWorldPositionMatrixChannel(rEyeballGuide.modoItem)
        lEyeballWPosChan = modox.LocatorUtils.getItemWorldPositionMatrixChannel(lEyeballGuide.modoItem)

        rEyelidWPosChan= modox.LocatorUtils.getItemWorldPositionMatrixChannel(rRootGuide.modoItem)
        lEyelidWPosChan = modox.LocatorUtils.getItemWorldPositionMatrixChannel(lRootGuide.modoItem)

        rEyeballWPosChan >> rEyelidWPosChan
        lEyeballWPosChan >> lEyelidWPosChan

        # We need to connect main eyes panel to drive eyelids and also remove controller feature from eyelids.

        # Add Eyes Open and Eyes Follow channels
        # Order of getting channels here is the order in which they will be created.
        panel = self._getMainCtrlModulePanel()
        globalEyesFollowChannel = self._getGlobalEyelidsFollowEyeballsChannelFromPanel(panel)
        globalEyesOpenChannel = self._getGlobalEyesOpenChannelFromPanel(panel)

        ctrl = rs.Controller(panel)
        ctrl.setChannelState(globalEyesOpenChannel.name, rs.Controller.ChannelState.ANIMATED)
        ctrl.setChannelState(globalEyesFollowChannel.name, rs.Controller.ChannelState.ANIMATED)

        rEyelidsRigAssm = rEyelidsModule.getFirstSubassemblyOfItemType(rs.c.RigItemType.MODULE_RIG_ASSM)
        lEyelidsRigAssm = lEyelidsModule.getFirstSubassemblyOfItemType(rs.c.RigItemType.MODULE_RIG_ASSM)

        globalEyesOpenChannel >> rEyelidsRigAssm.modoItem.channel(self._CHAN_EYES_OPEN_GLOBAL)
        globalEyesOpenChannel >> lEyelidsRigAssm.modoItem.channel(self._CHAN_EYES_OPEN_GLOBAL)

        # Connect the eyes follow eyeballs channels.
        eyeballsPiece = self.module.getFirstPieceByIdentifier(self._PIECE_ID_EYEBALLS_SETUP)
        eyelidsFollowPieceChannel = eyeballsPiece.assemblyModoItem.channel('EyelidsFollowEyeballs')
        globalEyesFollowChannel >> eyelidsFollowPieceChannel

        # For the eyes open slider we also need to plug it into the eyes open region
        # on the eyes module.
        gestureNode = self.module.getKeyItem('gestEyeOpen')
        lx.eval('channelItem.link cmdRegion.channels.graph {%s} {%s:%s} add' % (gestureNode.modoItem.id,
                                                                                panel.modoItem.id,
                                                                                'EyesOpen'))

    def _removeEyelids(self):
        subModulues = self.module.getSubmodulesWithIdentifier(self._EYELIDS_MODULE_ID)
        for module in subModulues:
            module.selfDelete()

        # Remove eyes open global channel
        panel = self._getMainCtrlModulePanel()
        globalEyesOpenChannel = self._getGlobalEyesOpenChannelFromPanel(panel)
        globalEyesFollowChannel = self._getGlobalEyelidsFollowEyeballsChannelFromPanel(panel)

        ctrl = rs.Controller(panel)
        ctrl.setChannelState(globalEyesOpenChannel.name, rs.Controller.ChannelState.IGNORE)
        ctrl.setChannelState(globalEyesFollowChannel.name, rs.Controller.ChannelState.IGNORE)

        # This is ridiculous but it looks like there's no way to remove channel via SDK
        # and the command doesn't take arguments, the relevant channel needs to be selected.
        modox.ChannelSelection().set([globalEyesOpenChannel, globalEyesFollowChannel], modox.SelectionMode.REPLACE)
        rs.run('channel.delete')

    def _getMainCtrlModulePanel(self):
        ctrlModule = self.module.getSubmodulesWithIdentifier(self._MAIN_CTRL_SUBMODULE_ID)[0]
        return ctrlModule.getKeyItem(rs.c.KeyItem.PANEL_CONTROLLER)

    def _getGlobalEyesOpenChannelFromPanel(self, panel):
        globalEyesOpenChannel = panel.modoItem.channel('EyesOpen')
        xitem = modox.Item(panel.modoItem)
        if globalEyesOpenChannel is None:
            globalEyesOpenChannel = xitem.addUserChannel('EyesOpen',
                                                         lx.symbol.sTYPE_FLOAT,
                                                         'Eyes Open',
                                                         minVal=0.0,
                                                         useMin=True,
                                                         default=1.0)
            rs.run('channel.setup channel:{%s}' % modox.ChannelUtils.getChannelIdent(globalEyesOpenChannel))
        return globalEyesOpenChannel

    def _getGlobalEyelidsFollowEyeballsChannelFromPanel(self, panel):
        globalEyelidsFollowChannel = panel.modoItem.channel('EyelidsFollow')
        xitem = modox.Item(panel.modoItem)
        if globalEyelidsFollowChannel is None:
            globalEyelidsFollowChannel = xitem.addUserChannel('EyelidsFollow',
                                                         lx.symbol.sTYPE_PERCENT,
                                                         'Eyelids Follow Eyeballs',
                                                         minVal=0.0,
                                                         maxVal=100.0,
                                                         useMin=True,
                                                         useMax=True,
                                                         default=0.0)
            rs.run('channel.setup channel:{%s}' % modox.ChannelUtils.getChannelIdent(globalEyelidsFollowChannel))
        return globalEyelidsFollowChannel


class EyesModule(rs.base_FeaturedModule):

    descIdentifier = 'std.eyes'
    descUsername = 'Eyes'
    descFeatures = [CmdSelfBuild, PropEyelids]

    MAIN_CTRL_SUBMODULE_ID = 'mctrl'
    EYE_SUBMODULE_ID = 'eye'

    def addMainControllerModule(self):
        """ Advanced joint module serves as the main controller for eyes setup.
        """
        moduleOp = rs.ModuleOperator(self.module.rigRootItem)
        mainCtrlModule = moduleOp.addModuleFromPreset(rs.c.ModulePresetFilename.ADV_JOINT)
        self.module.addSubmodule(mainCtrlModule, self.MAIN_CTRL_SUBMODULE_ID)
        mainCtrlModule.name = 'EyesController'

        # Remove deformation setup and translation ability by default.
        # To do this I want to access eye module properties directly.
        mainFeaturedModule = rs.FeaturedModuleOperator.getAsFeaturedModule(mainCtrlModule)
        mainFeaturedModule.onSet(MainCtrlEnableDeformation.descIdentifier, False)

        # Change the main controller distance by setting Rest Distance Factor channel
        # on the module's assembly.
        mainCtrlModule.assemblyItem.setChannelProperty('TargetRestDistanceFactor', 2.0)

        # Change look of the main controller
        targetCtrl = mainCtrlModule.getKeyItem(rs.c.KeyItem.TARGET_CONTROLLER)
        rs.run('item.channel locator$isShape plane item:{%s}' % targetCtrl.modoItem.id)
        rs.run('item.channel locator$isSize.X 0.15 item:{%s}' % targetCtrl.modoItem.id)

        # Plug adv joint module to the socket on the main module.
        sockets = self.module.socketsByNames
        socket = sockets['Main']
        plugs = mainCtrlModule.plugsByNames
        plugs["Main"].connectToSocket(socket)
        plugs['Main'].hidden = True

        # Hide bind skeleton joint
        bindloc = mainCtrlModule.getKeyItem(rs.c.KeyItem.BIND_LOCATOR)
        bindloc.hidden = True

        # Disable the target base controller, we won't need it in eyes setup.
        targetBaseCtrl = mainCtrlModule.getKeyItem('ctrlbase')
        targetBaseCtrl.hidden = True
        targetBaseCtrl.setChannelProperty('select', modox.c.ItemSelectable.NO)
        targetBaseCtrl.setChannelProperty('isShape', 'circle')
        targetBaseCtrl.setChannelProperty('isRadius', 0)
        ctrlIF = rs.Controller(targetBaseCtrl)
        ctrlIF.setChannelState(modox.c.TransformChannels.RotationZ, rs.Controller.ChannelState.LOCKED)

        fkctrl = mainCtrlModule.getKeyItem(rs.c.KeyItem.CONTROLLER)
        fkctrl.setChannelProperty('isShape', 'pyramid')
        fkctrl.setChannelProperty('isAxis', 'z')
        fkctrl.setChannelProperty('isSize.X', 0.075)
        fkctrl.setChannelProperty('isSize.Y', 0.075)
        fkctrl.setChannelProperty('isSize.Z', -0.075)
        fkctrl.setChannelProperty('isOffset.Z', 0.075)

        return mainCtrlModule

    def setup2eyes(self, mainCtrlModule):
        rsocket = self.module.getKeyItem('reyeballsocket', includePieces=True)
        lsocket = self.module.getKeyItem('leyeballsocket', includePieces=True)
        reyeModule = self.addEyeModule(rsocket, rs.c.Side.RIGHT)
        leyeModule = self.addEyeModule(lsocket, rs.c.Side.LEFT)

        self.linkEyeballSocketsToMainCtrlModule(mainCtrlModule)
        self.linkEyeballModuleSocketToEyeEyeballsSetupPiece(reyeModule, leyeModule)

        moduleOp = rs.ModuleOperator(self.module.rigRootItem)
        moduleOp.setSymmetry(leyeModule, reyeModule)

        # Attach eyeball space guides in the main module to their counterparts
        # in the eyeball modules. We only want the eyeball modules guides to be editable
        # and the main module to conform to that.
        reyeBallGuide = reyeModule.getKeyItem(rs.c.KeyItem.CONTROLLER_GUIDE)
        leyeBallGuide = leyeModule.getKeyItem(rs.c.KeyItem.CONTROLLER_GUIDE)
        mainRSocketGuide = self.module.getKeyItem('reyeballgd', includePieces=True)
        mainLSocketGuide = self.module.getKeyItem('leyeballgd', includePieces=True)

        rigRootIdent = self.module.rigRootItem.modoItem.id
        rs.run('rs.guide.attachToOther guideFrom:{%s} guideTo:{%s} rootItem:{%s}' % (mainRSocketGuide.modoItem.id, reyeBallGuide.modoItem.id, rigRootIdent))
        rs.run('rs.guide.attachToOther guideFrom:{%s} guideTo:{%s} rootItem:{%s}' % (mainLSocketGuide.modoItem.id, leyeBallGuide.modoItem.id, rigRootIdent))

        # Attach the main eyes guide to the advanced joint base guide
        rootCtrlGuide = self.module.getKeyItem(rs.c.KeyItem.ROOT_CONTROLLER_GUIDE)
        advJointGuide =  mainCtrlModule.getKeyItem(rs.c.KeyItem.CONTROLLER_GUIDE)
        rs.run('rs.guide.attachToOther guideFrom:{%s} guideTo:{%s} rootItem:{%s}' % (rootCtrlGuide.modoItem.id, advJointGuide.modoItem.id, rigRootIdent))

        # Link eyeballs guides to main ctrl guide so they move with it.
        rs.run('rs.guide.link rootFrom:{%s} guideTo:{%s} rootItem:{%s}' % (reyeBallGuide.modoItem.id, advJointGuide.modoItem.id, rigRootIdent))
        rs.run('rs.guide.link rootFrom:{%s} guideTo:{%s} rootItem:{%s}' % (leyeBallGuide.modoItem.id, advJointGuide.modoItem.id, rigRootIdent))

    def linkEyeballSocketsToMainCtrlModule(self, mainCtrlModule):
        mainSocket = mainCtrlModule.socketsByNames['Main']
        reyeSocket = self.module.getKeyItem('reyeballsocket', includePieces=True)
        leyeSocket = self.module.getKeyItem('leyeballsocket', includePieces=True)

        mainSocketWRotMtx = modox.LocatorUtils.getItemWorldRotationMatrixChannel(mainSocket.modoItem)
        reyeSocketWRotMtx = modox.LocatorUtils.getItemWorldRotationMatrixChannel(reyeSocket.modoItem)
        leyeSocketWRotMtx = modox.LocatorUtils.getItemWorldRotationMatrixChannel(leyeSocket.modoItem)

        mainSocketWRotMtx >> reyeSocketWRotMtx
        mainSocketWRotMtx >> leyeSocketWRotMtx

    def linkEyeballModuleSocketToEyeEyeballsSetupPiece(self, reyeballModule, leyeballModule):
        """
        The eye main module contains eyeballs setup piece in which the space for
        eyelids is defined.
        This space is a mix between parent space (head) and eyeballs orientation,
        depending on the eyelids follow eyeballs slider value.
        This function needs to plug eyeball sockets into the eyeballs setup piece
        so the mixing has the eval eyeballs orientation.
        """
        setupPiece = self.module.getFirstPieceByIdentifier(PIECE_ID_EYE_EYEBALLS_SETUP)
        rEyeballSpaceChan = setupPiece.assemblyModoItem.channel('RightEyeballSpaceEval')
        lEyeballSpaceChan = setupPiece.assemblyModoItem.channel('LeftEyeballSpaceEval')

        rsockets = reyeballModule.socketsByNames
        reyeballSocket = rsockets['Main']
        lsockets = leyeballModule.socketsByNames
        leyeballSocket = lsockets['Main']

        rsocketWRotChan = modox.LocatorUtils.getItemWorldRotationMatrixChannel(reyeballSocket.modoItem)
        lsocketWRotChan = modox.LocatorUtils.getItemWorldRotationMatrixChannel(leyeballSocket.modoItem)

        rsocketWRotChan >> rEyeballSpaceChan
        lsocketWRotChan >> lEyeballSpaceChan

    def addEyeModule(self, socket, side=rs.c.Side.CENTER):
        moduleOp = rs.ModuleOperator(self.module.rigRootItem)
        eyeModule = moduleOp.addModuleFromPreset(rs.c.ModulePresetFilename.STD_JOINT)
        self.module.addSubmodule(eyeModule, self.EYE_SUBMODULE_ID)
        eyeModule.name = 'Eyeball'
        eyeModule.side = side

        # Remove deformation setup and translation ability by default.
        # Also switch rotation order to Y dominant.
        # To do this I want to access eye module properties directly.
        eyeFeaturedModule = rs.FeaturedModuleOperator.getAsFeaturedModule(eyeModule)
        eyeFeaturedModule.onSet(EyeEnableDeformation.descIdentifier, False)
        eyeFeaturedModule.onSet(PropRotationOrderYDominant.descIdentifier, True)

        # Plug into the socket which should be eyes ctrl one.
        plugs = eyeModule.plugsByNames
        plugs["Main"].connectToSocket(socket)
        plugs['Main'].hidden = True

        # Disable Z rotation as eyes can't be banked.
        ctrl = eyeModule.getKeyItem(rs.c.KeyItem.CONTROLLER)
        ctrlIF = rs.Controller(ctrl)
        ctrlIF.setChannelState(modox.c.TransformChannels.RotationZ, rs.Controller.ChannelState.LOCKED)

        ctrl.setChannelProperty('isShape', 'sphere')
        ctrl.setChannelProperty('isRadius', 0.05)

        # Edit guide look as well
        # We want guide to clearly show that it's separate from the one that allows
        # for setting eyelids orientation.
        ctrlGuide = eyeModule.getKeyItem(rs.c.KeyItem.CONTROLLER_GUIDE)
        ctrlGuide.setChannelProperty('isShape', 'pyramid')
        size = ctrlGuide.getChannelProperty('isSize.X')
        ctrlGuide.setChannelProperty('isOffset.Z', size * 0.5)
        ctrlGuide.setChannelProperty('rsgdDraw', 0)

        if side == rs.c.Side.RIGHT:
            offset = modo.Vector3(-0.1, 0, 0)
            rs.ModuleGuide(eyeModule).offsetPosition(offset)
        elif side == rs.c.Side.LEFT:
            offset = modo.Vector3(0.1, 0, 0)
            rs.ModuleGuide(eyeModule).offsetPosition(offset)

        return eyeModule
