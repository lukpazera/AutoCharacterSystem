
import lx
import modo
import modox

from ..xfrm_link_setup import TransformLinkSetup
from ..const import TransformLinkType as t
from ..log import log
from ..item import Item


class WorldTransformPermanentLinkSetup(TransformLinkSetup):
    """
    """
    # -------- Attribute channels

    descIdentifier = t.WORLD_POS_PERMANENT
    descUsername = 'World Position'

    # -------- Public methods

    def onNew(self, compensation=True):
        # simply link world position of target item to source item.
        wposFromChan = modox.LocatorUtils.getItemWorldPositionMatrixChannel(self.modoItem)
        wposTargetChan = modox.LocatorUtils.getItemWorldPositionMatrixChannel(self.targetModoItem)
        wposTargetChan >> wposFromChan

        wrotFromChan = modox.LocatorUtils.getItemWorldRotationMatrixChannel(self.modoItem)
        wrotTargetChan = modox.LocatorUtils.getItemWorldRotationMatrixChannel(self.targetModoItem)
        wrotTargetChan >> wrotFromChan

    def onRemove(self):
        wposFromChan = modox.LocatorUtils.getItemWorldPositionMatrixChannel(self.modoItem)
        wposTargetChan = modox.LocatorUtils.getItemWorldPositionMatrixChannel(self.targetModoItem)
        wposTargetChan << wposFromChan

        wrotFromChan = modox.LocatorUtils.getItemWorldRotationMatrixChannel(self.modoItem)
        wrotTargetChan = modox.LocatorUtils.getItemWorldRotationMatrixChannel(self.targetModoItem)
        wrotTargetChan << wrotFromChan
