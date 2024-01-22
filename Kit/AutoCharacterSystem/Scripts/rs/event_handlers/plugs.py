
""" Event handler that handles updates to plugs.
"""


import modo
import modox

from ..event_handler import EventHandler
from ..const import EventTypes as e
from ..log import log
from ..items.plug import PlugItem
from ..xfrm_link import TransformLink


class PlugsEventHandler(EventHandler):

    descIdentifier = 'plugs'
    descUsername = 'Plugs'
  
    @property
    def eventCallbacks(self):
        return {e.GUIDE_APPLY_INIT: self.event_GuideApplyInit,
                e.GUIDE_APPLY_ITEM_SCAN: self.event_guideApplyItemScan,
                e.GUIDE_APPLY_PRE: self.event_guideApplyPre,
                e.GUIDE_APPLY_POST: self.event_guideApplyPost}

    def event_GuideApplyInit(self, **kwargs):
        self._allLinks = []
        self._allPlugs = []

    def event_guideApplyItemScan(self, **kwargs):
        try:
            modoItem = kwargs['item']
        except KeyError:
            return

        try:
            plug = PlugItem(modoItem)
        except TypeError:
            return

        self._allPlugs.append(plug)

        try:
            xfrmLink = TransformLink(modoItem)
        except TypeError:
            return
        
        self._allLinks.append(xfrmLink)
            
    def event_guideApplyPre(self, **kwargs):
        for xfrmLink in self._allLinks:
            xfrmLink.deactivate()

    def event_guideApplyPost(self, **kwargs):
        for xfrmLink in self._allLinks:
            xfrmLink.updateRestPose()

        for xfrmLink in self._allLinks:
            xfrmLink.reactivate()

        # It's CRUCIAL to store the offset after
        # all plugs dynamic parenting is reactivated.
        for plug in self._allPlugs:
            plug.cacheParentTransformOffset()

        del self._allLinks
        del self._allPlugs

    # -------- Private methods
