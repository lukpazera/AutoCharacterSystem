
import math

import lx
import modo
import modox

import rs
from rs.const import KeyItem as k
from .common import PropEnableTransformSet
from .common import PropEnableControllerAndTransformSet

KEY_HIERARCHY_PARENT = 'hrchp'
KEY_HIERARCHY_CHILD = 'hrchc'

KEY_VERTEBRA1_CONTROLLER_GUIDE = 'v1ctrlgd'
KEY_TWEAK_CONTROLLER = 'tweakCtrl'
KEY_UPPER_CONTROLLER = 'ctrlup'
KEY_LOWER_CONTROLLER = 'ctrllow'
KEY_UPPER_STRETCH_CONTROLLER = 'ctrlupstretch'
KEY_LOWER_STRETCH_CONTROLLER = 'ctrllowstretch'
KEY_VERTEBRA1_TWEAK_CONTROLLER = 'v1TweakCtrl'
KEY_CHEST_TWEAK_CONTROLLER = 'chestTweakCtrl'


class HorizontalVariant(rs.base_ModuleVariant):

    descIdentifier = 'horiz'
    descUsername = 'Horizontal'
    descName = 'Spine'
    descFilename = 'Spine Horiz'
    descDefaultThumbnailName = 'ModuleTorsoHorizontal'
    descApplyGuide = True

    def onApply(self):
        # To apply horizontal variant we really only need to clear rotation on a main spine guide.
        rootGuide = self.module.getKeyItem(rs.c.KeyItem.ROOT_CONTROLLER_GUIDE)

        rootGuideRotVec = modox.LocatorUtils.getItemRotation(rootGuide.modoItem, 0.0, lx.symbol.s_ACTIONLAYER_EDIT)
        rootGuideRotVec.x = 0.0
        modox.LocatorUtils.setItemRotation(rootGuide.modoItem, rootGuideRotVec, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_EDIT)
        return True


class VertebraPiece(rs.base_SerialPiece):

    descIdentifier = 'vertebra'
    descSerialNameToken = ['Vertebra']
    descPieceHierarchy = {k.BIND_LOCATOR: k.BIND_LOCATOR,
                          KEY_HIERARCHY_PARENT: KEY_HIERARCHY_CHILD,
                          k.TIP_REFERENCE_GUIDE: k.REFERENCE_GUIDE}

    # Controller guides go under root controller guide.
    descModuleHierarchy = {KEY_VERTEBRA1_CONTROLLER_GUIDE: k.CONTROLLER_GUIDE,
                           k.GUIDE_FOLDER: k.GUIDE_FOLDER,
                           k.RIG_FOLDER: k.RIG_FOLDER}
    descDeformersHierarchy = {k.DEFORM_FOLDER: k.GENERAL_INFLUENCE}
    descChainGuide = k.CONTROLLER_GUIDE # This is guide for setting up aligned chain and guide draw links


class VertebraeSetup(rs.base_SerialPiecesSetup):

    KEY_TIP_BIND_LOCATOR = 'tipbindloc'
    KEY_TIP_CONTROLLER_CHAIN = 'tiploc'
    KEY_TIP_REFERENCE_GUIDE = 'tiprefgd'
    KEY_CHEST_CONTROLLER_GUIDE = 'chestctrlgd'
    KEY_CHEST_BIND_LOCATOR = 'chestbloc'
    KEY_CHEST_REFERENCE_GUIDE = 'chestrefgd'

    KEY_PIECE_VERTEBRA_DEFORM = 'vertdfrm'
    KEY_PIECE_VERTEBRA_UP_DEFORM = 'vertdfrmup'

    KEY_MODULE_UP_ITEM_INFLUENCE = 'upiteminf'
    KEY_MODULE_LOW_ITEM_INFLUENCE = 'lowiteminf'

    descSerialPieceClass = VertebraPiece
    descSequenceStart = 2
    descCountChannel = None
    descModuleHierarchy = {k.BIND_LOCATOR: KEY_CHEST_BIND_LOCATOR,
                           KEY_TIP_REFERENCE_GUIDE: KEY_CHEST_REFERENCE_GUIDE,
                           KEY_HIERARCHY_PARENT: KEY_HIERARCHY_CHILD}

    # This is for setting up aligning guide as a chain
    descFitGuide = True
    descGuideItemLinks = True
    descGuideChainStart = KEY_VERTEBRA1_CONTROLLER_GUIDE
    descGuideChainEnd = KEY_CHEST_CONTROLLER_GUIDE

    def onSerialPieceAdded(self, piece, prevPiece=None, nextPiece=None):
        """
        Perform any manual operations that need to be done on a piece to integrate it with the module.
        """

        # Connect locators that need to be affected by item influences to these influences.
        item1 = piece.getKeyItem(self.KEY_PIECE_VERTEBRA_DEFORM).modoItem
        item2 = piece.getKeyItem(self.KEY_PIECE_VERTEBRA_UP_DEFORM).modoItem

        upItemInfluence = modox.Deformer(self.module.getKeyItem(self.KEY_MODULE_UP_ITEM_INFLUENCE).modoItem)
        upItemInfluence.meshes = [item1, item2]

        lowItemInfluence = modox.Deformer(self.module.getKeyItem(self.KEY_MODULE_LOW_ITEM_INFLUENCE).modoItem)
        lowItemInfluence.meshes = [item1, item2]


class PropVertebrae(rs.base_ModuleProperty):

    # -------- Constants

    _CHAN_VERTEBRAE = 'Vertebrae'

    # -------- Property interface

    descIdentifier = 'verts'
    descUsername = 'vertebrae'
    descValueType = lx.symbol.sTYPE_INTEGER
    descApplyGuide = True
    descRefreshContext = True
    descTooltipMsgTableKey = 'spnVertebrae'

    def onQuery(self):
        """ Queries module for current number of segments.

        Returns
        -------
        int
        """
        # This returns long here for some reason so we have to cast to int.
        return int(self.module.getFirstSubassemblyOfItemType(rs.c.RigItemType.MODULE_RIG_ASSM).modoItem.channel(self._CHAN_VERTEBRAE).get(0.0, lx.symbol.s_ACTIONLAYER_SETUP))

    def onSet(self, value):
        """ Sets new number of segments for this module.

        Parameters
        ----------
        int
        """
        currentVal = self.onQuery()

        if value == currentVal:
            return False
        # 2 vertebrae are already in the module and minimum 1 piece is required
        # so this setup cannot have less then 3 vertebrae.
        if value < 3:
            value = 3

        # 2 segments are always there so need to substract it from number of serial pieces to install
        serialPiecesCount = value - 2

        pieceOp = rs.PieceOperator(self.module)
        pieceOp.installSerialPieces(serialPiecesCount, VertebraeSetup)
        # Store the setting manually
        rigAssm = self.module.getFirstSubassemblyOfItemType(rs.c.RigItemType.MODULE_RIG_ASSM).modoItem
        rigAssm.channel(self._CHAN_VERTEBRAE).set(value, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
        return True


class PropEnableStretching(PropEnableControllerAndTransformSet):

    descIdentifier = 'pstretch'
    descUsername = 'spineStretch'
    channelSet = modox.c.TransformChannels.ScaleAll
    descTooltipMsgTableKey = 'spnEnableStretch'
    controllerIdent = [KEY_UPPER_STRETCH_CONTROLLER, KEY_LOWER_STRETCH_CONTROLLER]


class PropEnableTweakTransformSet(PropEnableTransformSet):

    @property
    def items(self):
        items = []
        items.append(self.module.getKeyItem(KEY_VERTEBRA1_TWEAK_CONTROLLER))
        vertebraPieces = self.module.getPiecesByIdentifier(VertebraPiece.descIdentifier).values()
        for piece in vertebraPieces:
            items.append(piece.getKeyItem(KEY_TWEAK_CONTROLLER))
        return items


class PropEnableTweakTranslation(PropEnableTweakTransformSet):

    descIdentifier = 'ptwmove'
    descUsername = 'spineTweakPos'
    channelSet = modox.c.TransformChannels.PositionAll
    descTooltipMsgTableKey = 'spnEnableTweakPos'


class PropEnableTweakRotation(PropEnableTweakTransformSet):

    descIdentifier = 'ptwrot'
    descUsername = 'spineTweakRot'
    channelSet = modox.c.TransformChannels.RotationAll
    descTooltipMsgTableKey = 'spnEnableTweakRot'


class PropEnableTweakScale(PropEnableTweakTransformSet):

    descIdentifier = 'ptwscl'
    descUsername = 'spineTweakScl'
    channelSet = [modox.c.TransformChannels.ScaleX, modox.c.TransformChannels.ScaleY]
    descTooltipMsgTableKey = 'spnEnableTweakScl'


class SpineModule(rs.base_FeaturedModule):

    descIdentifier = 'std.spine'
    descUsername = 'Spine'
    descFeatures = [PropVertebrae,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableStretching,
                    PropEnableTweakTranslation,
                    PropEnableTweakRotation,
                    PropEnableTweakScale
                    ]
    descVariants = [HorizontalVariant]
