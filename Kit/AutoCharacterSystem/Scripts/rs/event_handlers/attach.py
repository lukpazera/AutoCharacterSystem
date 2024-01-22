
""" Event handler that handles updates to rig attachments.
"""


import modo

from ..event_handler import EventHandler
from ..const import EventTypes as e
from ..log import log
from ..attach_op import AttachOperator


class AttachmentsEventHandler(EventHandler):
    """ Handles events that require attachment sets to be updated.
    """

    descIdentifier = 'attach'
    descUsername = 'Attachments'
  
    @property
    def eventCallbacks(self):
        return {e.GUIDE_APPLY_INIT: self.event_guideApplyInit,
                e.GUIDE_APPLY_PRE: self.event_guideApplyPre,
                e.GUIDE_APPLY_POST: self.event_guideApplyPost}

    def event_guideApplyInit(self, **kwargs):
        """ Called in the beginning of the guide application process.
        """
        try:
            rig = kwargs['rig']
        except KeyError:
            return

        try:
            attachments = AttachOperator(rig)
        except TypeError:
            return

        self._allLinks = []
        for attset in attachments.sets:
            self._allLinks.extend(attset.transformLinks)
            
    def event_guideApplyPre(self, **kwargs):
        for xfrmLink in self._allLinks:
            xfrmLink.deactivate()

    def event_guideApplyPost(self, **kwargs):
        for xfrmLink in self._allLinks:
            xfrmLink.updateRestPose()
            
        for xfrmLink in self._allLinks:
            xfrmLink.reactivate()
        
        del self._allLinks

    # -------- Private methods