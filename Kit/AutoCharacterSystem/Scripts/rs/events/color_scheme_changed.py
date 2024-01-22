
""" Color scheme of the rig has changed.
"""


import rs.event
import rs.const as c


class EventModuleSideChanged(rs.event.Event):
    """ Event sent when rig's color scheme was changed.
    
    Callback
    --------
    rig : Rig
        Callback takes single argument with a rig which color scheme
        was changed.
    """
    
    descType = c.EventTypes.RIG_COLOR_SCHEME_CHANGED
    descUsername = 'Rig Color Scheme Changed'
