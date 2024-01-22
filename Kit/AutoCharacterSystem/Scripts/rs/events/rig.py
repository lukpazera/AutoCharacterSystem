

from ..event import Event
from .. import const as c


class EventRigReferenceSizeChanged(Event):
    """ Event sent after rig reference size as changed.

    Callback
    --------
    rig : Rig
    size : float
        Callback takes a rig which reference size was changed and a new size value.
    """

    descType = c.EventTypes.RIG_REFERENCE_SIZE_CHANGED
    descUsername = 'Rig Reference Size Changed'


class EventRigDropped(Event):
    """ Event sent after rig was dropped (loaded) into the scene from existing preset.

    Callback
    --------
    rig : Rig
        Callback takes the rig that was dropped.
    """

    descType = c.EventTypes.RIG_DROPPED
    descUsername = 'Rig Dropped'


class EventRigNameChanged(Event):
    """ Event sent after rig name was changed.

    Callback
    --------
    rig : Rig
        Callback takes the rig which name was changed.

    oldName : str

    newName : str
    """

    descType = c.EventTypes.RIG_NAME_CHANGED
    descUsername = 'Rig Name Changed'


class EventRigStandardizePre(Event):
    """ Event sent right before rig gets standardized.

    Callback
    --------
    rig : Rig
        Callback takes the rig that will be standardized.
    """

    descType = c.EventTypes.RIG_STANDARDIZE_PRE
    descUsername = 'Rig Standardize Pre'
