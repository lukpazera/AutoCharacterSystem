

import modox

from .item import Item
from . import const as c


class ChannelIdentifier(object):
    """
    Utility class for creating unique identifiers for rig item channels.

    The identifier is a simple string with no spaces so it can be used as a channel name.
    Identifier takes into account:
    - module name
    - item type
    - item name
    - channel name
    """
    @classmethod
    def renderIdentifier(cls, channel):
        """
        Renders an unique string identifier for rig item channel.

        Parameters
        ----------
        channel : modo.Channel

        Raises
        ------
        TypeError
            When channel does not belong to rig item.
        """
        # To generate channel preset idents I need main item
        # and not its transform. So I need to get main item from transform one first.
        if modox.ItemUtils.isTransformItem(channel.item):
            sourceItem = modox.ItemUtils.getTransformItemHost(channel.item)
        else:
            sourceItem = channel.item

        try:
            rigItem = Item.getFromModoItem(sourceItem)
        except TypeError:
            raise TypeError

        side = rigItem.side
        moduleName = rigItem.moduleRootItem.name.replace(' ', '_')  # module name can have spaces
        itemName = rigItem.name.replace(' ',
                                        '_')  # rig item name can have spaces and these are forbidden in channel names.
        chanName = channel.name
        itemType = rigItem.type.replace(' ', '_')  # just in case

        sideTrans = {c.Side.RIGHT: 'R', c.Side.LEFT: 'L', c.Side.CENTER: 'C'}
        sideString = sideTrans[side]

        renderedName = sideString + '..' + moduleName + '..' + itemType + '..' + itemName + '..' + chanName
        return renderedName

    @classmethod
    def flipSide(cls, identifier):
        """
        Flips side on identifier.

        Use this if you want to "mirror" identifier.

        Parameters
        ----------
        identifier : str
        """
        if identifier.startswith('R'):
            return 'L' + identifier[1:]
        elif identifier.startswith('L'):
            return 'R' + identifier[1:]
        return identifier

    @classmethod
    def isCenterChannel(cls, identifier):
        """
        Tests whether given identifier is for a channel that is on center item.

        Returns
        -------
        bool
        """
        if identifier.startswith('C'):
            return True
        return False

    @classmethod
    def isRightSideChannel(cls, identifier):
        """
        Tests whether given identifier is for a channel that is on right side.

        Returns
        -------
        bool
        """
        return identifier.startswith('R')

    @classmethod
    def extractChannelNameFromIdentifier(cls, identifier):
        """
        Extracts MODO channel name from the channel identifier.

        Returns
        -------
        str
            The extracted channel name.
        """
        return identifier.rpartition('..')[2]
