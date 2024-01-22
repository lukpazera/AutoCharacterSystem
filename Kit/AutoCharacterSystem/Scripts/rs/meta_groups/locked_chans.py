

import modo

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..const import TriState
from ..log import log
from ..item_features.controller import ControllerItemFeature as Controller
from ..item_features.controller_guide import ControllerGuideItemFeature as ControllerGuide


class LockedChannelsMetaGroup(MetaGroup):
    
    descIdentifier = MetaGroupType.LOCKED_CHANNELS
    descUsername = 'LockedChannels'
    descModoGroupType = '' # for standard group
    descLockedDefault = TriState.ON

    def onItemAdded (self, modoItem):
        try:
            ctrl = self._testItem(modoItem)
        except TypeError:
            return
        
        self.addChannelsToGroup(ctrl.lockedChannels)

    def onItemChanged(self, modoItem):
        try:
            ctrl = self._testItem(modoItem)
        except TypeError:
            return

        self.updateChannelsForItem(modoItem, ctrl.lockedChannels)

    def onItemRemoved(self, modoItem):
        self.removeItemChannelsFromGroup(modoItem)

    # -------- Private methods

    def _testItem(self, modoItem):
        """ Tests item to see if it's a valid item to query for locked channels.
        
        Returns
        -------
        Controller
            Item converted to controller interface or None.
        
        Raises
        ------
        TypeError
            When modoItem is not a controller.
        """
        for ctrlClass in [Controller, ControllerGuide]:
            try:
                return ctrlClass(modoItem)
            except TypeError:
                pass
        raise TypeError