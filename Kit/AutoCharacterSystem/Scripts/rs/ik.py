

import lx
import modo
import modox

from modox import IK23BarSolver
from modox import IK23BarSetup
from .item_features.guide import GuideItemFeature
from .item_features.controller import ControllerItemFeature
from .log import log


class IK23Bar(object):
    """ Adds support for using standard IK (new in 13.2) with ACS rigs.
    
    This class presents a set of methods that need to be called
    in right order during guide application process.
    The methods will make sure that IK is properly disabled for
    guide application, its settings are updated and then IK
    is enabled again.
    """
    
    def scanItem(self, modoItem):
        """ Caches IK items for later use.
        
        This needs to be called for every item in the rig.
        We need to cache solver modifier and goal item.
        
        Parameters
        ----------
        modoItem : modo.Item
        """
        self._testSolverItem(modoItem)
    
    def disable(self):
        """ Disables all fbik solvers by setting their blending to 0%.
        """
        modoVer = lx.service.Platform().AppVersion()
        if modoVer >= 1410:
            modox.IKUtils.disableIK()
        else:
            for solver in self._ikSolvers:
                solver.backupSetupBlend()
                solver.enabled = False

    def reenable(self):
        """ Reenables FBIK by reverting solvers blending to value prior to calling disable().
        """
        modoVer = lx.service.Platform().AppVersion()
        if modoVer >= 1410:
            modox.IKUtils.enableIK()
        else:
            for solver in self._ikSolvers:
                solver.restoreSetupBlend()

    def updateRestPose(self):
        for solver in self._ikSolvers:
            solver.resetFromFK()
            modoVer = lx.service.Platform().AppVersion()
            if modoVer < 1400:
                self._fix3barIK(solver)

    def post(self):
        """ Call when matching is complete.
        """
        self._cleanUp()

    # -------- Private methods

    def _fix3barIK(self, solver):
        """ Applies a workaround to reset 3 bar solver from FK properly.
        
        Use it until it's fixed in MODO.
        """
        # This is workaround for 3 bar ik.
        # 2 bar ik is fine.
        iksetup = IK23BarSetup(solver)
        if iksetup.type == IK23BarSetup.Type.BAR2:
            return
        chainItems = iksetup.chain
        hrch = modox.ItemUtils.duplicateItemsAsHierarchy(chainItems, 'locator')
        tempSetup = IK23BarSetup.apply(hrch)
        angleBias = tempSetup.solver.setupAngleBias
        iksetup.solver.setupAngleBias = angleBias
        tempSetup.selfDelete()

    def _testSolverItem(self, modoItem):
        try:
            self._ikSolvers.append(IK23BarSolver(modoItem))
            return True
        except TypeError:
            pass
        return False

    def _cleanUp(self):
        del self._ikGoals
        del self._ikSolvers
        
    def _initData(self):
        self._ikGoals = []
        self._ikSolvers = []

    def __init__(self):
        self._initData()
