

import lx
import modo
import modox

from .core import service
from .rig import Rig
from .item_features.controller import ControllerItemFeature
from . import const as c
from .util_chan import ChannelIdentifier
from .log import log
from .item import Item


class Pose(object):
    """
    This object represents an animation pose.
    """

    _BUFFER_ID = 'posebuf'

    @property
    def currentScopeIsSelection(self):
        """
        Tests whether current scope for the pose is selection.

        The scope is selection when some controllers belonging to a rig the pose is initialized with
        are selected in the scene.

        Returns
        -------
        bool
        """
        itemSelection = modox.ItemSelection()
        selectionSize = itemSelection.size
        if selectionSize == 0:
            return False

        searchCount = min(selectionSize, 16)  # Don't test selection beyond first 16 items.
        return self._isAnyControllerSelected(searchCount)

    @property
    def allControllers(self):
        """
        Gets all controllers that are included in the pose.

        Returns
        -------
        [ControllerItemFeature]
        """
        return self._getAllControllers()

    def getKeyframedControllers(self, time=None, action=lx.symbol.s_ACTIONLAYER_EDIT):
        """
        Gets all controllers that are keyframed at given time on a given action.

        Returns
        -------
        [ControllerItemFeature]
        """
        ctrls = self._getAllControllers()
        keyframed = []
        for ctrl in ctrls:
            channels = ctrl.animatedChannels
            for channel in channels:
                if modox.ChannelUtils.hasKeyframeOnTimeAndAction(channel, time, action):
                    keyframed.append(ctrl)
                    break
        return keyframed

    @property
    def currentControllers(self):
        """
        Gets current pose controllers. It'll get all controllers with no item selection and
        only selected controllers otherwise.

        Returns
        -------
        [Controller]
        """
        ctrls = self._getControllersFromSelection()
        if ctrls:
            return ctrls
        return self._getAllControllers()

    @property
    def currentChannels(self):
        """
        Gets current pose channels. It'll get all channels with no controller selection and
        only channels from selected controllers otherwise.

        Returns
        -------
        [modo.Channel]
        """
        if modox.ItemSelection().size == 0:
            return self.allChannels

        # We try to get channels from selection if there is some item selection.
        # If there are no valid controllers in selected
        selectedChannels = self._getControllerChannelsFromSelection()
        if selectedChannels:
            return selectedChannels

        return self.allChannels

    @property
    def allChannels(self):
        """
        Gets all the channels that are (or can be) part of the pose.

        Returns
        -------
        [modo.Channel]
        """
        ctrls = self._getAllControllers()

        channels = []
        for ctrl in ctrls:
            channels.extend(ctrl.animatedChannels)
        return channels

    @property
    def rig(self):
        return self._rig

    def copy(self):
        """
        Copies pose into the buffer.

        Buffer is persistent across single MODO session.
        """
        buffer =self._storePoseInBuffer(self.currentChannels)
        service.buffer.put(buffer, self._BUFFER_ID)

    def paste(self, buffer=None):
        """
        Pastes pose from buffer.

        The pose needs to be put into buffer using copy() first.

        Returns
        -------
        Buffer object that was used to paste pose from.
        You can still use that buffer afterwards for any subsequent operations.
        """
        if buffer is None:
            try:
                buffer = service.buffer.take(self._BUFFER_ID)
            except LookupError:
                if service.debug.output:
                    log.out("No pose in the buffer, can't paste anything...")
                return

        self._setPoseFromBuffer(buffer, self.currentChannels)
        return buffer

    def mirror(self):
        """
        Mirrors pose on the spot.
        """
        currentChannels = self.currentChannels

        posXChannelName = modox.c.TransformChannels.PositionX
        rotYZChannelNames = [modox.c.TransformChannels.RotationY, modox.c.TransformChannels.RotationZ]

        buffer = self._storePoseInBuffer(currentChannels)
        mirroredBuffer = {}
        for channelIdent in buffer:
            value = buffer[channelIdent]
            mirrorIdent = channelIdent
            modoChannelName = ChannelIdentifier.extractChannelNameFromIdentifier(channelIdent)

            if ChannelIdentifier.isCenterChannel(channelIdent):
                # Flip channel value on center channel only if it's rotation Y or Z.
                if modoChannelName in rotYZChannelNames:
                    value *= -1.0
            else:
                mirrorIdent = ChannelIdentifier.flipSide(channelIdent)

            # Always flip channel value if it's position X.
            if modoChannelName == posXChannelName:
                value *= -1.0

            mirroredBuffer[mirrorIdent] = value

        self._setPoseFromBuffer(mirroredBuffer, currentChannels)

    def mirrorPush(self):
        """
        Performs push mirror on selected controllers.

        Push mirror only works on sided controllers and pushes pose from one side to the other.
        """
        ctrls = self._getControllersFromSelection()

        sidedCtrls = []
        for ctrl in ctrls:
            if ctrl.item.side == c.Side.CENTER:
                continue
            sidedCtrls.append(ctrl)

        channels = self._getChannelsFromControllers(sidedCtrls)
        poseBuffer = self._storePoseInBuffer(channels)
        mirroredBuffer = self._getMirroredBuffer(poseBuffer)

        # Target controllers are all controllers
        self._setPoseFromBuffer(mirroredBuffer, self.allChannels)

    def mirrorPull(self):
        """
        Performs pull mirror on selected controllers.

        Pull mirror copies pose from equivalent controllers
        on the other side (if there are any).
        """
        selectedCtrls = self._getControllersFromSelection()
        targetCtrls = self._filterCentrControllersOut(selectedCtrls)
        targetChannels = self._getChannelsFromControllers(targetCtrls)

        ctrlsToPullFrom = self._getMirrorControllers(targetCtrls)
        channelsToPullFrom = self._getChannelsFromControllers(ctrlsToPullFrom)
        buffer = self._storePoseInBuffer(channelsToPullFrom)
        mirroredBuffer = self._getMirroredBuffer(buffer)
        self._setPoseFromBuffer(mirroredBuffer, targetChannels)

    # -------- Private methods

    def _getMirrorControllers(self, ctrls):
        """
        Tries to get controllers that are mirrors of the passed as argument ones.
        """
        ctrlsRefNames = []
        for ctrl in ctrls:
            ctrlsRefNames.append(ctrl.item.getMirroredReferenceName(module=True, basename=True))

        allCtrls = self._getAllControllers()
        sourceCtrls = {}
        for ctrl in allCtrls:
            sourceCtrls[ctrl.item.getReferenceName()] = ctrl

        mirrorCtrls = []
        for refName in ctrlsRefNames:
            try:
                mirrorCtrls.append(sourceCtrls[refName])
            except KeyError:
                continue
        return mirrorCtrls

    def _isAnyControllerSelected(self, limit=0):
        rigRootModoItem = self.rig.rootModoItem
        itemSelection = modox.ItemSelection()

        if limit == 0:
            limit = itemSelection.size

        result = False

        for x in range(limit):
            rawItem = itemSelection.getRawByIndex(x)
            try:
                rigItem = Item.getFromOther(rawItem)
            except TypeError:
                continue

            # For some reason it's possible to have rig item with no rig
            # in some circumstances, possibly some transient states when
            # this query gets fired so I need to be able to handle that case too.
            # AttributeError will be thrown when trying to test None for modoItem property.
            try:
                if rigItem.rigRootItem.modoItem != rigRootModoItem:
                    continue
            except AttributeError:
                continue

            try:
                ctrl = ControllerItemFeature(rigItem)
            except TypeError:
                continue

            result = True
            break

        return result

    def _getAllControllers(self):
        controllersElementSet = self._rig[c.ElementSetType.CONTROLLERS]
        ctrls = []
        for ctrlModoItem in controllersElementSet.elements:
            try:
                ctrl = ControllerItemFeature(ctrlModoItem)
            except TypeError:
                continue
            if ctrl.isStoredInPose:
                ctrls.append(ctrl)
        return ctrls

    def _getControllersFromSelection(self, limit=0):
        controllers = []
        rigRootModoItem = self.rig.rootModoItem
        itemSelection = modox.ItemSelection()

        if limit == 0:
            limit = itemSelection.size

        for x in range(limit):
            rawItem = itemSelection.getRawByIndex(x)
            try:
                rigItem = Item.getFromOther(rawItem)
            except TypeError:
                continue

            if rigItem.rigRootItem.modoItem != rigRootModoItem:
                continue

            try:
                ctrl = ControllerItemFeature(rigItem)
            except TypeError:
                continue

            if ctrl.isStoredInPose:
                controllers.append(ctrl)
        return controllers

    def _filterCentrControllersOut(self, ctrls):
        sidedCtrls = []
        for ctrl in ctrls:
            if ctrl.item.side == c.Side.CENTER:
                continue
            sidedCtrls.append(ctrl)
        return sidedCtrls

    def _getChannelsFromControllers(self, controllers):
        channels = []
        for ctrl in controllers:
            channels.extend(ctrl.animatedChannels)
        return channels

    def _getControllerChannelsFromSelection(self, limit=0):
        controllers = self._getControllersFromSelection(limit)
        return self._getChannelsFromControllers(controllers)

    def _storePoseInBuffer(self, channels):
        """
        Returns
        -------
        dict {str: value}
            key is channel identifier, value is channel value for the pose.
        """
        buffer = {}
        for channel in channels:
            ident = ChannelIdentifier.renderIdentifier(channel)
            value = modox.ChannelUtils.getRawChannelValue(channel, None, lx.symbol.s_ACTIONLAYER_EDIT)

            buffer[ident] = value
        return buffer

    def _getMirroredBuffer(self, buffer):
        posXChannelName = modox.c.TransformChannels.PositionX
        rotYZChannelNames = [modox.c.TransformChannels.RotationY, modox.c.TransformChannels.RotationZ]

        mirroredBuffer = {}
        for channelIdent in buffer:
            value = buffer[channelIdent]
            mirrorIdent = channelIdent
            modoChannelName = ChannelIdentifier.extractChannelNameFromIdentifier(channelIdent)

            if ChannelIdentifier.isCenterChannel(channelIdent):
                # Flip channel value on center channel only if it's rotation Y or Z.
                if modoChannelName in rotYZChannelNames:
                    value *= -1.0
            else:
                mirrorIdent = ChannelIdentifier.flipSide(channelIdent)

            # Always flip channel value if it's position X.
            if modoChannelName == posXChannelName:
                value *= -1.0

            mirroredBuffer[mirrorIdent] = value
        return mirroredBuffer

    def _setPoseFromBuffer(self, buffer, channels):
        for channel in channels:
            ident = ChannelIdentifier.renderIdentifier(channel)
            try:
                value = buffer[ident]
            except KeyError:
                continue
            channel.set(value, time=None, key=True, action=lx.symbol.s_ACTIONLAYER_EDIT)

    def __init__(self, rig):
        if not isinstance(rig, Rig):
            try:
                self._rig = Rig(rig)
            except TypeError:
                raise
        else:
            self._rig = rig

        self._controllers = None