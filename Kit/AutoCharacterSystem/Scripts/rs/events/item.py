
""" Various events that concern items.
"""


from ..event import Event
from .. import const as c


class EventItemRemoved(Event):
    """ Event to send when an item belonging to a rig was moved out of the rig.
    
    Note that this means that the item was not deleted, just moved out
    of the rig setup.

    Callback
    --------
    item : modo.Item
        Callback takes single argument which is a rig item that was removed.
    """
    
    descType = c.EventTypes.ITEM_REMOVED
    descUsername = 'Item Removed'


class EventItemChannelEditBatchPre(Event):
    """ Event to send prior to editing some items channels.
    
    This event is really just for unlocking channels to changes.

    Callback
    --------
    rig : Rig, RootItem
        Callback takes single argument, a rig which items channels
        will be edited or rig's RootItem.
    """
    
    descType = c.EventTypes.ITEM_CHAN_EDIT_BATCH_PRE
    descUsername = 'Item Channel Editing Batch Pre'


class EventItemChannelEditBatchPost(Event):
    """ Event to send after editing of set of channels is done.
    
    Callback
    --------
    Takes no arguments, you need to cache data during the Pre event.
    """
    
    descType = c.EventTypes.ITEM_CHAN_EDIT_BATCH_POST
    descUsername = 'Item Channel Editing Batch Post'


class EventRigItemSelected(Event):
    """ Event to send when rig item was selected.
    
    Callback
    --------
    item : Item
        Takes one argument - rig item that was selected.
    """
    
    descType = c.EventTypes.RIG_ITEM_SELECTED
    descUsername = 'Rig Item Selected'
