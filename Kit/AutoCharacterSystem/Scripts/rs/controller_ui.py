

import lx
import modo
import modox

from .core import service
from .const import EventTypes as e


class ChannelSet(object):
    """ Allows for creating channels sets attached to a scene item.
    
    You do not access channel set directly but through a modo item
    that the channel set is related to.
    ChannelSet is suited for building sets from user channels only.

    Parameters
    ----------
    modoItem : modo.Item, modo.Group
        Either Modo item to which the channel set is linked or the 
        channel set modo.Group item.
    
    Raises
    ------
    TypeError
        If modoItem does not have channel sets attached to it.
    """

    CHAN_SET_GRAPH = 'rs.channelSet'
    CHAN_SET_GROUP_TYPE = 'chanset'
    
    @classmethod
    def new(self, name, channels, modoItem):
        self._newChanSetItem(name, channels, modoItem)
        chanSet = ChannelSet(modoItem)
        return chanSet

    @classmethod
    def removeIfFree(cls, modoItem):
        """
        Removes channel set if it's not linked to rig controller.

        Parameters
        ----------
        modoItem : modo.Item
            Channel set group modo item.
        """
        ctrl = modox.ItemUtils.getFirstForwardGraphConnection(modoItem, cls.CHAN_SET_GRAPH)
        if ctrl is None:  # None means this channel set is not connected to any controller.
            lx.eval('!item.delete group child:0 item:{%s}' % (modoItem.id))

    def open(self):
        lx.eval('!tool.drop')
        self._chanSetItem.select(replace=False)
        self._chanSetItem.deselect()
    
    def rebuild(self, channels):
        chanSetName = self._chanSetItem.name
        self.selfDelete()
        self._chanSetItem = self._newChanSetItem(chanSetName, channels, self._modoItem)

    def freeFromRig(self):
        """
        Frees channel set from the rig.

        After channel set is freed there's no link between channel set and rig anymore
        so it becomes an independent element in the scene.
        """
        modox.ItemUtils.clearForwardGraphConnections(self._chanSetItem, self.CHAN_SET_GRAPH)

    def selfDelete(self):
        modo.Scene().removeItems(self._chanSetItem)
    
    @property
    def channelSetModoItem(self):
        """
        Gets channel set group item.

        Returns
        -------
        modo.Item
        """
        return self._chanSetItem

    @property
    def channelsSourceModoItem(self):
        """
        Gets source item from channels are coming from.

        Returns
        -------
        modo.Item
        """
        return self._modoItem

    @property
    def name(self):
        """
        Gets channel set modo item name.

        Returns
        -------
        str
        """
        return self._chanSetItem.name

    @name.setter
    def name(self, name):
        """
        Sets new name for channel set modo Item.

        Parameters
        ----------
        name : str
        """
        self._chanSetItem.name = name

    # -------- Private methods

    @classmethod
    def _newChanSetItem(self, name, channels, modoItem):
        chanSet = modo.Scene().addGroup(name, self.CHAN_SET_GROUP_TYPE)
        
        chanUtils = modox.ChannelUtils()
        xitem = modox.Item(modoItem)
        userChans = xitem.getUserChannels(sort=True)
        setChansNames = [chan.name for chan in channels]
        
        for chan in userChans:
            if chan.name in setChansNames or chanUtils.isDivider(chan):
                chanSet.addChannel(chan)

        ctrlGraph = modoItem.itemGraph(self.CHAN_SET_GRAPH)
        chanSetGraph = chanSet.itemGraph(self.CHAN_SET_GRAPH)
        chanSetGraph >> ctrlGraph

        service.events.send(e.CHANNEL_SET_ADDED, group=chanSet)
    
        return chanSet

    def _getChannelSetItem(self):
        graph = self._modoItem.itemGraph(self.CHAN_SET_GRAPH)
        connectedSets = graph.reverse()
        if len(connectedSets) > 0:
            return connectedSets[0]
        return None

    def _getSourceItemFromChannelSetItem(self):
        graph = self._chanSetItem.itemGraph(self.CHAN_SET_GRAPH)
        connectedSets = graph.forward()
        if len(connectedSets) > 0:
            return connectedSets[0]
        return None

    def __init__(self, modoItem):
        if modoItem.type == self.CHAN_SET_GROUP_TYPE:
            self._chanSetItem = modoItem
            self._modoItem = self._getSourceItemFromChannelSetItem()
            if self._modoItem is None:
                raise TypeError
        else:
            self._modoItem = modoItem
            self._chanSetItem = self._getChannelSetItem()
            if self._chanSetItem is None:
                raise TypeError
