

import lx
import modo
from . import sys_component
from . import const as c

actionSetup = lx.symbol.s_ACTIONLAYER_SETUP


class MetaGroup(sys_component.SystemComponent):
    """ Represents a collection of items in meta rig.
    
    Parameters
    ----------
    existingGroupItem : modo.Group, modo.Item, lx.object.Item
        Group item that is base for this meta group.

    Raises
    ------
    TypeError
        
    Attributes
    ----------
    descModoGroupType : str
        Type of modo group the meta group is based on.
        This is the same as the value of the tag set on MODO group items.
        When empty a standard group will be created.

    descDeleteWithChildren : bool
        When set to True the group will be deleted along with its children groups.
        Use it cautiously and ONLY for groups that have other groups parented to them
        which are NOT PART OF META RIG (channel sets group is an example)!

    Methods
    -------
    onItemAdded()
        Called when an item is added to the rig.
    
    onItemRemoved()
        Called when an item is removed from the rig.
        
    onItemChanged()
        Called when an item in a rig has changed.
    """

    TAG_META_GROUP = 'RSMG'
    
    descIdentifier = ''
    descUsername = ''
    descModoGroupType = ''
    descDeleteWithChildren = False
    descVisibleDefault = c.TriState.DEFAULT
    descRenderDefault = c.TriState.DEFAULT
    descSelectableDefault = c.TriState.DEFAULT
    descLockedDefault = c.TriState.DEFAULT

    # -------- System Component Interface

    @classmethod
    def sysType(cls):
        return c.SystemComponentType.META_GROUP

    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
    
    @classmethod
    def sysUsername(cls):
        return cls.descUsername

    # -------- Public class methods
    
    @classmethod
    def new(cls):
        newGroup = modo.Scene().addGroup(cls.descUsername, cls.descIdentifier)
        newGroup.setTag(cls.TAG_META_GROUP, cls.descIdentifier)
        newMetaGroup = cls(newGroup)
        newMetaGroup.resetPropertiesToDefaults()
        return newMetaGroup

    # -------- Public methods
    
    @property
    def modoGroupItem(self):
        return self._group

    @property
    def items(self):
        """ Gets a list of modo item members.
        
        Returns
        -------
        list of modo.Item
        """
        return self.modoGroupItem.items
    
    @property
    def channels(self):
        return self.modoGroupItem.channels

    @property
    def childGroups(self):
        return self.modoGroupItem.children(recursive=True)

    @property
    def membersVisible(self):
        return self._group.channel('visible').get()
    
    @membersVisible.setter
    def membersVisible(self, state):
        """ Tristate.
        """
        self._group.channel('visible').set(state, time=0.0, key=False, action=actionSetup)

    @property
    def membersRender(self):
        return self._group.channel('render').get()
    
    @membersRender.setter
    def membersRender(self, state):
        self._group.channel('render').set(state, time=0.0, key=False, action=actionSetup)

    @property
    def membersSelectable(self):
        return self._group.channel('select').get()

    @membersSelectable.setter
    def membersSelectable(self, state):
        self._group.channel('select').set(state, time=0.0, key=False, action=actionSetup)

    @property
    def membersLocked(self):
        return self._group.channel('lock').get()
    
    @membersLocked.setter
    def membersLocked(self, state):
        self._group.channel('lock').set(state, time=0.0, key=False, action=actionSetup)

    def resetPropertiesToDefaults(self):
        self.membersVisible = self.descVisibleDefault
        self.membersSelectable = self.descSelectableDefault
        self.membersLocked = self.descLockedDefault
        self.membersRender = self.descRenderDefault

    # -------- Default interface implementations.
    
    def onItemRemoved(self, modoItem):
        """ Called when item removed event was sent.
        
        This default implementation removes the item if it belongs to a group.
        It does it without testing the type.
        
        Parameters
        ----------
        modoItem : modo.Item
        """
        self.removeItemFromGroup(modoItem)
        
    # -------- Helper methods for clients to use
    
    def addItems(self, items):
        """ Adds a single or a list of items to a group.
        
        Paramters
        ---------
        items : modo.Item, list of modo.Item
        """
        self.modoGroupItem.addItems(items)

    def addChannelsToGroup(self, channels):
        """ Adds a list of channels to the group.
        
        Parameters
        ----------
        channels : list of modo.Channel
        """
        for channel in channels:
            self.modoGroupItem.addChannel(channel)

    def removeItemFromGroup(self, modoItem):
        """ Removes given item from group.
        
        Parameters
        ----------
        modoItem : modo.Item
        """
        # TODO: This might be slow.
        self.modoGroupItem.removeItems(modoItem)

    def removeItemChannelsFromGroup(self, modoItem):
        """ Removes all channels related to an item from group.
        
        This removes item's own channels as well as its
        primary transform channels!
        
        Parameters
        ----------
        modoItem : modo.Item
        """
        channels = self._getItemChannelsInGroup(modoItem)
        for chan in channels:
            self.modoGroupItem.removeChannel(chan.index, chan.item)

    def updateChannelsForItem(self, modoItem, newChannelsList):
        """ Updates channels in group to match new channels list.
        
        This method performs non-destructive update. This means
        that channels that are already in group will not be touched.
        Channels that are in group but are not on the new channels list
        will be removed and ones that are in the new list but not
        in a group yet will be added.
        """
        channelsInGroup = self._getItemChannelsInGroup(modoItem)
        channelsInGroupIdents = self._channelsToChannelIdents(channelsInGroup)
        newChannelIdents = self._channelsToChannelIdents(newChannelsList)

        channelsToRemove = []
        channelsToAdd = []

        for chanInGroup in channelsInGroup:
            if self._renderChannelIdent(chanInGroup) not in newChannelIdents:
                channelsToRemove.append(chanInGroup)

        for actorChan in newChannelsList:
            if self._renderChannelIdent(actorChan) not in channelsInGroupIdents:
                channelsToAdd.append(actorChan)

        for channel in channelsToRemove:
            self.modoGroupItem.removeChannel(channel.index, channel.item)
        
        for channel in channelsToAdd:
            self.modoGroupItem.addChannel(channel)

    # -------- Private methods

    def _getItemChannelsInGroup(self, modoItem):
        """ Gets a list of channels related to the given item that are already in group.
        
        Returns
        -------
        list : modo.Channel
        """
        itemIdents = [modoItem.id]
        try:
            loc = modo.LocatorSuperType(modoItem.internalItem)
        except TypeError:
            pass
        else:
            itemIdents.append(loc.position.id)
            itemIdents.append(loc.rotation.id)
            itemIdents.append(loc.scale.id)

        chans = []
        for channel in self.modoGroupItem.groupChannels:
            if channel.item.id in itemIdents:
                chans.append(channel)
        
        return chans
    
    def _renderChannelIdent(self, channel):
        return channel.item.id + str(channel.index)

    def _channelsToChannelIdents(self, chanList):
        return [self._renderChannelIdent(chan) for chan in chanList]

    def __init__(self, existingGroupItem):
        if not isinstance(existingGroupItem, modo.Group):
            if isinstance(existingGroupItem, modo.Item):
                existingGroupItem = modo.Group(existingGroupItem.internalItem)
            elif isinstance(existingGroupItem, lx.object.Item):
                existingGroupItem = modo.Group(existingGroupItem)
            else:
                raise TypeError
        self._group = existingGroupItem
