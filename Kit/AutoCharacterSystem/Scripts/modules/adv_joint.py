

import lx
import modo
import modox

import rs
from .common import PropEnableTransformSet
from .common import PropEnableSpaceSwitchingTemplate
from .common import PropEnableJointDeformation
from .common import PropEnableControllerAndTransformSet
from .common import PropRotationOrder


KEY_BLENDED_JOINT = 'blend'
KEY_STRETCH_CONTROLLER = 'ctrlstretch'


class PropEnableTranslation(PropEnableControllerAndTransformSet):

    descIdentifier = 'pmove'
    descUsername = 'enableTranslation'
    descRefreshContext = True
    channelSet = modox.c.TransformChannels.PositionAll
    controllerIdent = [rs.c.KeyItem.CONTROLLER, 'ctrlbase']
    descEnableArray = [False, True]  # This means that we don't want to touch the first controller, but second one will be enabled/disabled
    descTooltipMsgTableKey = 'jntAdvEnableTranslation'


class PropEnableStretching(PropEnableControllerAndTransformSet):

    descIdentifier = 'pstretch'
    descUsername = 'enableStretch'
    descRefreshContext = True
    controllerIdent = 'ctrlstretch'
    channelSet = modox.c.TransformChannels.ScaleAll
    descTooltipMsgTableKey = 'enableStretch'


class PropEnableSpaceSwitching(PropEnableSpaceSwitchingTemplate):

    descTooltipMsgTableKey = 'jntAdvEnableSpaceSwitch'


class PropEnableDeformation(PropEnableJointDeformation):
    """
    Adds/removes deformation setup.
    """

    descAimAtJointType = True
    descTooltipMsgTableKey = 'enableDfrm'

    def onEnabled(self, piece):
        # Set the reference guide for tip blended locator.
        tipRefGuide = self.module.getKeyItem(rs.c.KeyItem.TIP_REFERENCE_GUIDE)
        tipJoint = piece.getKeyItem('tipjoint')
        rs.GuideItemFeature(tipJoint).guide = tipRefGuide


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


class PropEnableUpController(PropEnableControllerAndTransformSet):

    descIdentifier = 'pup'
    descUsername = 'enableUp'
    descRefreshContext = True
    controllerIdent = 'ctrlup'
    channelSet = modox.c.TransformChannels.PositionAll
    descTooltipMsgTableKey = 'jntAdvEnableUp'


class PropEnableSecondaryFKController(PropEnableControllerAndTransformSet):

    descIdentifier = 'psecctrl'
    descUsername = 'enableSecCtrl'
    descRefreshContext = True
    controllerIdent = 'ctrlsec'
    channelSet = modox.c.TransformChannels.RotationAll
    descTooltipMsgTableKey = 'enableSecCtrl'


class AdvancedJointModule(rs.base_FeaturedModule):

    descIdentifier = 'std.advJoint'
    descUsername = 'Advanced Joint'
    descFeatures = [PropEnableTranslation,
                    PropEnableStretching,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableDeformation,
                    PropEnableSpaceSwitching,
                    modox.c.FormCommandList.DIVIDER,
                    PropRotationOrderXDominant,
                    PropRotationOrderYDominant,
                    PropEnableUpController,
                    PropEnableSecondaryFKController,
                    ]

    def onSwitchToFK(self, switcherFeature):
        stretchCtrl = self.module.getKeyItem(KEY_STRETCH_CONTROLLER)
        blendedJoint = self.module.getKeyItem(KEY_BLENDED_JOINT)
        masterScaleChan = self.module.getInputChannel(rs.c.InputChannelName.MASTER_SCALE_FACTOR)
        masterScale = masterScaleChan.get(time=None, action=None)
        lx.out(masterScale)
        blendedScale = modox.LocatorUtils.getItemScale(blendedJoint.modoItem, time=None, action=None)  # will it get eval?
        stretchScaleXfrm = modox.LocatorUtils.getTransformItem(stretchCtrl.modoItem, modox.c.TransformType.SCALE)
        stretchScaleXfrm.channel(modox.c.TransformChannels.ScaleZ).set(blendedScale.z / masterScale, time=None, key=True, action=lx.symbol.s_ACTIONLAYER_EDIT)
