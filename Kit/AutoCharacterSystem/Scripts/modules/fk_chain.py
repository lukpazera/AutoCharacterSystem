
import math

import lx
import modo
import modox

import rs
from rs.const import KeyItem as k
from .common import PropEnableTransformSet
from .common import PropEnableControllerAndTransformSet
from .common import PropRotationOrder
from .common import PropEnableSpaceSwitchingTemplate


class SegmentPiece(rs.base_SerialPiece):

    SOCKET_IDENTIFIER = 'segSocket'

    descIdentifier = 'segment'
    descSerialNameToken = ['Seg', 'Segment']
    descPieceHierarchy = {k.BIND_LOCATOR: k.BIND_LOCATOR,
                          k.CONTROLLER: k.CONTROLLER,
                          k.REFERENCE_GUIDE: k.REFERENCE_GUIDE}
    descModuleHierarchy = {k.CONTROLLER_GUIDE: k.CONTROLLER_GUIDE}
    descDeformersHierarchy = {k.DEFORM_FOLDER: k.GENERAL_INFLUENCE}
    descChainGuide = k.CONTROLLER_GUIDE


class SegmentsSetup(rs.base_SerialPiecesSetup):

    KEY_TIP_BIND_LOCATOR = 'tipbindloc'
    KEY_TIP_CONTROLLER_CHAIN = 'tiploc'
    KEY_TIP_REFERENCE_GUIDE = 'tiprefgd'

    descSerialPieceClass = SegmentPiece
    descSequenceStart = 2
    descCountChannel = 'Segments'
    descModuleHierarchy = {k.CONTROLLER: KEY_TIP_CONTROLLER_CHAIN,
                           k.REFERENCE_GUIDE: KEY_TIP_REFERENCE_GUIDE,
                           k.BIND_LOCATOR: KEY_TIP_BIND_LOCATOR}
    # This is for setting up aligning guide as a chain
    descFitGuide = True
    descGuideItemLinks = True
    descGuideChainStart = k.CONTROLLER_GUIDE
    descGuideChainEnd = k.TIP_CONTROLLER_GUIDE


class PropSegments(rs.base_ModuleProperty):

    # -------- Constants

    _CHAN_SEGMENTS = 'Segments'

    # -------- Property interface

    descIdentifier = 'psegs'
    descUsername = 'jcSegments'
    descValueType = lx.symbol.sTYPE_INTEGER
    descApplyGuide = True
    descRefreshContext = True

    def onQuery(self):
        """ Queries module for current number of segments.

        Returns
        -------
        int
        """
        # This returns long here for some reason so we have to cast to int.
        return int(self.module.getFirstSubassemblyOfItemType(rs.c.RigItemType.MODULE_RIG_ASSM).modoItem.channel(self._CHAN_SEGMENTS).get(0.0, lx.symbol.s_ACTIONLAYER_EDIT))

    def onSet(self, value):
        """ Sets new number of segments for this module.

        Parameters
        ----------
        int
        """
        currentVal = self.onQuery()

        if value == currentVal:
            return False
        if value < 1:
            value = 1

        # 1 segment is always there so need to substract it from number of serial pieces to install
        value -= 1

        pieceOp = rs.PieceOperator(self.module)
        pieceOp.installSerialPieces(value, SegmentsSetup)
        return True


class PropEnableTranslation(PropEnableTransformSet):
    """
    This property makes it possible to translate entire chain.
    """

    descIdentifier = 'pmove'
    descUsername = 'enableTranslation'
    channelSet = modox.c.TransformChannels.PositionAll
    descTooltipMsgTableKey = 'jntChainEnableTranslation'

class PropEnableStretching(PropEnableControllerAndTransformSet):

    descIdentifier = 'pstretch'
    descUsername = 'enableStretch'
    channelSet = modox.c.TransformChannels.ScaleAll
    controllerIdent = 'ctrlstretch'
    descTooltipMsgTableKey = 'enableStretch'

class PropEnableSpaceSwitching(PropEnableSpaceSwitchingTemplate):

    descDynaSpaceControllers = 'ctrl'
    descDynaSpaceControllerRefGuides = 'refgd'
    descTooltipMsgTableKey = 'jntChainEnableSpaceSwitch'

    def onEnabled(self):
        translation = PropEnableTranslation(self.module)
        translation.onSet(True)


class CmdFlipDirection(rs.base_ModuleCommand):

    descIdentifier = 'cmdflipdir'
    descUsername = 'jcFlipGuideDir'
    descTooltipMsgTableKey = 'jntChainFlipGuideDir'

    def run(self, arguments):
        modKeyItems = self.module.getKeyItems()
        guideItem = modKeyItems[k.CONTROLLER_GUIDE] # picks root controller guide
        loc = modo.LocatorSuperType(guideItem.modoItem.internalItem)
        rot = loc.rotation.y.get(0.0, lx.symbol.s_ACTIONLAYER_SETUP)
        if rot > 0.0:
            loc.rotation.y.set(0.0, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
        else:
            loc.rotation.y.set(math.radians(180.0), 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
        rs.Scene().context = rs.c.Context.GUIDE


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


class FKChainModule(rs.base_FeaturedModule):

    descIdentifier = 'std.fkChain'
    descUsername = 'Joint Chain'
    descFeatures = [PropSegments,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableTranslation,
                    PropEnableStretching,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableSpaceSwitching,
                    modox.c.FormCommandList.DIVIDER,
                    PropRotationOrderXDominant,
                    PropRotationOrderYDominant,
                    modox.c.FormCommandList.DIVIDER,
                    CmdFlipDirection]
