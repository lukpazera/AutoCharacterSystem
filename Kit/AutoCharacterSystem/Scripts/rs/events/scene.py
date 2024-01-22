

from ..event import Event
from .. import const as c


class EventContextRigResetVisible(Event):
    """ Event to send when leaving context is resetting visibility.
    
    Callback
    --------
    context : Context
    rig : Rig
        Callback takes two arguments, a context that system switches to and a rig
        for which item visibility needs to be switched
    """
    
    descType = c.EventTypes.CONTEXT_RIG_VIS_RESET
    descUsername = 'Reset Rig Visibility For Context'


class EventContextRigSetVisible(Event):
    """ Event to send when switching context is setting visibility.

    Callback
    --------
    context : Context
    rig : Rig
        Callback takes three arguments, visibility state to switch to, a context that system switches to
        and a rig for which item visibility needs to be switched
    """
    
    descType = c.EventTypes.CONTEXT_RIG_VIS_SET
    descUsername = 'Set Rig Visibility For Context'


class EventEditRigChanged(Event):
    """ Event to send when edit rig was changed.

    Callback
    --------
        Callback has no arguments.
    """
    
    descType = c.EventTypes.EDIT_RIG_CHANGED
    descUsername = 'Edit Rig Changed'
    