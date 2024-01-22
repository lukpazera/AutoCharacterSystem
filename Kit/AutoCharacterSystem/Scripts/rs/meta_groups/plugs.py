

import modo

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..log import log
from ..items.plug import PlugItem


class PlugsMetaGroup(MetaGroup):
    
    descIdentifier = MetaGroupType.PLUGS
    descUsername = 'Plugs'
    descModoGroupType = '' # for standard group
    
    def onItemAdded(self, modoItem):
        try:
            plug = PlugItem(modoItem)
        except TypeError:
            return

        self.modoGroupItem.addItems(modoItem)

