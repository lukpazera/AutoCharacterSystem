
""" Event handler that is processing events affecting meta rig.
"""


import modo

from ..event_handler import EventHandler
from ..const import EventTypes as e
from ..const import MetaGroupType as m
from ..const import TriState
from ..log import log
from ..component_setups.rig import RigComponentSetup
from ..items.root_item import RootItem
from ..rig import Rig
from ..meta_rig import MetaRig
from ..controller_ui import ChannelSet


class MetaRigEventHandler(EventHandler):
    """ Handles events that affect meta rig.
    """

    descIdentifier = 'metarig'
    descUsername = 'Meta Rig'
  
    @property
    def eventCallbacks(self):
        return {e.ITEM_ADDED: self.event_itemAdded,
                e.ITEM_CHANGED: self.event_itemChanged,
                e.ITEM_REMOVED: self.event_itemRemoved,
                e.CHANNEL_SET_ADDED: self.event_channelSetAdded,
                e.ITEM_CHAN_EDIT_BATCH_PRE: self.event_itemChanEditPre,
                e.ITEM_CHAN_EDIT_BATCH_POST: self.event_itemChanEditPost}

    def event_itemAdded(self, **kwargs):
        try:
            addedItem = kwargs['item']
        except KeyError:
            return
        metaRig = self._getMetaRigFromItem(addedItem)
        if metaRig is None:
            return
        self._item = addedItem
        metaRig.iterateOverGroups(self._callOnItemAdded)

    def event_itemChanged(self, **kwargs):
        try:
            changedItem = kwargs['item']
        except KeyError:
            return
        metaRig = self._getMetaRigFromItem(changedItem)
        if metaRig is None:
            return
        self._item = changedItem
        metaRig.iterateOverGroups(self._callOnItemChanged)

    def event_itemRemoved(self, **kwargs):
        try:
            itemToRemove = kwargs['item']
        except KeyError:
            return
        metaRig = self._getMetaRigFromItem(itemToRemove)
        if metaRig is None:
            return
        self._item = itemToRemove
        metaRig.iterateOverGroups(self._callOnItemRemoved)

    def event_channelSetAdded(self, **kwargs):
        """ Called when channel set is added to rig.
        
        We want to make that channel set group item be part
        of meta rig groups hierarchy - it needs to be parented
        to the channels sets meta group.
        """
        try:
            chanSetGroupItem = kwargs['group']
        except KeyError:
            return
        
        try:
            chanSet = ChannelSet(chanSetGroupItem)
        except TypeError:
            return

        metaRig = self._getMetaRigFromItem(chanSet.channelsSourceModoItem)
        if metaRig is None:
            return
        
        try:
            chanSetsGroup = metaRig.getGroup(m.CHANNEL_SETS)
        except LookupError:
            return

        chanSetGroupItem.setParent(chanSetsGroup.modoGroupItem)

    def event_itemChanEditPre(self, **kwargs):
        """ Called before some items channels will be edited.
        
        Meta rig needs to unlock all the locked channels, editing channel
        values will not work correctly otherwise.
        """
        # We need to create a bunch of class properties to cache data.
        # These will be deleted from the post event.
        try:
            rootItem = kwargs['rig']
        except KeyError:
            return
        
        if isinstance(rootItem, Rig):
            rootItem = rootItem.rootItem
        if not isinstance(rootItem, RootItem):
            return

        self._metaRig = MetaRig(rootItem)
        self._lockGroup = self._metaRig.getGroup(m.LOCKED_CHANNELS)
        self._lockStateBkp = self._lockGroup.membersLocked
        self._lockGroup.membersLocked = TriState.OFF
    
    def event_itemChanEditPost(self, **kwargs):
        """ Get locked channels back on.
        """
        # If members data was no set up properly during the pre event
        # we just leave and do nothing.
        try:
            self._lockGroup.membersLocked = self._lockStateBkp
        except AttributeError:
            return

        del self._lockStateBkp
        del self._lockGroup
        del self._metaRig

    # -------- Private methods
    
    def _callOnItemAdded(self, group):
        try:
            group.onItemAdded(self._item)
        except AttributeError:
            pass

    def _callOnItemChanged(self, group):
        try:
            group.onItemChanged(self._item)
        except AttributeError:
            pass

    def _callOnItemRemoved(self, group):
        try:
            group.onItemRemoved(self._item)
        except AttributeError:
            pass

    def _getMetaRigFromItem(self, modoItem):
        """ Gets meta rig from a given item.
        
        Returns
        -------
        MetaRig
            Or None if meta rig cannot be found.
        """
        try:
            rigSetup = RigComponentSetup(modoItem)
        except TypeError:
            return None

        rootItem = RootItem(rigSetup.rootModoItem)
        return MetaRig(rootItem)