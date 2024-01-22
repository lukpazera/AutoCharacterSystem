

import lx
import modo
import modox

import rs
from . import base_twist
from .common import PropHolderJoint
from .common import PropEnableControllerAndTransformSet


# -------- Variants

class FrontLegVariant(rs.base_ModuleVariant):

    descIdentifier = 'front'
    descUsername = 'Front Leg'
    descName = 'FrontLeg'
    descFilename = 'Quad Front Leg'
    descDefaultThumbnailName = 'ModuleQuadFrontLeg'
    descApplyGuide = True
    descRefreshContext = True

    def onApply(self):
        lowLegGuide = self.module.getKeyItem("gdeditLowLeg")
        posToSet = modox.LocatorUtils.getItemPosition(lowLegGuide.modoItem)

        posToSet.y = -0.255
        posToSet.z = -.12

        modox.LocatorUtils.setItemPosition(lowLegGuide.modoItem, posToSet, action=lx.symbol.s_ACTIONLAYER_EDIT)

        return True


# -------- Upper twist setup

class UpperTwistJointPiece(base_twist.base_TwistJointPiece):

    descIdentifier = 'uptwistjoint'
    descSerialNameToken = ['UpTwist']  # This is the string to replace when renaming serial pieces.
    descKeyBindJoint = 'upbindloc'
    descRelatedRegion = 'Upper'


class UpperTwistJointsSetup(base_twist.base_TwistJointsSetup):

    descSerialPieceClass = UpperTwistJointPiece
    descTwistSetupPieceIdentifier = 'uptwistsetup'
    descKeyParentJoint = 'upbindloc'
    descKeyChildJoint = 'lowbindloc'


class UpperJointsProperty(base_twist.base_TwistJointsProperty):
    """
    Allows for setting a number of joints in the upper arm.
    """

    descIdentifier = 'upjoints'
    descUsername = 'qUpJoints'
    descChannelNameJointCount = 'UpJointsCount'
    descTwistSetupClass = UpperTwistJointsSetup

    descChannelNameMinTwist = 'UpperMinimumTwist'
    descChannelNameMaxTwist = 'UpperMaximumTwist'

    descTooltipMsgTableKey = 'qlegUpperJoints'


# -------- Lower twist setup

class LowerTwistJointPiece(base_twist.base_TwistJointPiece):

    descIdentifier = 'lowtwistjoint'
    descSerialNameToken = ['LowTwist']  # This is the string to replace when renaming serial pieces.
    descKeyBindJoint = 'lowbindloc'
    descRelatedRegion = 'Lower'


class LowerTwistJointsSetup(base_twist.base_TwistJointsSetup):

    descSerialPieceClass = LowerTwistJointPiece
    descTwistSetupPieceIdentifier = 'lowtwistsetup'
    descKeyParentJoint = 'lowbindloc'
    descKeyChildJoint = 'footbindloc'


class LowerJointsProperty(base_twist.base_TwistJointsProperty):
    """
    Allows for setting a number of joints in the upper arm.
    """

    descIdentifier = 'lowjoints'
    descUsername = 'qLowJoints'
    descChannelNameJointCount = 'LowJointsCount'
    descTwistSetupClass = LowerTwistJointsSetup

    descChannelNameMinTwist = 'LowerMinimumTwist'
    descChannelNameMaxTwist = 'LowerMaximumTwist'
    desc1JointMinMaxTwist = [0.0, 1.0]
    desc2JointMinMaxTwist = [0.0, 0.5]

    descTooltipMsgTableKey = 'qlegLowerJoints'


class PropHipHolderJoint(PropHolderJoint):

    descIdentifier = 'hip'
    descUsername = 'holdHip'
    descHolderJointPieceIdentifier = 'hip'

    descHolderBindLocatorIdentifier = 'hipbloc'
    descHolderJointInfluenceIdentifier = 'hipinf'
    descLowerDriverBindLocatorIdentifier = 'upbindloc'

    descTooltipMsgTableKey = 'qlegHipHolder'


class PropKneeHolderJoint(PropHolderJoint):

    descIdentifier = 'knee'
    descUsername = 'holdKnee'
    descHolderJointPieceIdentifier = 'knee'

    descHolderBindLocatorIdentifier = 'kneebloc'
    descHolderJointInfluenceIdentifier = 'kneeinf'
    descLowerDriverBindLocatorIdentifier = 'lowbindloc'

    descTooltipMsgTableKey = 'qlegKneeHolder'


class PropAnkleHolderJoint(PropHolderJoint):

    descIdentifier = 'ankle'
    descUsername = 'holdAnkle'
    descHolderJointPieceIdentifier = 'ankle'

    descHolderBindLocatorIdentifier = 'anklebloc'
    descHolderJointInfluenceIdentifier = 'ankleinf'
    descLowerDriverBindLocatorIdentifier = 'footbindloc'

    descTooltipMsgTableKey = 'qlegAnkleHolder'


class PropEnableXZStretchingController(PropEnableControllerAndTransformSet):

    descIdentifier = 'pstretch'
    descUsername = 'enableStretch'
    descRefreshContext = True
    controllerIdent = 'ctrllegstretch'
    channelSet = [modox.c.TransformChannels.ScaleX,
                  modox.c.TransformChannels.ScaleZ]
    descTooltipMsgTableKey = 'enableStretch'


class QuadLegModule(rs.base_FeaturedModule):
    
    descIdentifier = 'std.quadLeg'
    descUsername = 'Quadruped Leg'
    descVariants = [FrontLegVariant]
    descFeatures = [UpperJointsProperty,
                    LowerJointsProperty,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableXZStretchingController,
                    modox.c.FormCommandList.DIVIDER,
                    PropHipHolderJoint,
                    PropKneeHolderJoint,
                    PropAnkleHolderJoint]

    def onSwitchToFK(self, switcherFeature):
        solver = switcherFeature.ikChain.ikSolvers[0]
        scaleFactor = solver.scaleOutput[0]

        legStretchCtrl = self.module.getKeyItem('ctrllegstretch')
        scale = modox.LocatorUtils.getItemScale(legStretchCtrl.modoItem)
        scale.z = scaleFactor
        modox.LocatorUtils.setItemScale(legStretchCtrl.modoItem, scale, time=None, key=True, action=lx.symbol.s_ACTIONLAYER_EDIT)

