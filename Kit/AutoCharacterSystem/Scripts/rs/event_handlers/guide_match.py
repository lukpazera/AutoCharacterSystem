
""" Event handler that is matching items to their guides.
"""


import modo

from ..event_handler import EventHandler
from ..const import EventTypes as e
from ..log import log
from ..guide_match import GuideMatcher
from ..guide_fbik import GuideFullBodyIK
from ..ik import IK23Bar
from ..guide_symmetry import GuideSymmetry


class MatchToGuideEventHandler(EventHandler):
    """ Handles matching items to their guides during guide application events.
    """

    descIdentifier = 'guidematch'
    descUsername = 'Match to Guide'
  
    @property
    def eventCallbacks(self):
        return {e.GUIDE_APPLY_INIT: self.event_guideApplyInit,
                e.GUIDE_APPLY_ITEM_SCAN: self.event_guideApplyItemScan,
                e.GUIDE_APPLY_PRE: self.event_guideApplyPre,
                e.GUIDE_APPLY_DO: self.event_guideApplyDo,
                e.GUIDE_APPLY_POST: self.event_guideApplyPost}

    def event_guideApplyInit(self, **kwargs):
        """ Called in the beginning of the guide application process.
        """
        try:
            rig = kwargs['rig']
        except KeyError:
            return

        self._matcher = GuideMatcher()
        self._fbik = GuideFullBodyIK()
        self._ik23bar = IK23Bar()
        self._symmtery = GuideSymmetry()
    
    def event_guideApplyItemScan(self, **kwargs):
        try:
            modoItem = kwargs['item']
        except KeyError:
            return
        
        self._matcher.scanItem(modoItem)
        self._fbik.scanItem(modoItem)
        self._ik23bar.scanItem(modoItem)
        self._symmtery.scanItem(modoItem)

    def event_guideApplyPre(self, **kwargs):
        self._fbik.disable()
        self._ik23bar.disable()
        self._symmtery.applySymmetry()

    def event_guideApplyDo(self, **kwargs):
        self._matcher.match()

    def event_guideApplyPost(self, **kwargs):
        self._matcher.post()
        self._fbik.updateChainsRestPoses()
        self._fbik.reenable()
        self._ik23bar.updateRestPose()
        self._ik23bar.reenable()

    # -------- Private methods