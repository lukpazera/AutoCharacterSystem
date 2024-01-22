

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..log import log
from ..items.bind_loc import BindLocatorItem


class BindLocatorsMetaGroup(MetaGroup):
    
    descIdentifier = MetaGroupType.BIND_LOCATORS
    descUsername = 'BindLocators'
    descModoGroupType = '' # for standard group
    
    def onItemAdded(self, modoItem):
        try:
            bindLoc = BindLocatorItem(modoItem)
        except TypeError:
            return
        self.modoGroupItem.addItems(modoItem)