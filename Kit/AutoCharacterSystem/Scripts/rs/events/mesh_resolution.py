

from ..event import Event
from .. import const as c


class EventMeshResolutionRenamed(Event):
    """ Event to send when a name of mesh resolution was changed.
    
    Callback
    --------
    rigRoot : RootItem
    name : str
    newName : str
        Callback takes 3 arguments, a name of resolution that was changed
        and a new name for this resolution.
    """
    
    descType = c.EventTypes.MESH_RES_RENAMED
    descUsername = 'Mesh Resolution Renamed'


class EventMeshResolutionRemoved(Event):
    """ Event to send when a mesh resolution was removed.
    
    Callback
    --------
    rigRoot : RootItem
    name : str
        Callback takes 2 arguments, a name of resolution that was removed.
    """
    
    descType = c.EventTypes.MESH_RES_REMOVED
    descUsername = 'Mesh Resolution Removed'