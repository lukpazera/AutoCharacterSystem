
""" Series of events sent by the guide.
"""


from ..event import Event
from .. import const as c


class EventGuideApplyInit(Event):
    """ Event sent one time at the beginning of the guide application process.
    
    Callback
    --------
    rig : Rig
        Callback takes single argument, a rig to which the guide is about
        to be applied.
    """
    
    descType = c.EventTypes.GUIDE_APPLY_INIT
    descUsername = 'Guide Apply Initialisation'
    

class EventGuideApplyItemScan(Event):
    """ Event sent during guide apply initialisation process.
    
    Event is sent separately for each item in rig's hierarchy.
    Clients should perform any preparatory actions on items
    or cache any data that they'll need at subsequent steps of
    guide application process.
    
    Callback
    --------
    item : Item
        Callback takes single argument, a rig item that should be scanned/
        prepared.
    """
    
    descType = c.EventTypes.GUIDE_APPLY_ITEM_SCAN
    descUsername = 'Guide Apply Item Scan'


class EventGuideApplyPre(Event):
    """ Event sent after item scanning but before applying guide to rig.
    
    Event is sent once after all items are scanned.
    
    Callback
    --------
    Callback takes no arguments, all data should be cached during
    prior event calls in the chain.
    """
    
    descType = c.EventTypes.GUIDE_APPLY_PRE
    descUsername = 'Guide Apply Pre'


class EventGuideApplyPost(Event):
    """ Event sent after guide was applied to rig.
    
    Event is sent once at the end of guide application process.
    Typically, this should revert any temporary changes back so
    the rig is in the same state as it was prior to applying guide.
    
    Callback
    --------
    rig : Rig
        Callback takes single argument, a rig to which the guide was applied.
    """
    
    descType = c.EventTypes.GUIDE_APPLY_POST
    descUsername = 'Guide Apply Post'


class EventGuideApplyPost2(Event):
    """ Event sent after ApplyPost event.

    Use this for applying changes that should happen after the ApplyPost event.

    Callback
    --------
    rig : Rig
        Callback takes single argument, a rig to which the guide was applied.
    """

    descType = c.EventTypes.GUIDE_APPLY_POST2
    descUsername = 'Guide Apply Post 2'


class EventModuleGuideScaled(Event):
    """ Event sent when module guide scale was changed.

    When module guide size was changed some other rig elements may need to be scaled
    accordingly.

    Callback
    --------
    module : Module
    factor : float
        Module that was scaled, factor is by how much the guide was scaled.
    """

    descType = c.EventTypes.GUIDE_APPLY_POST
    descUsername = 'Guide Apply Post'


class EventGuideLinkChanged(Event):
    """ Event sent when a guide was either linked to or unlinked from another guide.

    Callback
    --------
    guide : GuideItem,
        Callback takes single argument, guide item that was linked or unlinked.
    """

    descType = c.EventTypes.GUIDE_LINK_CHANGED
    descUsername = 'Guide Link Changed'