"""
Item Cache

Use this class to cache and then restore some item data.
This can be done either on the same item or across different items.
"""

import math

import lx
import modo
import modox

from . import const as c
from .log import log


class ChannelCache(object):
    name = None
    storageType = None
    value = None
    forwardLinks = {}
    reverseLinks = {}

    # -------- Private methods

    def __init__(self, name=None, storageType=None):
        if name is not None:
            self.name = name
        if storageType is not None:
            self.storageType = storageType


class ItemCache(object):

    def cacheChannels(self, modoItem, packageNames=None):
        """
        Caches connections from/to all channels that belong to rigging system package.

        By default we assume that all rig item or rig package names start with 'rs.' prefix and
        we only cache these.

        Parameters
        ----------
        modoItem : modo.Item
            The item which channel connections should be cached.

        packageNames : str, [str], optional
            If packageNames is not None only channels belonging to listed package(s) are going to be cached
            instead of all rig package names.
        """
        if packageNames is not None and type(packageNames) not in (list, tuple):
            packageNames = [packageNames]

        for channel in modoItem.channels():
            if packageNames is not None and modox.ChannelUtils.getPackageName(channel) not in packageNames:
                continue
            elif not self._isSystemPackageChannel(channel):
                continue

            hasLinks = False
            chanCache = ChannelCache(channel.name, channel.storageType)
            # Cache value for numeric channels only
            if modox.ChannelUtils.isNumericChannel(channel):
                chanCache.value = channel.get(None, None) # caching eval action at current time value for now.
            else:
                chanCache.value = None

            if channel.fwdCount > 0:
                chanCache.forwardLinks = channel.fwdLinked
                hasLinks = True
            if channel.revCount > 0:
                chanCache.reverseLinks = channel.revLinked
                hasLinks = True

            if hasLinks:
                self._channelsCache.append(chanCache)

    def restoreChannels(self, modoItem):
        """
        Restores all connections from cache to a given item.

        Parameters
        ----------
        modoItem : modo.Item
            The item the connections should be restored to.
        """
        if not self._channelsCache:
            return

        xitem = modox.Item(modoItem.internalItem)

        for chanCache in self._channelsCache:
            channel = modoItem.channel(chanCache.name)
            if channel is None:
                channel = xitem.addUserChannel(chanCache.name, chanCache.storageType)
                # It's crucial here to set value on setup action directly.
                # It doesn't work correctly in every case otherwise.
                # Also, be sure to skip setting value if cache is None
                # as that indicates non-numeric channel (like Matrix or other storage type or eval).
                if chanCache.value is not None:
                    try:
                        channel.set(chanCache.value, 0.0, False, lx.symbol.s_ACTIONLAYER_SETUP)
                    except RuntimeError:
                        log.out('Setting value from cache failed for channel: %s' % (channel.item.name + ':' + channel.name))
            for linkedChannel in chanCache.reverseLinks:
                linkedChannel >> channel
            for linkedChannel in chanCache.forwardLinks:
                channel >> linkedChannel

    def applyOutputs(self, modoItem):
        """
        Applies all channel output values for an item to channels that are driven by these outputs.

        This is meant for applying guide outputs really so it only works with
        evaluated static values that are applied to setup action.
        This function probably needs to be enhanced if it needs to be used beyond
        applying guide outputs.
        """
        for channel in modoItem.channels():
            sourceIsAngle = modox.ChannelUtils.isAngleChannel(channel)
            if channel.fwdCount == 0:
                continue
            v = channel.get(time=None, action=None) # We need evaluated value
            for outputChannel in channel.fwdLinked:
                # Only numeric channels are supported.
                if not modox.ChannelUtils.isNumericChannel(outputChannel):
                    continue
                # When we apply an angle value to a non-angle channel we need to convert
                # radians (angles are in radians internally) to degrees.
                # MODO does that automatically in UI so you never see radians but under the hood
                # applying raw angle value to a non-angle channel will make it apply
                # angle in radians, not degrees!!!
                if sourceIsAngle and not modox.ChannelUtils.isAngleChannel(outputChannel):
                    v = math.degrees(v)
                outputChannel.set(v, 0.0, False, lx.symbol.s_ACTIONLAYER_SETUP)

    # -------- Private methods

    def _isSystemPackageChannel(self, channel):
        index = channel.index
        item = channel.item.internalItem

        # This tests item and user channels
        # these have no packages
        try:
            package = item.ChannelPackage(index)
        except LookupError:
            return False

        return package.startswith(c.String.SYSTEM_PACKAGE_PREFIX)

    def __init__(self):
        self._channelsCache = []