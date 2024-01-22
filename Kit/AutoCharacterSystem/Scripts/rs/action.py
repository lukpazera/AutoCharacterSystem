

import lx
import lxu
import modo
import modox

from .core import service
from .rig import Rig
from .item_features.controller import ControllerItemFeature
from . import const as c
from .util_chan import ChannelIdentifier
from .log import log
from .item import Item
from .util import run
from modox import channel_lxe


class Action(object):
    """
    This object represents an animation action.
    """

    @property
    def allChannels(self):
        """
        Gets all the channels that are (or can be) part of the pose.

        Returns
        -------
        [modo.Channel]
        """
        controllersElementSet = self.rig[c.ElementSetType.CONTROLLERS]
        ctrls = controllersElementSet.elements
        channels = []
        for ctrlModoItem in ctrls:
            try:
                ctrl = ControllerItemFeature(ctrlModoItem)
            except TypeError:
                continue
            channels.extend(ctrl.animatedChannels)
        return channels

    @property
    def rig(self):
        return self._rig

    def mirror(self):
        """
        Mirrors action on the spot.
        """
        self._mirrorByLxe()

    # -------- Private methods

    def _mirrorByLxe(self):
        posXChannelName = modox.c.TransformChannels.PositionX
        rotYZChannelNames = [modox.c.TransformChannels.RotationY, modox.c.TransformChannels.RotationZ]

        # Channel map has all the channels keyed by their identifiers.
        channelMap = self._buildChannelMap()
        channelIdentsToProcess = self._getListOfChannelIdentifiersToProcess(list(channelMap.keys()))

        chanUtilsLxe = channel_lxe.ChannelUtils()
        selectionService = lx.service.Selection()
        scene = lx.object.Scene(lxu.select.SceneSelection().current())
        chanRead = lx.object.ChannelRead(scene.Channels(lx.symbol.s_ACTIONLAYER_EDIT, selectionService.GetTime()))
        chanWrite = lx.object.ChannelWrite(scene.Channels(lx.symbol.s_ACTIONLAYER_EDIT, selectionService.GetTime()))

        for channelIdent in channelIdentsToProcess:
            mirrorIdent = channelIdent
            mirrorValues = False
            modoChannelName = ChannelIdentifier.extractChannelNameFromIdentifier(channelIdent)

            if ChannelIdentifier.isCenterChannel(channelIdent):
                # Flip channel value on center channel only if it's rotation Y or Z.
                if modoChannelName in rotYZChannelNames:
                    mirrorValues = True
            else:
                mirrorIdent = ChannelIdentifier.flipSide(channelIdent)

            # Always flip channel value if it's position X.
            if modoChannelName == posXChannelName:
                mirrorValues = True

            sourceChannel = channelMap[channelIdent]

            # Swap channels if we're doing one side to another
            if mirrorIdent != channelIdent:
                # If a channel doesn't have an equivalent on the other side - skip the operation.
                try:
                    targetChannel = channelMap[mirrorIdent]
                except KeyError:
                    continue

                chanUtilsLxe.CopyItemChannelsByName(
                    chanRead,
                    chanWrite,
                    sourceChannel.item.internalItem,
                    targetChannel.item.internalItem,
                    [sourceChannel.name],
                    None,
                    channel_lxe.iCHAN_READMODE_ALL,
                    channel_lxe.iCHAN_WRITEMODE_AUTO,
                    True,  # mutual copy
                    mirrorValues,
                    False)

            else:
                if mirrorValues:
                    modox.ChannelUtils.mirrorChannel(sourceChannel)

    def _mirrorByChannelCopyPaste(self):
        posXChannelName = modox.c.TransformChannels.PositionX
        rotYZChannelNames = [modox.c.TransformChannels.RotationY, modox.c.TransformChannels.RotationZ]

        # Channel map has all the channels keyed by their identifiers.
        channelMap = self._buildChannelMap()
        channelIdentsToProcess = self._getListOfChannelIdentifiersToProcess(list(channelMap.keys()))

        for channelIdent in channelIdentsToProcess:
            mirrorIdent = channelIdent
            mirrorValues = False
            modoChannelName = ChannelIdentifier.extractChannelNameFromIdentifier(channelIdent)

            if ChannelIdentifier.isCenterChannel(channelIdent):
                # Flip channel value on center channel only if it's rotation Y or Z.
                if modoChannelName in rotYZChannelNames:
                    mirrorValues = True
            else:
                mirrorIdent = ChannelIdentifier.flipSide(channelIdent)

            # Always flip channel value if it's position X.
            if modoChannelName == posXChannelName:
                mirrorValues = True

            sourceChannel = channelMap[channelIdent]

            # Swap channels if we're doing one side to another
            if mirrorIdent != channelIdent:

                # If a channel doesn't have an equivalent on the other side - skip the operation.
                try:
                    targetChannel = channelMap[mirrorIdent]
                except KeyError:
                    continue

                if mirrorValues:
                   modox.ChannelUtils.mirrorChannel(sourceChannel)
                   modox.ChannelUtils.mirrorChannel(targetChannel)

                # Assign buffer channel here
                sourceStorageType = sourceChannel.storageType
                bufferChannel = self._getTempChannel(sourceStorageType)

                sourceIdent = modox.ChannelUtils.getChannelIdent(sourceChannel)
                targetIdent = modox.ChannelUtils.getChannelIdent(targetChannel)
                bufferIdent = modox.ChannelUtils.getChannelIdent(bufferChannel)

                # Do the swapping
                run('select.channel {%s} mode:set' % (sourceIdent))
                run('channel.copy')
                run('select.channel {%s} mode:set' % (bufferIdent))
                run('channel.paste')

                run('select.channel {%s} mode:set' % (targetIdent))
                run('channel.copy')
                run('select.channel {%s} mode:set' % (sourceIdent))
                run('channel.paste')

                run('select.channel {%s} mode:set' % (bufferIdent))
                run('channel.copy')
                run('select.channel {%s} mode:set' % (targetIdent))
                run('channel.paste')

                # Clear selection at the end
                run('select.channel {%s} mode:remove' % (targetIdent))

            else:
                if mirrorValues:
                    modox.ChannelUtils.mirrorChannel(sourceChannel)

    def _getListOfChannelIdentifiersToProcess(self, identifiers):
        """
        We're only going to process right side and center channels.
        Left side channels will be processed with right side automatically if they have an equivalent.
        """
        filteredIdentifiers = []
        for identifier in identifiers:
            if ChannelIdentifier.isRightSideChannel(identifier) or ChannelIdentifier.isCenterChannel(identifier):
                filteredIdentifiers.append(identifier)
        return filteredIdentifiers

    def _buildChannelMap(self):
        """
        Returns
        -------
        dict {str: value}
            key is channel identifier, value is the channel itself.
        """
        buffer = {}
        for channel in self.allChannels:
            ident = ChannelIdentifier.renderIdentifier(channel)
            buffer[ident] = channel
        return buffer

    def _getTempChannel(self, storageType):
        rootModoItem = self._rig.rootModoItem
        xitem = modox.Item(rootModoItem.internalItem)

        channelName = 'rsBuffer' + storageType
        bufferChannel = rootModoItem.channel(channelName)
        if bufferChannel is None:
            bufferChannel = xitem.addUserChannel(channelName, storageType)
        return bufferChannel

    def __init__(self, rig):
        if not isinstance(rig, Rig):
            try:
                self._rig = Rig(rig)
            except TypeError:
                raise
        else:
            self._rig = rig