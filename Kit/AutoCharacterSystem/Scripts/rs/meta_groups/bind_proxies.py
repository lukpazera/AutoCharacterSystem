

import modo

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..items.bind_proxy import BindProxyItem
from ..log import log


class BindProxiesMetaGroup(MetaGroup):
    
    descIdentifier = MetaGroupType.BIND_PROXIES
    descUsername = 'Bind Proxy Meshes'
    descModoGroupType = '' # for standard group
    
    def onItemAdded(self, modoItem):
        try:
            rigidMesh = BindProxyItem(modoItem)
        except TypeError:
            return

        self.modoGroupItem.addItems(modoItem)

