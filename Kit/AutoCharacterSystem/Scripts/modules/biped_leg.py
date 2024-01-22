

import lx
import modox
import rs
from . import base_twist
from .common import PropHolderJoint
from .common import PropEnableControllerAndTransformSet


# -------- Thigh twist setup

class ThighTwistJointPiece(base_twist.base_TwistJointPiece):

    descIdentifier = 'thightwistjoint'
    descSerialNameToken = ['ThighTwist']  # This is the string to replace when renaming serial pieces.
    descKeyBindJoint = 'thighbindloc'
    descRelatedRegion = 'Thigh'


class ThighTwistJointsSetup(base_twist.base_TwistJointsSetup):

    descSerialPieceClass = ThighTwistJointPiece
    descTwistSetupPieceIdentifier = 'thightwistsetup'
    descKeyParentJoint = 'thighbindloc'
    descKeyChildJoint = 'shinbindloc'


class ThighJointsProperty(base_twist.base_TwistJointsProperty):
    """
    Allows for setting a number of joints in the upper arm.
    """

    descIdentifier = 'thighjoints'
    descUsername = 'thighJoints'
    descChannelNameJointCount = 'ThighJointsCount'
    descTwistSetupClass = ThighTwistJointsSetup

    descChannelNameMinTwist = 'ThighMinimumTwist'
    descChannelNameMaxTwist = 'ThighMaximumTwist'

    descTooltipMsgTableKey = 'legThighJoints'

# -------- Shin twist setup

class ShinTwistJointPiece(base_twist.base_TwistJointPiece):

    descIdentifier = 'shintwistjoint'
    descSerialNameToken = ['ShinTwist']  # This is the string to replace when renaming serial pieces.
    descKeyBindJoint = 'shinbindloc'
    descRelatedRegion = 'Shin'


class ShinTwistJointsSetup(base_twist.base_TwistJointsSetup):

    descSerialPieceClass = ShinTwistJointPiece
    descTwistSetupPieceIdentifier = 'shintwistsetup'
    descKeyParentJoint = 'shinbindloc'
    descKeyChildJoint = 'footbindloc'


class ShinJointsProperty(base_twist.base_TwistJointsProperty):
    """
    Allows for setting a number of joints in the upper arm.
    """

    descIdentifier = 'shinjoints'
    descUsername = 'shinJoints'
    descChannelNameJointCount = 'ShinJointsCount'
    descTwistSetupClass = ShinTwistJointsSetup

    descChannelNameMinTwist = 'ShinMinimumTwist'
    descChannelNameMaxTwist = 'ShinMaximumTwist'
    desc1JointMinMaxTwist = [0.0, 1.0]
    desc2JointMinMaxTwist = [0.0, 0.5]

    descTooltipMsgTableKey = 'legShinJoints'


class PropKneeHolderJoint(PropHolderJoint):

    descIdentifier = 'knee'
    descUsername = 'holdKnee'
    descHolderJointPieceIdentifier = 'knee'

    descHolderBindLocatorIdentifier = 'kneebloc'
    descHolderJointInfluenceIdentifier = 'kneeinf'
    descLowerDriverBindLocatorIdentifier = 'shinbindloc'

    descTooltipMsgTableKey = 'legKneeHolder'


class PropHipHolderJoint(PropHolderJoint):

    descIdentifier = 'hip'
    descUsername = 'holdHip'
    descHolderJointPieceIdentifier = 'hip'

    descHolderBindLocatorIdentifier = 'hipbloc'
    descHolderJointInfluenceIdentifier = 'hipinf'
    descLowerDriverBindLocatorIdentifier = 'thighbindloc'

    descTooltipMsgTableKey = 'legHipHolder'


class PropAnkleHolderJoint(PropHolderJoint):

    descIdentifier = 'ankle'
    descUsername = 'holdAnkle'
    descHolderJointPieceIdentifier = 'ankle'

    descHolderBindLocatorIdentifier = 'anklebloc'
    descHolderJointInfluenceIdentifier = 'ankleinf'
    descLowerDriverBindLocatorIdentifier = 'footbindloc'

    descUpperDriverPieceIdentifier = ShinTwistJointsSetup.descTwistSetupPieceIdentifier
    descUpperDriverOutputChannelName = 'ShinFootTwistedWRotMtx'
    descUpperDriverInputChannelName = 'UpperDriverWRotMtx'

    descTooltipMsgTableKey = 'legAnkleHolder'


class PropEnableXZStretchingController(PropEnableControllerAndTransformSet):

    descIdentifier = 'pstretch'
    descUsername = 'enableStretch'
    descRefreshContext = True
    descTooltipMsgTableKey = 'enableStretch'
    controllerIdent = 'ctrllegstretch'
    channelSet = [modox.c.TransformChannels.ScaleX,
                  modox.c.TransformChannels.ScaleZ]


# ------- Leg module

class BipedLegVer2(rs.base_FeaturedModule):

    descIdentifier = 'std.bipedLeg.v2'
    descUsername = 'Biped Leg'
    descFeatures = [ThighJointsProperty,
                    ShinJointsProperty,
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

