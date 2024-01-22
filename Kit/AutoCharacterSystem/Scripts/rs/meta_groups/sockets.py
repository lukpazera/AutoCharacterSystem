

import modo

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..log import log
from ..items.socket import SocketItem


class SocketsMetaGroup(MetaGroup):
    
    descIdentifier = MetaGroupType.SOCKETS
    descUsername = 'Sockets'
    descModoGroupType = '' # for standard group
    
    def onItemAdded(self, modoItem):
        try:
            socket = SocketItem(modoItem)
        except TypeError:
            return

        self.modoGroupItem.addItems(modoItem)

