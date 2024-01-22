

from ..element_set import ElementSetFromMetaGroupItems
from ..const import MetaGroupType
from ..const import ElementSetType


class BindSkeletonElementSet(ElementSetFromMetaGroupItems):
    
    descIdentifier = ElementSetType.BIND_SKELETON
    descUsername = 'Bind Skeleton'
    descMetaGroupIdentifier = MetaGroupType.BIND_LOCATORS