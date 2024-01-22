

import modo

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..log import log
from ..item_features.controller import ControllerItemFeature as Controller


class ControllersMetaGroup(MetaGroup):
    
    descIdentifier = MetaGroupType.CONTROLLERS
    descUsername = 'Controllers'
    descModoGroupType = '' # for standard group
    
    def onItemAdded(self, modoItem):
        try:
            ctrl = Controller(modoItem)
        except TypeError:
            return

        self.modoGroupItem.addItems(modoItem)

    def onItemChanged(self, modoItem):
        """ Called when some aspect of an item has changed.
        
        In this case we do not need to preserve anything so this will simply
        readd the item.
        """
        try:
            ctrl = Controller(modoItem)
        except TypeError:
            self.modoGroupItem.removeItems(modoItem)
            return

        self.modoGroupItem.addItems(modoItem)
