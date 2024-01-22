
import lx
import modo
import modox

import rs
from .common import PropEnableTransformSet
from .common import PropEnableControllerAndTransformSet
from .common import PropEnableJointDeformation
from .common import PropRotationOrder
from .common import PropEnableSpaceSwitchingTemplate


class RigidVariant(rs.base_ModuleVariant):
    """
    NOT USED ANYMORE.
    USER CAN SIMPLY SWITCH DEFORMATION OFF ON THE STANDARD JOINT.
    """
    descIdentifier = 'rigid'
    descUsername = 'Rigid Joint'
    descName = 'RigidJoint'
    descFilename = 'Rigid Joint'
    descDefaultThumbnailName = 'ModuleRigidJoint'
    descApplyGuide = False
    descRefreshContext = True

    def onApply(self):
        # Remove deformations setup.
        # This is a bit of a hack, we spawn the enable deformation property
        # and set it to false.
        # Note that the guide/context updates won't happen
        # when the property is called manually like that.
        enableDeformation = PropEnableDeformation(self.module)
        enableDeformation.onSet(False)

        return True


class PropEnableDeformation(PropEnableJointDeformation):

    def onDisabled(self):
        cmdBox = CmdControllerShapeBox(self.module)
        cmdBox.run()

    def onEnabled(self, piece):
        cmdLink = CmdControllerShapeLink(self.module)
        cmdLink.run()


class PropEnableSecondaryController(PropEnableControllerAndTransformSet):

    descIdentifier = 'psecctrl'
    descUsername = 'enableSecCtrl'
    descRefreshContext = True
    controllerIdent = 'ctrlsec'
    channelSet = modox.c.TransformChannels.RotationAll
    descTooltipMsgTableKey = 'enableSecCtrl'

    def onEnabled(self):
        cmdBox = CmdControllerShapeBox(self.module)
        cmdBox.run()

        # Reparent tip joint (if it exists).
        # The tip joint won't be there if there's no deform piece installed in the module.
        try:
            piece = self.module.getFirstPieceByIdentifier(PropEnableDeformation.descDeformPieceIdentifier)
        except LookupError:
            return

        tipJoint = piece.getKeyItem('tipjoint')

        secondaryCtrl = self.module.getKeyItem(self.controllerIdent)
        tipJoint.modoItem.setParent(secondaryCtrl.modoItem, 0)

    def onDisabled(self):
        # Reparent tip joint (if it exists).
        piece = self.module.getFirstPieceByIdentifier(PropEnableDeformation.descDeformPieceIdentifier)
        try:
            tipJoint = piece.getKeyItem('tipjoint')
        except LookupError:
            return

        primaryCtrl = self.module.getKeyItem(rs.c.KeyItem.CONTROLLER)
        tipJoint.modoItem.setParent(primaryCtrl.modoItem, 0)


class PropEnableTranslation(PropEnableTransformSet):

    descIdentifier = 'pmove'
    descUsername = 'enableTranslation'
    channelSet = modox.c.TransformChannels.PositionAll
    descTooltipMsgTableKey = 'stdjntEnableTranslation'


class PropEnableRotation(PropEnableTransformSet):

    descIdentifier = 'prot'
    descUsername = 'enableRotation'
    channelSet = modox.c.TransformChannels.RotationAll
    descTooltipMsgTableKey = 'stdjntEnableRotation'


class PropEnableStretching(PropEnableControllerAndTransformSet):

    descIdentifier = 'pstretch'
    descUsername = 'enableStretch'
    channelSet = modox.c.TransformChannels.ScaleAll
    controllerIdent = 'ctrlstretch'
    descTooltipMsgTableKey = 'enableStretch'


class PropEnableSpaceSwitching(PropEnableSpaceSwitchingTemplate):

    descDynaSpaceControllers = 'ctrl'
    descDynaSpaceControllerRefGuides = 'refgdCtrl'

    def onEnabled(self):
        translation = PropEnableTranslation(self.module)
        translation.onSet(True)
        rotation = PropEnableRotation(self.module)
        rotation.onSet(True)


class PropRotationOrderXDominant(PropRotationOrder):
    """
    Sets rotation orders on all controllers such that X axis is dominant (has full range of motion).
    Useful for situation when vertical movement is the main axis of movement.
    """

    descIdentifier = 'pxrotord'
    descUsername = 'rotOrderX'
    rotationOrder = modox.c.RotationOrders.ZYX
    descTooltipMsgTableKey = 'rotOrderX'


class PropRotationOrderYDominant(PropRotationOrder):
    """
    Sets rotation orders on all controllers such that Y axis is dominant (has full range of motion).
    Useful for situation when horizontal movement is the main axis of motion.
    """

    descIdentifier = 'pyrotord'
    descUsername = 'rotOrderY'
    rotationOrder = modox.c.RotationOrders.ZXY
    descTooltipMsgTableKey = 'rotOrderY'


class CmdControllerShapeLink(rs.base_ModuleCommand):

    descIdentifier = 'cmdlinkshape'
    descUsername = 'stdjntLinkShape'
    descTooltipMsgTableKey = 'stdjntLinkShape'

    def run(self, arguments=[]):
        ctrl = self.module.getKeyItem(rs.c.KeyItem.CONTROLLER)

        rs.run('!item.channel locator$isShape circle item:{%s}' % ctrl.modoItem.id)
        rs.run('!item.channel locator$isRadius 0.0 item:{%s}' % ctrl.modoItem.id)

        rs.run('!item.channel locator$link custom item:{%s}' % ctrl.modoItem.id)


class CmdControllerShapeBox(rs.base_ModuleCommand):

    descIdentifier = 'cmdboxshape'
    descUsername = 'stdjntBoxShape'
    descTooltipMsgTableKey = 'stdjntBoxShape'

    def run(self, arguments=[]):
        ctrl = self.module.getKeyItem(rs.c.KeyItem.CONTROLLER)

        rs.run('!item.channel locator$link none item:{%s}' % ctrl.modoItem.id)
        rs.run('!item.channel locator$isShape box item:{%s}' % ctrl.modoItem.id)


class ControllerVariant(rs.base_ModuleVariant):

    descIdentifier = 'ctrl'
    descUsername = 'Controller'
    descName = 'Controller'
    descFilename = 'Controller'
    descDefaultThumbnailName = 'ModuleRigidController'
    descApplyGuide = False
    descRefreshContext = True
    descFeatures = [PropEnableTranslation,
                    PropEnableRotation,
                    PropEnableStretching,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableSpaceSwitching,
                    PropEnableSecondaryController,
                    modox.c.FormCommandList.DIVIDER,
                    PropRotationOrderXDominant,
                    PropRotationOrderYDominant,
                    ]

    def onApply(self):
        # Remove deformations setup.
        # This is a bit of a hack, we spawn the enable deformation property
        # and set it to false.
        # Note that the guide/context updates won't happen
        # when the property is called manually like that.
        enableDeformation = PropEnableDeformation(self.module)
        enableDeformation.onSet(False)
        enableTranslation = PropEnableTranslation(self.module)
        enableTranslation.onSet(True)

        # We also want the Y dominant rotation order to be set
        # to be in line with MODO's default rotation order.
        dominantY = PropRotationOrderYDominant(self.module)
        dominantY.onSet(True)

        bindloc = self.module.getKeyItem(rs.c.KeyItem.BIND_LOCATOR)
        # This is CRUCIAL here.
        # We do want to keep this bind locator in there but it needs to be hidden.
        # The reason is that without this hidden bind locator there will be no link
        # when the bake bind skeleton hierarchy will be built.
        # This bind loc basically connects this module's socket and plug without appearing
        # in the baked hierarchy itself.
        bindloc.hidden = True
        return True


class StandardJointModule(rs.base_FeaturedModule):

    descIdentifier = 'std.joint'
    descUsername = 'Standard Joint'
    descFeatures = [PropEnableTranslation,
                    PropEnableRotation,
                    PropEnableStretching,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableDeformation,
                    PropEnableSpaceSwitching,
                    PropEnableSecondaryController,
                    modox.c.FormCommandList.DIVIDER,
                    PropRotationOrderXDominant,
                    PropRotationOrderYDominant,
                    modox.c.FormCommandList.DIVIDER,
                    CmdControllerShapeBox,
                    CmdControllerShapeLink
                    ]
    descVariants = [ControllerVariant]