

import lx
import modo
import modox

from . import preset
from . import const as c
from .item_features.controller import ControllerItemFeature
from .controller_op import ControllerOperator
from .preset_thumb import PresetThumbnail
from .pose import Pose
from .core import service
from .util import run


class ActionPresetThumbnail(PresetThumbnail):
    
    descIdentifier = 'action'
    descUsername = 'Action'
    descWindowLayout = 'rs_SaveActionThumb_Layout'
    descWindowTitle = 'Save Action'
    descButtonName = 'Save Action'


class PosePresetThumbnail(PresetThumbnail):
    
    descIdentifier = 'pose'
    descUsername = 'Pose'
    descWindowLayout = 'rs_SavePoseThumb_Layout'
    descWindowTitle = 'Save Pose'
    descButtonName = 'Save Pose'


class MotionPreset(preset.Preset):
    """ A base class for poses and actions presets.
    """
    
    descContext = c.Context.ANIMATE
    descSupportsDestinationItem = True
    descDestinationRig = preset.Preset.DestinationRig.SELECTED

    @property
    def channels(self):
        """ Needs to return all channels that should be contained within the preset.
        """        
        controllersElementSet = self.rig[c.ElementSetType.CONTROLLERS]
        ctrls = controllersElementSet.elements
        channels = []
        for ctrlModoItem in ctrls:
            try:
                ctrl = ControllerItemFeature(ctrlModoItem)
            except TypeError:
                continue
            if ctrl.isStoredInPose:
                channels.extend(ctrl.animatedChannels)
        return channels


class ActionPreset(MotionPreset):
    
    descIdentifier = 'action'
    descUsername = 'Action'
    descValuesType = preset.Preset.ValuesType.ENVELOPE
    descPresetDescription = 'ACS Action'
    descThumbnailClass = ActionPresetThumbnail

    def preLoad(self, settings):
        name = self.name
        if not name:
            name = 'New Action'
        actor = self.rig.actor
        actionClip = actor.addAction(name)
        actionClip.active = True
        run('group.current {%s} actr' % actor.id)


class PosePreset(MotionPreset):
    
    descIdentifier = 'pose'
    descUsername = 'Pose'
    descValuesType = preset.Preset.ValuesType.STATIC
    descPresetDescription = 'ACS Pose'
    descThumbnailClass = PosePresetThumbnail
    descSelectionSensitive = True
    descDefaultButtonName = "Save Pose As..."
    descDefaultIcon = "rs.preset.savePose"

    _SIDE_SETTING = 'side'
    _WORLD_SPACE_CTRLS_SETTING = 'wspace'

    @property
    def channels(self):
        pose = Pose(self.rig)
        return pose.currentChannels

    @property
    def loadChannels(self):
        """
        When saving preset pose is controller selection sensitive but on load we want to get all the channels always.
        """
        pose = Pose(self.rig)
        return pose.allChannels

    @property
    def icon(self):
        pose = Pose(self.rig)
        if pose.currentScopeIsSelection:
            return 'rs.preset.savePoseSelected'
        return 'rs.preset.savePose'

    @property
    def buttonName(self):
        pose = Pose(self.rig)
        if pose.currentScopeIsSelection:
            return "Save Selection Pose As..."
        return "Save Pose As..."

    @property
    def descSettings(self):
        """
        Scan pose contents to see if the preset is a one sided one.

        If it is we're going to store a setting for that.
        """
        pose = Pose(self.rig)
        ctrls = pose.currentControllers

        settings = {}
        self._addSidedSetting(ctrls, settings)
        self._addWorldSpaceControllersSetting(ctrls, settings)

        return settings

    def preLoad(self, settings):
        dropAction = service.userValue.get(c.UserValue.PRESET_DROP_ACTION_CODE)
        if (dropAction == c.DropActionCode.MIRRORPOSE or
            self._checkIfSidedAndDroppedOnTheOtherSide(settings)):
            self.contentItem.mirror()
            self._mirrorCharacterSpaceControllerIdentifiers(settings)

        if self.destinationItem is not None:
            self._checkAndApplyWorldOffset(settings)

    # -------- Private methods

    def _addSidedSetting(self, ctrls, settings):
        sideCounter = {c.Side.CENTER: 0,
                       c.Side.RIGHT: 0,
                       c.Side.LEFT: 0}

        sidedPose = True

        for ctrl in ctrls:
            sideCounter[ctrl.item.side] = 1

            if sideCounter[c.Side.CENTER] > 0:
                sidedPose = False
                break

            if sideCounter[c.Side.RIGHT] > 0 and sideCounter[c.Side.LEFT] > 0:
                sidedPose = False
                break

        if sidedPose:
            if sideCounter[c.Side.RIGHT] > 0:
                settings[self._SIDE_SETTING] = c.Side.RIGHT
            elif sideCounter[c.Side.LEFT] > 0:
                settings[self._SIDE_SETTING] = c.Side.LEFT

    def _addWorldSpaceControllersSetting(self, ctrls, settings):
        ctrlsList = []
        for ctrl in ctrls:
            if ControllerOperator.isControllerInCharacterSpace(ctrl):
                ctrlsList.append(ctrl)

        ctrlsIdents = [self.renderItemIdentifier(ctrl.item) for ctrl in ctrlsList]
        if len(ctrlsIdents) > 0:
            settings[self._WORLD_SPACE_CTRLS_SETTING] = ctrlsIdents

    def _checkIfSidedAndDroppedOnTheOtherSide(self, settings):
        try:
            presetSide = settings[self._SIDE_SETTING]
        except KeyError:
            return False

        if self.destinationItem is None:
            return False

        destinationSide = self.destinationItem.side
        if destinationSide == c.Side.CENTER or destinationSide == presetSide:
            return False

        return True

    def _checkAndApplyWorldOffset(self, settings):
        try:
            ctrl = ControllerItemFeature(self.destinationItem)
        except TypeError:
            return

        if not ControllerOperator.isControllerInCharacterSpace(ctrl):
            return

        # We need to apply world offset
        # For some reason getting that setting brings identifiers
        # in unicode instead of str.
        # Watch out for that! Although unicode works fine for typical str purpose
        # it's not the same type so if I need to compare the identifier to str it won't work!
        try:
            wspaceCtrlIdentifiers = settings[self._WORLD_SPACE_CTRLS_SETTING]
        except KeyError:
            return

        destCtrlIdentifier = self.renderItemIdentifier(ctrl.item)
        if destCtrlIdentifier not in wspaceCtrlIdentifiers:
            return

        wpos = modox.LocatorUtils.getItemPosition(ctrl.modoItem)
        referenceWPos = modo.Vector3(wpos[0], wpos[1], wpos[2])

        contentItem = self._contentItem

        # Get world position from inside preset
        try:
            px = contentItem.getChannelValue(self.renderChannelIdentifier(ctrl.item, 'pos.X'))
            py = contentItem.getChannelValue(self.renderChannelIdentifier(ctrl.item, 'pos.Y'))
            pz = contentItem.getChannelValue(self.renderChannelIdentifier(ctrl.item, 'pos.Z'))
        except LookupError:
            return

        storedWPos = modo.Vector3(px, py, pz)
        offset = referenceWPos - storedWPos

        # Go through all the wspace controllers and modify their values in content item.
        for wposCtrlIdentifier in wspaceCtrlIdentifiers:
            xident = self.renderChannelIdentifier(wposCtrlIdentifier, 'pos.X')
            yident = self.renderChannelIdentifier(wposCtrlIdentifier, 'pos.Y')
            zident = self.renderChannelIdentifier(wposCtrlIdentifier, 'pos.Z')
            try:
                px = contentItem.getChannelValue(xident)
                py = contentItem.getChannelValue(yident)
                pz = contentItem.getChannelValue(zident)
            except LookupError:
                continue

            contentItem.setChannelValue(xident, px + offset.x)
            contentItem.setChannelValue(yident, py + offset.y)
            contentItem.setChannelValue(zident, pz + offset.z)

    def _mirrorCharacterSpaceControllerIdentifiers(self, settings):
        try:
            wspaceCtrlIdentifiers = settings[self._WORLD_SPACE_CTRLS_SETTING]
        except KeyError:
            return

        mirroredIdents = []
        for ctrlIdent in wspaceCtrlIdentifiers:
            mirroredIdents.append(self.mirrorItemIdentifier(ctrlIdent))

        settings[self._WORLD_SPACE_CTRLS_SETTING] = mirroredIdents