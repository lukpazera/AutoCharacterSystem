""" Space switcher item.

    Space switcher item is base don dynamic parent modifier
    and is used for dynamically switching space of a controller
    to which it is attached.
"""

import lx
import modo
from modox import ItemUtils

from .. import item
from .. import const as c


class SpaceSwitcherItem(item.Item):

    descType = c.RigItemType.SPACE_SWITCHER
    descUsername = 'Space Switcher'
    descModoItemType = 'cmDynamicParent'
    descFixedModoItemType = True
    descDefaultName = 'SpaceSwitcher'
    descPackages = ['rs.pkg.generic', 'rs.pkg.dynaParent']
    descItemCommand = None
    descDropScriptSource = None
    descDropScriptDestination = None

    def onAdd(self, subtype):
        # Enable drawing when item is selected only.
        self.setChannelProperty('draw', 2)
