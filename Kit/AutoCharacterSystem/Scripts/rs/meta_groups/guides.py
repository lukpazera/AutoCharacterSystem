

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..log import log
from ..items.guide import GuideItem


class GuidesMetaGroup(MetaGroup):
    
    descIdentifier = MetaGroupType.GUIDES
    descUsername = 'Guides'
    descModoGroupType = '' # for standard group
    
    def onItemAdded(self, modoItem):
        try:
            guide = GuideItem(modoItem)
        except TypeError:
            return
        self.modoGroupItem.addItems(modoItem)
