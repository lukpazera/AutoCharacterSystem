
""" Item added to rig event definition.
"""


import rs.event
import rs.const as c


class EventItemAdded(rs.event.Event):
    """ Event to send when an item was added to rig.
    
    Callback
    --------
    item : modo.Item
        Callback takes single argument which is an item that was added to the rig.
    """
    
    descType = c.EventTypes.ITEM_ADDED
    descUsername = 'Item Added'