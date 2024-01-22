
""" Side of module or item changed.
"""


import rs.event
import rs.const as c


class EventModuleSideChanged(rs.event.Event):
    """ Event to send when module's side was changed.
    
    Callback
    --------
    module : Module
        Module which side was changed.

    oldSide : str
        Old side constant.

    newSide : str
        New side constant.
    """

    descType = c.EventTypes.MODULE_SIDE_CHANGED
    descUsername = 'Module Side Changed'


class EventItemSideChanged(rs.event.Event):
    """ Event to send when item's side was changed.
    
    Callback
    --------
    item : Item
        Callback takes single argument, an Item which side was changed.
    """
    
    descType = c.EventTypes.ITEM_SIDE_CHANGED
    descUsername = 'Item Side Changed'
