
""" Channel set added to rig event definition.
"""


import rs.event
import rs.const as c


class EventChannelSetAdded(rs.event.Event):
    """ Event to send when channel set was added to rig.
    
    Callback
    --------
    group : modo.Item or modo.Group
        Callback takes single argument which is a channel set group item.
    """
    
    descType = c.EventTypes.CHANNEL_SET_ADDED
    descUsername = 'Channel Set Added'