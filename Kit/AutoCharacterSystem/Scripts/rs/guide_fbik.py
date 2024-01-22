

import lx
import modo
from modox import FBIKChainItem
from modox import FBIKSolver

from .item_features.guide import GuideItemFeature
from .item_features.controller import ControllerItemFeature
from .log import log


class GuideFullBodyIK(object):
    """ Adds support for using FBIK with ACS rigs.
    
    This class presents a set of methods that need to be called
    in right order during guide application process.
    The methods will make sure that IK is properly disabled for
    guide application, its settings are updated and then IK
    is enabled again.
    """
    
    def scanItem(self, modoItem):
        """ Caches FBIK items for later use.
        
        This needs to be called for every item in the rig.
        
        Parameters
        ----------
        modoItem : modo.Item
        """
        if self._testChainItem(modoItem):
            return
        self._testSolverItem(modoItem)
    
    def disable(self):
        """ Disables all fbik solvers by setting their blending to 0%.
        """
        for solver in self._ikSolvers:
            solver.backupSetupBlend()
            solver.enabled = False

    def reenable(self):
        """ Reenables FBIK by reverting solvers blending to value prior to calling disable().
        """
        for solver in self._ikSolvers:
            solver.restoreSetupBlend()

    def updateChainsRestPoses(self):
        for ikitem in self._ikChainItems:
            ikitem.updateRestPose()
            
    def post(self):
        """ Call when matching is complete.
        """
        self._cleanUp()

    # -------- Private methods

    def _testSolverItem(self, modoItem):
        if modoItem.type == 'ikFullBody':
            self._ikSolvers.append(FBIKSolver(modoItem))
            return True
        return False
            
    def _testChainItem(self, modoItem):
        try:
            ikitem = FBIKChainItem(modoItem)
        except TypeError:
            return False
        log.out('found ik chain item %s' % modoItem.name)
        self._ikChainItems.append(ikitem)
        return True

    def _cleanUp(self):
        del self._ikChainItems
        del self._ikSolvers
        
    def _initData(self):
        self._ikChainItems = []
        self._ikSolvers = []

    def __init__(self):
        self._initData()
