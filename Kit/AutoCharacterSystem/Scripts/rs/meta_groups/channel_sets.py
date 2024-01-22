

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..log import log


class ChannelSetsMetaGroup(MetaGroup):
    """ This group is a parent to all channel sets in the rig.
    """
    
    descIdentifier = MetaGroupType.CHANNEL_SETS
    descUsername = 'ChannelSets'
    descModoGroupType = '' # for standard group
    descDeleteWithChildren = True  # When deleting the group take all channel sets with you.