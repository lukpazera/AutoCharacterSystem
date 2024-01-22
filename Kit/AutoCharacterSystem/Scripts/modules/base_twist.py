"""
This module implements base classes for twist joint setups for limbs.
"""


import lx
import modox

import rs
from rs.const import KeyItem as k


class base_TwistJointPiece(rs.base_SerialPiece):

    descIdentifier = ''
    descSerialNameToken = ''  # This is the string to replace when renaming serial pieces.
    descKeyBindJoint = ''  # Key of the parent bind locator joint and all twist joints in the setup.

    # This is custom property for setting related command region
    descRelatedRegion = ''

    # This is for parenting items between pieces and between module and pieces (in case of first and last piece).
    # Here we just parent piece twist joint bind locators to each other and the first one will go to the arm.
    @property
    def descPieceHierarchy(self):
        return {self.descKeyBindJoint: self.descKeyBindJoint}

    descDeformersHierarchy = {k.DEFORM_FOLDER: k.GENERAL_INFLUENCE}


class base_TwistJointsSetup(rs.base_SerialPiecesSetup):

    descSerialPieceClass = None  # Make sure to define serial piece class
    descTwistSetupPieceIdentifier = ''  # Identifier of the piece that implements twist setup
    descSequenceStart = 1
    descKeyParentJoint = ''  # Key of the main joint and all twist joints, same as descKeyBindJoint in TwistJointPiece above.
    descKeyChildJoint = ''  # Key of the joint that is child to the joint the twist setup is on (forearm for arm, hand for forearm, etc.)

    # Parent module items to items from last piece to close hierarchy between
    # last piece and module
    @property
    def descModuleHierarchy(self):
        """
        This needs to be implemented as property here so descKeyChildJoint is taken
        from implementing class not the base class.
        """
        return {self.descKeyParentJoint: self.descKeyChildJoint}

    def onSerialPieceAdded(self, piece, prevPiece=None, nextPiece=None):
        """
        Perform any manual operations that need to be done on a piece to integrate it with the module.
        """
        twistSetupPiece = self.module.getFirstPieceByIdentifier(self.descTwistSetupPieceIdentifier)
        modox.Assembly.autoConnectOutputsToInputs(twistSetupPiece.assemblyModoItem, piece.assemblyModoItem)

        # We need to set baked parent for twist joint to the first joint so
        # twist joints become leaves when baked.
        modBakeParentItem = self.module.getKeyItem(self.descKeyParentJoint)
        pieceTwistJoint = piece.getKeyItem(self.descKeyParentJoint)
        pieceTwistJoint.bakedParent = modBakeParentItem.modoItem

        # Set up related command region if this property is defined.
        relatedRegionName = self.descSerialPieceClass.descRelatedRegion
        if relatedRegionName:
            modClayOp = rs.RigClayModuleOperator(self.module)
            for modRegion in modClayOp.polygonRegions:
                if modRegion.name == relatedRegionName:
                    pieceTwistJoint.relatedCommandRegion = modRegion.modoItem
                    break


class base_TwistJointsProperty(rs.base_ModuleProperty):
    """
    Allows for setting a number of joints for a given section of the limb.

    Note that the main joint counts as 1 so twist joints are really added
    with property value of 2 or greater.

    Attributes
    ----------
    descKeyCtrlPanel : str
        Key of the controller item that contains the min/max twist channels (sliders).

    descChannelNameMinTwist : str
        Name of the Minimum Twist channel on the key item that has this channel added.

    descChannelNameMaxTwist : str
        Name of the Maximum Twist channel on the key item that has this channel added.

    desc1JointMinMaxTwist : [min, max]
        Minimum and maximum twist values for a chain that only has a single joint (no twist joints).

    desc2JointMinMaxTwist : [min, max]
        Minimum and maximum twist values for a chain that has 2 joints (1 twist joint).
    """

    descIdentifier = None
    descUsername = None
    descValueType = lx.symbol.sTYPE_INTEGER
    descTwistSetupClass = None  # Class implementing twist serial joints setup
    descChannelNameOffset = 'OffsetAlongJoint'  # Name of the channel on the twist joint piece to set offset along main joint on.
    descChannelNameTwistBlend = 'TwistBlendAmount'
    descChannelNameJointCount = ''  # Name of the channel on which the total joint count is stored.

    descKeyCtrlPanel = 'ctrlpanel'
    descChannelNameMinTwist = 'MinimumTwist'
    descChannelNameMaxTwist = 'MaximumTwist'
    desc1JointMinMaxTwist = [0.25, 1.0]
    desc2JointMinMaxTwist = [0.25, 0.75]

    def onQuery(self):
        return int(self.module.rigSubassembly.modoItem.channel(self.descChannelNameJointCount).get(0.0, lx.symbol.s_ACTIONLAYER_SETUP))

    def onSet(self, value):
        currentVal = self.onQuery()

        if value < 1:
            value = 1

        if value > 16:
            value = 16

        if value == currentVal:
            return False

        # 1 arm joint is always there.
        twistJointsCount = value - 1

        pieceOp = rs.PieceOperator(self.module)
        pieceOp.installSerialPieces(twistJointsCount, self.descTwistSetupClass)

        serialPieceId = self.descTwistSetupClass.descSerialPieceClass.descIdentifier
        pieces = self.module.getPiecesByIdentifierOrdered(serialPieceId)

        self._setTwistJointsSettings(pieces)
        self._setMinMaxTwistSettings(currentVal, value)

        rigAssm = self.module.rigSubassembly.modoItem
        rigAssm.channel(self.descChannelNameJointCount).set(value, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
        return True

    # -------- Private methods

    def _setTwistJointsSettings(self, pieces):
        """
        Sets all the twist settings that are dependent on number of joints in the chain.

         - each twist joint needs to have its offset along arm joint set after new pieces
        were added or removed.
         - each twist joint needs to have its blend amount set.
         - min and max twist default settings are different for chains of 1, 2 and more than 2 joints.
        """
        if len(pieces) == 0:
            return

        jointCount = len(pieces) + 1
        offsetStep = 1.0 / float(jointCount)
        offset = offsetStep

        for piece in pieces:
            piece.assemblyModoItem.channel(self.descChannelNameOffset).set(offset,
                                                                           0.0, key=False,
                                                                           action=lx.symbol.s_ACTIONLAYER_SETUP)
            offset += offsetStep

        # Twist blending setting
        twistBlendStep = 1.0 / len(pieces)
        twistBlendAmount = 0
        for piece in pieces:
            twistBlendAmount += twistBlendStep
            piece.assemblyModoItem.channel(self.descChannelNameTwistBlend).set(twistBlendAmount,
                                                                               0.0, key=False,
                                                                               action=lx.symbol.s_ACTIONLAYER_SETUP)

    def _setMinMaxTwistSettings(self, previousJointCount, newJointCount):
        # Set min/max twist values
        if newJointCount == 1:
            # single joint twist defaults
            self._setMinMaxTwistChannels(self.desc1JointMinMaxTwist[0], self.desc1JointMinMaxTwist[1])
        elif newJointCount == 2:
            # two twist joints defaults
            self._setMinMaxTwistChannels(self.desc2JointMinMaxTwist[0], self.desc2JointMinMaxTwist[1])
        else:
            # We change min max twist settings for chains longer than 2 joints
            # only if we went from less than 3 joints to 3 joints or more.
            # We do not change min/max twist settings otherwise.
            if previousJointCount < 3:
                self._setMinMaxTwistChannels(0.0, 1.0)

    def _setMinMaxTwistChannels(self, minValue, maxValue):
        panelCtrl = self.module.getKeyItem(self.descKeyCtrlPanel)
        minTwist = panelCtrl.modoItem.channel(self.descChannelNameMinTwist)
        maxTwist = panelCtrl.modoItem.channel(self.descChannelNameMaxTwist)
        minTwist.set(minValue, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
        maxTwist.set(maxValue, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)


