
""" Item in rig changed event definition.
"""


import rs.event
import rs.const as c


class EventItemChanged(rs.event.Event):
    """ Event to send when an item belonging to a rig changed
    its properties.
    
    Callback
    --------
    item : modo.Item
        Callback takes single argument which is a rig item that changed.
    """
    
    descType = c.EventTypes.ITEM_CHANGED
    descUsername = 'Item Changed'