

import lx
import modo
import modox

import rs
from .base_twist import *
from .common import PropHolderJoint
from .common import PropEnableControllerAndTransformSet


FINGERS_SUBMODULE_ID = 'barmFinger'


# -------- Upper arm twist setup

class UpperArmTwistJointPiece(base_TwistJointPiece):

    descIdentifier = 'uparmtwistjoint'
    descSerialNameToken = ['ArmTwist']  # This is the string to replace when renaming serial pieces.
    descKeyBindJoint = 'armbindloc'
    descRelatedRegion = 'Arm'


class UpperArmTwistJointsSetup(base_TwistJointsSetup):

    descSerialPieceClass = UpperArmTwistJointPiece
    descTwistSetupPieceIdentifier = 'armtwistsetup'
    descKeyParentJoint = 'armbindloc'
    descKeyChildJoint = 'farmbindloc'


class UpperArmJoints(base_TwistJointsProperty):
    """
    Allows for setting a number of joints in the upper arm.
    """

    descIdentifier = 'armjoints'
    descUsername = 'armJoints'
    descChannelNameJointCount = 'UpperArmJoints'
    descTwistSetupClass = UpperArmTwistJointsSetup

    descChannelNameMinTwist = 'ArmMinimumTwist'
    descChannelNameMaxTwist = 'ArmMaximumTwist'

    descTooltipMsgTableKey = 'armArmJoints'


# -------- Forearm twist setup

class ForearmTwistJointPiece(base_TwistJointPiece):

    descIdentifier = 'farmtwistjoint'
    descSerialNameToken = ['ForearmTwist']  # This is the string to replace when renaming serial pieces.
    descKeyBindJoint = 'farmbindloc'
    descRelatedRegion = 'Forearm'


class ForearmTwistJointsSetup(base_TwistJointsSetup):

    descSerialPieceClass = ForearmTwistJointPiece
    descTwistSetupPieceIdentifier = 'farmtwistsetup'
    descKeyParentJoint = 'farmbindloc'
    descKeyChildJoint = 'handbindloc'


class ForearmJoints(base_TwistJointsProperty):
    """
    Allows for setting a number of joints in the forearm.
    """

    descIdentifier = 'farmjoints'
    descUsername = 'farmJoints'
    descChannelNameJointCount = 'ForearmJoints'
    descTwistSetupClass = ForearmTwistJointsSetup

    descChannelNameMinTwist = 'ForearmMinimumTwist'
    descChannelNameMaxTwist = 'ForearmMaximumTwist'

    descTooltipMsgTableKey = 'armForearmJoints'


# -------- Other

class Fingers(rs.base_ModuleProperty):
    """
    Set number of fingers on the hand.
    """

    descIdentifier = "fingers"
    descUsername = "fingers"
    descValueType = lx.symbol.sTYPE_INTEGER
    descApplyGuide = False
    descRefreshContext = rs.c.Context.GUIDE
    descTooltipMsgTableKey = 'armFingers'

    _NAMES = ['Index', 'Middle', 'Ring', 'Pinky']
    _SETTING_GROUP = 'hfing'
    _SETTING_INDEX = 'ix'
    _FINGERS_Z_OFFSET = modo.Vector3(0.0, 0.0, 0.2)
    _FINGERS_X_SPACING = 0.1
    _FINGERS_SUBMODULE_ID = FINGERS_SUBMODULE_ID

    def onQuery(self):
        subModules = self.module.getSubmodulesWithIdentifier(self._FINGERS_SUBMODULE_ID)
        return len(subModules)

    def onSet(self, value):
        submodules = self.module.getSubmodulesWithIdentifier(self._FINGERS_SUBMODULE_ID)
        currentCount = len(submodules)

        if value == currentCount:
            return False

        if value > currentCount:
            # Enable silent drop to add modules in controlled way.
            # Drop actions will not be executed
            rs.service.globalState.ControlledDrop = True

            newModules = self._addFingers(value, currentCount)
            oldModules = self._getModulesSortedByIndexes(submodules)
            allModules = oldModules + newModules
            socket = self.module.sockets[0]  # Get socket in blind
            self._setupGuide(socket.modoItem, newModules, oldModules)

            # Let's apply the guide here.
            guide = rs.Guide(self.module.rigRootItem)
            guide.apply(allModules)
            # And refresh context
            rs.Scene().contexts.refreshCurrent()

            rs.service.globalState.ControlledDrop = False
        else:
            self._removeFingers(value, submodules)

        # TODO: Does return value matter here since we do not want guide applied anyway?
        return False

    # -------- Private methods

    def _addFingers(self, count, currentCount):
        """
        Adds more fingers to the hand.
        Fingers are automatically linked with the arm module.

        Parameters
        ----------
        count : int
            How many to add

        currentCount : int
            How many are already there.
        """
        moduleOp = rs.ModuleOperator(self.module.rigRootItem)
        socket = self.module.sockets[0] # Get socket in blind

        newModules = []
        side = self.module.side

        thisModuleGuide = rs.ModuleGuide(self.module)
        #thisModuleRootGuide = thisModuleGuide.rootControllerGuides[0].item # this gets guide controller feature
        thisModuleRootGuide = self.module.getKeyItem('edgdhand')

        for x in range(count - currentCount):
            newModule = moduleOp.addModuleFromPreset(rs.c.ModulePresetFilename.FK_CHAIN)
            newModules.append(newModule)
            self.module.addSubmodule(newModule, self._FINGERS_SUBMODULE_ID)

            newModuleGuide = rs.ModuleGuide(newModule)
            newRootGuide = newModuleGuide.rootControllerGuides[0].item # this gets guide controller feature

            index = x + currentCount

            try:
                name = self._NAMES[index]
            except IndexError:
                name = "Extra"

            newModule.name = name
            newModule.side = side

            plugs = newModule.plugsByNames
            plugs["Main"].connectToSocket(socket)

            # Set module index
            newModule.settings.setInGroup(self._SETTING_GROUP, self._SETTING_INDEX, index)

            # Links finger guide to arm guide
            # Note that this has to be done after module side is set
            # as linking does some checks to avoid linking left side module to right side one for example.
            g = rs.Guide(thisModuleRootGuide.rigRootItem)
            g.linkGuideTransforms(newRootGuide, thisModuleRootGuide)

        return newModules

    def _removeFingers(self, targetCount, fingerModules):
        """
        Remove fingers to get to the target count.

        Parameters
        ----------
        targetCount : int
            How many fingers should be left.

        currentCount : int
            How many fingers are there now.
        """
        modulesSorted = self._getModulesSortedByIndexes(fingerModules)
        removeCount = len(fingerModules) - targetCount
        for x in range(removeCount):
            modToRemove = modulesSorted.pop(-1)
            modToRemove.selfDelete()

    def _getModulesSortedByIndexes(self, modules):
        """
        Gets a list of modules sorted by indexes, biggest index is last on list.
        """
        d = {}
        biggestIndex = 0
        for module in modules:
            index = module.settings.getFromGroup(self._SETTING_GROUP, self._SETTING_INDEX, 0)
            if index > biggestIndex:
                biggestIndex = index
            if index in d:
                d[index].append(module)
            else:
                d[index] = [module]

        mods = []
        for x in range(biggestIndex + 1):
            try:
                mods.extend(d[x])
            except KeyError:
                continue
        return mods

    def _setupGuide(self, rootItem, modules, existingModules=[]):
        """
        Sets up guides for newly added modules.
        We do not touch existing modules, we add new ones next to
        existing module with highest index.

        Parameters
        ----------
        rootItem : modo.Item
            The item that will be root point for placing all other modules.
        """

        # We simply copy local transforms from nearest finger.
        # We assume all fingers have exactly the same parent space so that's why
        # simple copying and offsetting local values should work.

        # XSpacing is based on either 2 last fingers spacing or will be done
        # as percentage of the reference size if there is
        startPosVec = modo.Vector3()
        spacingVec = modo.Vector3()
        if len(existingModules) > 1:
            m1 = rs.ModuleGuide(existingModules[-2])
            m2 = rs.ModuleGuide(existingModules[-1])
            p1 = modox.LocatorUtils.getItemPosition(m1.rootControllerGuides[0].modoItem)
            p2 = modox.LocatorUtils.getItemPosition(m2.rootControllerGuides[0].modoItem)
            startPosVec = p2
            spacingVec = p2 - p1
        elif len(existingModules) == 1:
            m1 = rs.ModuleGuide(existingModules[0])
            s = m1.boundingBoxDiagonalLength
            spacingVec = modo.Vector3(-s * 0.2, 0.0, 0.0)
            startPosVec = modox.LocatorUtils.getItemPosition(m1.rootControllerGuides[0].modoItem)

        if existingModules:
            # start pos will be slightly shifted to last existing finger module.
            fingerGuide = rs.ModuleGuide(existingModules[-1])
            rootGuide = fingerGuide.rootControllerGuides[0]
            startPosVec = modox.LocatorUtils.getItemPosition(rootGuide.modoItem)
            startRotVec = modox.LocatorUtils.getItemRotation(rootGuide.modoItem)
            startSclVec = modox.LocatorUtils.getItemScale(rootGuide.modoItem)

            refSize = fingerGuide.boundingBoxDiagonalLength
        else:
            startPosVec = modo.Vector3(0.0, 0.0, 0.2)
            startRotVec = modo.Vector3()
            startSclVec = modo.Vector3(1.0, 1.0, 1.0)
            refSize = None

        for module in modules:
            startPosVec = startPosVec + spacingVec # needs to be adding here, not substracting!
            guide = rs.ModuleGuide(module)
            rootGuide = guide.rootControllerGuides[0].item
            modox.LocatorUtils.setItemPosition(rootGuide.modoItem, startPosVec, action=lx.symbol.s_ACTIONLAYER_EDIT)
            modox.LocatorUtils.setItemRotation(rootGuide.modoItem, startRotVec, action=lx.symbol.s_ACTIONLAYER_EDIT)
            modox.LocatorUtils.setItemScale(rootGuide.modoItem, startSclVec, action=lx.symbol.s_ACTIONLAYER_EDIT)

            if refSize is not None:
                scaleFactor = refSize / guide.boundingBoxDiagonalLength
                guide.applyScaleFactor(scaleFactor)


class Thumb(rs.base_ModuleProperty):
    """
    Whether to add thumb or not.
    """

    descIdentifier = "thumb"
    descUsername = "thumb"
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descApplyGuide = True
    descRefreshContext = True
    descTooltipMsgTableKey = 'armThumb'

    _THUMB_SUBMODULE_ID = 'barmThumb'

    def onQuery(self):
        subModules = self.module.getSubmodulesWithIdentifier(self. _THUMB_SUBMODULE_ID)
        return len(subModules) > 0

    def onSet(self, value):
        submodules = self.module.getSubmodulesWithIdentifier(self. _THUMB_SUBMODULE_ID)
        hasThumb = len(submodules) > 0

        if hasThumb and value:
            return
        if not hasThumb and not value:
            return

        if value: # Add thumb
            # Enable silent drop to add modules in controlled way.
            # Drop actions will not be executed
            rs.service.globalState.ControlledDrop = True

            newModule = self._addThumb()
            #socket = self.module.sockets[0]  # Get socket in blind

            # To set up guide properly I need to know the size of finger module (if any).
            # If there are no fingers than thumb module should be scaled to the same size
            # as the arm module.
            fingers = self.module.getSubmodulesWithIdentifier(FINGERS_SUBMODULE_ID)
            if len(fingers) > 0:
                refModule = fingers[0]
            else:
                refModule = None

            self._setupGuide(newModule, refModule)

            # Let's apply the guide here.
            guide = rs.Guide(self.module.rigRootItem)
            guide.apply(newModule)
            # And refresh context
            rs.Scene().contexts.refreshCurrent()

            rs.service.globalState.ControlledDrop = False
        else:
            self._removeThumb(submodules[0])

    # -------- Private methods

    def _addThumb(self):
        moduleOp = rs.ModuleOperator(self.module.rigRootItem)
        socket = self.module.sockets[0] # Get socket in blind

        side = self.module.side

        thisModuleGuide = rs.ModuleGuide(self.module)
        #thisModuleRootGuide = thisModuleGuide.rootControllerGuides[0].item # this gets guide controller feature
        thisModuleRootGuide = self.module.getKeyItem('edgdhand')

        newModule = moduleOp.addModuleFromPreset(rs.c.ModulePresetFilename.FK_CHAIN)
        self.module.addSubmodule(newModule, self._THUMB_SUBMODULE_ID)

        newModule.name = "Thumb"
        newModule.side = side

        plugs = newModule.plugsByNames
        plugs["Main"].connectToSocket(socket)

        newModuleGuide = rs.ModuleGuide(newModule)
        newRootGuide = newModuleGuide.rootControllerGuides[0].item # this gets guide controller feature
        rs.Guide(thisModuleRootGuide.rigRootItem).linkGuideTransforms(newRootGuide, thisModuleRootGuide)

        return newModule

    def _removeThumb(self, module):
        module.selfDelete()

    def _setupGuide(self, module, refModule):
        startPos = modo.Vector3(0.1, 0.0, 0.1)
        startRot = modo.Vector3(0.0, 0.775, 0.0) # rotate 45 degrees on Y
        startScl = modo.Vector3(1.0, 1.0, 1.0)

        guide = rs.ModuleGuide(module)
        root = guide.rootControllerGuides[0]
        modox.LocatorUtils.setItemPosition(root.modoItem, startPos, action=lx.symbol.s_ACTIONLAYER_EDIT)
        modox.LocatorUtils.setItemRotation(root.modoItem, startRot, action=lx.symbol.s_ACTIONLAYER_EDIT)
        modox.LocatorUtils.setItemScale(root.modoItem, startScl, action=lx.symbol.s_ACTIONLAYER_EDIT)

        # Resize thumb module to fit first finger.
        if refModule is not None:
            fingerGuide = rs.ModuleGuide(refModule)
            refSize = fingerGuide.boundingBoxDiagonalLength
            scaleFactor = refSize / guide.boundingBoxDiagonalLength
            guide.applyScaleFactor(scaleFactor)
        else:
            pass


# -------- Holder Joints

class PropElbowHolderJoint(PropHolderJoint):

    descIdentifier = 'elbow'
    descUsername = 'Elbow Holder Joint'
    descHolderJointPieceIdentifier = 'elbow'

    descHolderBindLocatorIdentifier = 'elbowbloc'
    descHolderJointInfluenceIdentifier = 'elbowinf'
    descLowerDriverBindLocatorIdentifier = 'farmbindloc'

    descTooltipMsgTableKey = 'armElbowHolder'


class PropArmHolderJoint(PropHolderJoint):

    descIdentifier = 'armh'
    descUsername = 'Arm Holder Joint'
    descHolderJointPieceIdentifier = 'armh'

    descHolderBindLocatorIdentifier = 'armhbloc'
    descHolderJointInfluenceIdentifier = 'armhinf'
    descLowerDriverBindLocatorIdentifier = 'armbindloc'

    descTooltipMsgTableKey = 'armArmHolder'


class PropWristHolderJoint(PropHolderJoint):

    descIdentifier = 'wrist'
    descUsername = 'Wrist Holder Joint'
    descHolderJointPieceIdentifier = 'wrist'

    descHolderBindLocatorIdentifier = 'wristbloc'
    descHolderJointInfluenceIdentifier = 'wristinf'
    descLowerDriverBindLocatorIdentifier = 'handbindloc'

    descTooltipMsgTableKey = 'armWristHolder'


class PropEnableXZStretchingController(PropEnableControllerAndTransformSet):

    descIdentifier = 'pstretch'
    descUsername = 'enableStretch'
    descRefreshContext = True
    controllerIdent = ['ctrlarmstretch', 'ctrlhandstretch']
    channelSet = [modox.c.TransformChannels.ScaleX,
                  modox.c.TransformChannels.ScaleZ]
    descTooltipMsgTableKey = 'enableStretch'


class Arm(rs.base_FeaturedModule):

    descIdentifier = 'std.arm'
    descUsername = 'Biped Arm'
    descFeatures = [Thumb, Fingers]


class ArmVer2(rs.base_FeaturedModule):

    descIdentifier = 'std.arm.v2'
    descUsername = 'Biped Arm'
    descFeatures = [UpperArmJoints, ForearmJoints,
                    modox.c.FormCommandList.DIVIDER,
                    Thumb, Fingers,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableXZStretchingController,
                    modox.c.FormCommandList.DIVIDER,
                    PropArmHolderJoint,
                    PropElbowHolderJoint,
                    PropWristHolderJoint]

    def onSwitchToFK(self, switcherFeature):
        solver = switcherFeature.ikChain.ikSolvers[0]
        scaleFactor = solver.scaleOutput[0]

        armStretchCtrl = self.module.getKeyItem('ctrlarmstretch')
        scale = modox.LocatorUtils.getItemScale(armStretchCtrl.modoItem)
        scale.z = scaleFactor
        modox.LocatorUtils.setItemScale(armStretchCtrl.modoItem, scale, time=None, key=True, action=lx.symbol.s_ACTIONLAYER_EDIT)

