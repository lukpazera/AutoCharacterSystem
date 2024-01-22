

from ..element_set import ElementSetFromMetaGroupItems
from ..const import MetaGroupType
from ..const import ElementSetType


class PlugsElementSet(ElementSetFromMetaGroupItems):
    
    descIdentifier = ElementSetType.PLUGS
    descUsername = 'Plugs'
    descMetaGroupIdentifier = MetaGroupType.PLUGS


class SocketsElementSet(ElementSetFromMetaGroupItems):
    
    descIdentifier = ElementSetType.SOCKETS
    descUsername = 'Sockets'
    descMetaGroupIdentifier = MetaGroupType.SOCKETS