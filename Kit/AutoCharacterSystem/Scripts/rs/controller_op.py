import modo
import modox.channel_lxe
from .rig import Rig
from .meta_rig import MetaRig
from .item_features.controller import ControllerItemFeature
from .controller_ui import ChannelSet
from .module import Module
from .item import Item
from .items.plug import PlugItem
from .items.socket import SocketItem
from .log import log
from . import const as c


class ControllerOperator(object):

    @classmethod
    def isControllerInCharacterSpace(cls, ctrl):
        """
        Tests if controller is in character space.

        1. Checks dynamic parenting link and where it leads.

        2. If there's no dynamic parent link checks direct parent, if it's a plug check its socket.
           If socket belongs to the base module we're in character space.

        3. If parent is not plug we check its world rotation input. It could be space locator.
           If world rotation input leads to plug that connects to base - we're in character space.

        Returns
        -------
        bool
        """
        directParent = ctrl.modoItem.parent
        if directParent is None:
            return False

        try:
            rigItem = Item.getFromModoItem(directParent)
        except TypeError:
            return False

        if isinstance(rigItem, PlugItem):
            return cls._checkPlugForWorldSpace(rigItem)
        else:
            worldRotChannel = modox.LocatorUtils.getItemWorldRotationMatrixChannel(directParent)
            if worldRotChannel.revCount == 0:
                return False
            inputChannel = worldRotChannel.reverse(0)
            try:
                rigItem = Item.getFromModoItem(inputChannel.item)
            except TypeError:
                return False

            if isinstance(rigItem, PlugItem):
                return cls._checkPlugForWorldSpace(rigItem)

        return False

    @classmethod
    def _checkPlugForWorldSpace(self, rigItem):
        socket = rigItem.socket
        if socket is None:
            return False

        socketModuleRoot = socket.moduleRootItem
        if not socketModuleRoot:
            return False

        socketModule = Module(socketModuleRoot)
        if socketModule.identifier == c.ModuleIdentifier.BASE:
            return True
        return False

    def createAllChannelSets(self, makeIndependent=False):
        """
        Creates all channels sets that should be included with rig.

        Parameters
        ----------
        makeIndependent : bool
            When True channel sets will be freed from the rig meaning
            a collection of independent channel sets is created.
            This is useful for standardizing the rig - channel sets are freed from the rig
            so they don't get removed when controller feature is removed from rig item.
        """
        for ctrlModoItem in self._rig.getElements(c.ElementSetType.CONTROLLERS):
            try:
                ctrl = ControllerItemFeature(ctrlModoItem)
            except TypeError:
                continue
            # It's enough to query for channel set and it'll get created
            # when controller is set to channels and the set hasn't been created yet.
            try:
                chanSet = ctrl.channelSet
            except LookupError:
                chanSet = None

            if chanSet is not None and makeIndependent:
                chanSet.freeFromRig()

    def createModuleChannelSets(self, module):
        for ctrlModoItem in module.getElementsFromSet(c.ElementSetType.CONTROLLERS):
            try:
                ctrl = ControllerItemFeature(ctrlModoItem)
            except TypeError:
                continue
            # It's enough to query for channel set and it'll get created
            # when controller is set to channels and the set hasn't been created yet.
            try:
                ctrl.channelSet
            except LookupError:
                pass

    def updateModuleChannelSetNames(self, module):
        for ctrlModoItem in module.getElementsFromSet(c.ElementSetType.CONTROLLERS):
            try:
                ctrl = ControllerItemFeature(ctrlModoItem)
            except TypeError:
                continue
            ctrl.updateChannelSetName()

    def deleteModuleChannelSets(self, module):
        for ctrlModoItem in module.getElementsFromSet(c.ElementSetType.CONTROLLERS):
            try:
                ctrl = ControllerItemFeature(ctrlModoItem)
            except TypeError:
                continue
            # It's enough to query for channel set and it'll get created
            # when controller is set to channels and the set hasn't been created yet
            try:
                chanSet = ctrl.channelSet
            except LookupError:
                continue
            chanSet.selfDelete()

    def updateAllChannelSetNames(self):
        """
        Updates names for all channel sets belonging to the rig.
        """
        for ctrlModoItem in self._rig.getElements(c.ElementSetType.CONTROLLERS):
            try:
                ctrl = ControllerItemFeature(ctrlModoItem)
            except TypeError:
                continue
            ctrl.updateChannelSetName()

    def purgeChannelsSets(self):
        """
        Deletes channel sets that are part of meta rig but are not connected to any controllers.
        """
        metaRig = self._rig.metaRig
        chanSetGroup = metaRig.getGroup(c.MetaGroupType.CHANNEL_SETS)
        for chanSetModoItem in chanSetGroup.childGroups:
            ChannelSet.removeIfFree(chanSetModoItem)

    # -------- Private methods

    def __init__(self, rigInitializer):
        if isinstance(rigInitializer, Rig):
            self._rig = rigInitializer
        else:
            try:
                self._rig = Rig(rigInitializer)
            except TypeError:
                raise
