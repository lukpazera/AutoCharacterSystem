

import lx
import modo
import modox

import rs
from rs.const import KeyItem as k
from .common import PropEnableJointDeformation
from .common import PropEnableControllerAndTransformSet


class RigidJointVariant(rs.base_ModuleVariant):
    """
    NOTE: NOT USED ANYMORE AS MAKING RIGID VERSION OF THE JOINT
    IS A TOGGLEABLE PROPERTY NOW

    The rigid joint variant doesn't have:
    - deformer and deform folder
    - bind locator tip
    - aim at tip locator
    - different look to the bind locator
    """
    descIdentifier = 'ctrl'
    descUsername = 'Aim At Rigid Joint'
    descName = 'AimAtRigidJoint'
    descFilename = 'Joint Aim At Rigid'
    descDefaultThumbnailName = 'ModuleAimAtRigidJoint'
    descApplyGuide = False
    descRefreshContext = True

    _KEY_BIND_LOCATOR = 'blocBase'
    _KEY_TIP_BIND_LOCATOR = 'blocTip'
    _KEY_TIP_LOCATOR = 'locTip'

    def onApply(self):
        bloc = self.module.getKeyItem(self._KEY_TIP_BIND_LOCATOR)
        rs.run('!!item.delete child:0 item:{%s}' % bloc.modoItem.id)
        loc = self.module.getKeyItem(self._KEY_TIP_LOCATOR)
        rs.run('!!item.delete child:0 item:{%s}' % loc.modoItem.id)
        dfrmFolder = self.module.getKeyItem(rs.c.KeyItem.DEFORM_FOLDER)
        rs.run('!!item.delete child:1 item:{%s}' % dfrmFolder.modoItem.id)

        blocBase = self.module.getKeyItem(self._KEY_BIND_LOCATOR)
        ident = blocBase.modoItem.id
        rs.run('!item.channel locator$link none item:{%s}' % ident)
        rs.run('!item.linkShape rem item:{%s}' % ident)

        rs.run('!item.channel locator$isShape box item:{%s}' % ident)
        rs.run('!item.channel locator$isAlign false item:{%s}' % ident)
        rs.run('!item.channel locator$isOffset.Z 0.03 item:{%s}' % ident)
        rs.run('!item.channel locator$isSize.X 0.03 item:{%s}' % ident)
        rs.run('!item.channel locator$isSize.Y 0.03 item:{%s}' % ident)
        rs.run('!item.channel locator$isSize.Z 0.06 item:{%s}' % ident)

        return True


class PropEnableSpaceSwitching(rs.base_ModuleProperty):
    """
    Enables/disables space switching by changing arrangement of the rig controller and its properties.
    """

    descIdentifier = 'pspaces'
    descUsername = 'Enable Space Switching'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descApplyGuide = True
    descRefreshContext = True
    descTooltipMsgTableKey = 'jntAimEnableSpaceSwitch'

    _KEY_TARGET_CONTROLLER = 'ctrlTarget'
    _KEY_PLUG_RIG_SPACE = 'plugRigSpace'
    _KEY_PLUG_MAIN = 'plugMain'
    _KEY_REF_GUIDE_TARGET_CONTROLLER = 'refgdTargetCtrl'
    _KEY_REF_GUIDE_PLUG_MAIN = 'refgdPlugMain'

    def onQuery(self):
        ctrlItem = self.module.getKeyItem(self._KEY_TARGET_CONTROLLER)
        parent = ctrlItem.modoItem.parent
        parentRigItem = rs.Item.getFromOther(parent)
        return parentRigItem.identifier == self._KEY_PLUG_RIG_SPACE

    def onSet(self, state):
        currentState = self.onQuery()
        if state == currentState:
            return

        ctrlItem = self.module.getKeyItem(self._KEY_TARGET_CONTROLLER)
        ctrlModoItem = ctrlItem.modoItem
        plugRigSpace = self.module.getKeyItem(self._KEY_PLUG_RIG_SPACE)
        plugMain = self.module.getKeyItem(self._KEY_PLUG_MAIN)
        ctrlRefGuide = self.module.getKeyItem(self._KEY_REF_GUIDE_TARGET_CONTROLLER)

        # Changing set involves:
        # - parenting controller to different plug
        # - reparenting controller ref guide to reflect change in hierarchy above
        # - changing controller's animation space between fixed/dynamic.
        if state:
            guideFolder = self.module.getKeyItem(rs.c.KeyItem.GUIDE_FOLDER)
            ctrlModoItem.setParent(plugRigSpace.modoItem, 0)
            ctrlRefGuide.modoItem.setParent(guideFolder.modoItem, -1)
            rs.run('rs.controller.animSpace space:dynamic item:{%s}' % ctrlModoItem.id)
        else:
            mainPlugRefGuide = self.module.getKeyItem(self._KEY_REF_GUIDE_PLUG_MAIN)
            ctrlModoItem.setParent(plugMain.modoItem, 0)
            ctrlRefGuide.modoItem.setParent(mainPlugRefGuide.modoItem)
            rs.run('rs.controller.animSpace space:fixed item:{%s}' % ctrlModoItem.id)
        return True


class PropEnableDeformation(PropEnableJointDeformation):
    """
    Adds/removes deformation setup.
    """

    descAimAtJointType = True
    descTooltipMsgTableKey = 'enableDfrm'

    def onDisabled(self):
        # Need to hide the tip guide so it's there but not editable.
        tipCtrlGuide = self.module.getKeyItem(rs.c.KeyItem.TIP_CONTROLLER_GUIDE)
        tipCtrlGuide.hidden = True

        # Also, the tip guide needs to receive new default rest position.
        modox.LocatorUtils.setItemPosition(tipCtrlGuide.modoItem, modo.Vector3(0.0, 0.0, 0.2))

        # We need to disable the link between main and tip controller guides.
        mainCtrlGuide = self.module.getKeyItem(rs.c.KeyItem.CONTROLLER_GUIDE)
        rs.ItemLinkFeature(mainCtrlGuide).enable = False

        # Change the way bind locator is drawn.
        blocBase = self.module.getKeyItem(rs.c.KeyItem.BIND_LOCATOR)
        ident = blocBase.modoItem.id
        rs.run('!item.channel locator$link none item:{%s}' % ident)

        rs.run('!item.channel locator$isShape box item:{%s}' % ident)
        rs.run('!item.channel locator$isAlign false item:{%s}' % ident)

    def onEnabled(self, piece):
        # Set the reference guide for tip blended locator.
        tipRefGuide = self.module.getKeyItem(rs.c.KeyItem.TIP_REFERENCE_GUIDE)
        tipJoint = piece.getKeyItem('tipjoint')
        rs.GuideItemFeature(tipJoint).guide = tipRefGuide

        blocBase = self.module.getKeyItem(rs.c.KeyItem.BIND_LOCATOR)
        ident = blocBase.modoItem.id
        rs.run('!item.channel locator$link custom item:{%s}' % ident)
        rs.run('!item.channel locator$isShape circle item:{%s}' % ident)

        # Re-enable link between main guide and tip.
        mainCtrlGuide = self.module.getKeyItem(rs.c.KeyItem.CONTROLLER_GUIDE)
        rs.ItemLinkFeature(mainCtrlGuide).enable = True


class PropEnableStretching(PropEnableControllerAndTransformSet):

    descIdentifier = 'pstretch'
    descUsername = 'enableStretch'
    descRefreshContext = True
    controllerIdent = 'ctrlstretch'
    channelSet = modox.c.TransformChannels.ScaleAll
    descTooltipMsgTableKey = 'enableStretch'


class PropEnableBankController(PropEnableControllerAndTransformSet):

    descIdentifier = 'pbank'
    descUsername = 'enableBank'
    descRefreshContext = True
    controllerIdent = 'ctrlextra'
    channelSet = [modox.c.TransformChannels.RotationZ]
    descTooltipMsgTableKey = 'jntAimEnableBank'


class PropEnableUpController(PropEnableControllerAndTransformSet):

    descIdentifier = 'pup'
    descUsername = 'enableUp'
    descRefreshContext = True
    controllerIdent = 'ctrlup'
    channelSet = modox.c.TransformChannels.PositionAll
    descTooltipMsgTableKey = 'jntAimEnableUp'


class AimAtJointModule(rs.base_FeaturedModule):

    descIdentifier = 'std.aimAtJoint'
    descUsername = 'Aim At Joint'
    descFeatures = [PropEnableDeformation,
                    PropEnableStretching,
                    PropEnableSpaceSwitching,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableUpController, PropEnableBankController]
    descVariants = []
