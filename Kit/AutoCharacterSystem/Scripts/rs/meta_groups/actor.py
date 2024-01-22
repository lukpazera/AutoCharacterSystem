

import modo
import modox

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..log import log
from ..item_features.controller import ControllerItemFeature as Controller


class ActorMetaGroup(MetaGroup):
    
    descIdentifier = MetaGroupType.ACTOR
    descUsername = 'Actor'
    descModoGroupType = 'actor'

    def onItemAdded(self, modoItem):
        try:
            ctrl = Controller(modoItem)
        except TypeError:
            return

        if ctrl.addItemToActor:
            self.addItems(ctrl.modoItem)
        self.addChannelsToGroup(ctrl.actorChannels)

    def onItemChanged(self, modoItem):
        try:
            ctrl = Controller(modoItem)
        except TypeError:
            self.onItemRemoved(modoItem)
            return

        if ctrl.addItemToActor:
            self.addItems(ctrl.modoItem)
        else:
            self.removeItemFromGroup(modoItem)

        self.updateChannelsForItem(modoItem, ctrl.actorChannels)
    
    def onItemRemoved(self, modoItem):
        """ Called when item was removed from rig.
        
        This implementation overrides default implementation of this method.
        """
        self.removeItemFromGroup(modoItem)
        self.removeItemChannelsFromGroup(modoItem)

    @property
    def allAnimationChannels(self):
        """
        Gets all the animation channels for an actor.

        This includes channels added explicitly and all animated channels that are enabled on controllers
        added as items to the actor.

        Returns
        -------
        [modo.Channel]
        """
        chans = self.modoGroupItem.groupChannels
        items = self.modoGroupItem.items
        for item in items:
            try:
                ctrl = Controller(item)
            except TypeError:
                continue
            chans.extend(ctrl.animatedChannels)
        return chans
