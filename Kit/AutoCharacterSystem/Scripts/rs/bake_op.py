

import lx
import modo
import modox
from modox import TimeUtils
from modox import Monitor

from . import const as c
from .bind_skel_shadow import BindSkeletonShadow
from .items.bind_mesh import BindMeshItem
from .items.rigid_mesh import RigidMeshItem
from .items.bind_proxy import BindProxyItem
from .bind_meshes_op import BindMeshesOperator

from .item_utils import  ItemUtils
from .deform_stack import DeformStack
from .component_setup import ComponentSetup
from .log import log


class BakeActionChoice(object):
    NONE = 0
    ALL = 1
    CURRENT = 2


class BakeDescription(object):
    """
    Describes what kind of data will be baked.

    Attributes
    ----------
    actorName : str, None
        Set explicit baked actor name or None for using default name.
    """
    actions = BakeActionChoice.ALL
    meshes = True
    actorName = None
    unlinkSource = False


class BakeOperator(object):
    """ Bakes bind skeleton shadow.
    
    Parameters
    ----------
    bindSkeletonShadow : BindSkeletonShadow
        Bake operator works off bind skeleton shadow object.

    Raises
    ------
    TypeError
        When wrong type of item was passed to initialise.
    """

    ActionChoice = BakeActionChoice

    def bake(self, bakeDescription, monitor=None, monitorTicks=0.0):
        """ Bakes a set of actions on the bind skeleton shadow.
        
        Parameters
        ----------
        actions : list of modo.ActionClip
            When list is not set all rig actor actions are baked.
        """
        setup = modox.SetupMode()
        setup.store()

        bakeTicks = monitorTicks * 0.8
        meshTicks = monitorTicks * 0.1 # this is used twice, for rigid and proxy meshes

        setup.state = True

        self._bindSkelShadow.applyRestPose()
        self._targetActor = self._bindSkelShadow.addActor()
        self._renameActors(bakeDescription.actorName)
        self._renameSkeletonRoot()

        if bakeDescription.meshes:
            self._mergeRigidMeshes(monitor, meshTicks)
            self._mergeBindProxies(monitor, meshTicks)
            self._bakeBindMeshes()
            self._bindSkelShadow.moveDeformerConnections()
            self._extractDeformersStack()

        setup.state = False
        self._bakeAnimation(bakeDescription.actions, monitor, bakeTicks)

        if bakeDescription.unlinkSource:
            self._bindSkelShadow.unlinkFromSource()

        setup.restore()

    # -------- Private methods

    def _bakeAnimation(self, actionsChoice, monitor=None, monitorTicks=0.0):
        # If user chose not to bake actions, just leave early
        if actionsChoice == self.ActionChoice.NONE:
            if monitor is not None:
                monitor.tick(monitorTicks)
            return

        actions = []
        if actionsChoice == self.ActionChoice.ALL:
            actions = self._sourceActor.actions
        elif actionsChoice == self.ActionChoice.CURRENT:
            curAction = self._sourceActor.currentAction
            if curAction is not None:
                actions = [curAction]
            else:
                pass
        else:
            actions = []

        # Bail out if no actions to bake.
        # Remember about ticking monitor.
        if not actions:
            if monitor is not None:
                monitor.tick(monitorTicks)
            return

        frameRangeChannels = self._bindSkelShadow.rig.metaRig.getGroup(c.MetaGroupType.ACTOR).allAnimationChannels
        if not frameRangeChannels:
            log.out('Empty rig actor. Nothing to bake.', log.MSG_ERROR)
            if monitor is not None:
                monitor.tick(monitorTicks)
            return

        if monitor is not None:
            step = monitorTicks / float(len(actions))

        for sourceAction in actions:
            if monitor is not None:
                monitor.tick(step)

            targetActionName = sourceAction.name
            sourceAction.name += "_src"
            targetAction = self._targetActor.addAction(targetActionName)

            # Make sure to make actors and actions current.
            lx.eval('group.current {%s} actr' % self._sourceActor.id)
            lx.eval('layer.active {%s} type:actr' % sourceAction.id)

            lx.eval('group.current {%s} actr' % self._targetActor.id)
            lx.eval('layer.active {%s} type:actr' % targetAction.id)

            # Bake only 2 frames if no animation is found.
            try:
                frameStart, frameEnd = TimeUtils.getChannelsFrameRange(frameRangeChannels, sourceAction.name)
            except LookupError:
                frameStart = 0
                frameEnd = 1
            except ValueError:
                frameStart = 0
                frameEnd = 1

            for rootModoItem in self._bindSkelShadow.hierarchyRootModoItems:
                lx.eval('item.bake frameS:%d frameE:%d remConstraints:false hierarchy:true item:{%s}' % (frameStart, frameEnd, rootModoItem.id))

    def _renameSkeletonRoot(self):
        self._bindSkelShadow.skeletonRoot.name = self._bindSkelShadow.rig.name

    def _renameActors(self, bakedActorName=None):
        if bakedActorName is None:
            targetActorName = self._sourceActor.name
        else:
            targetActorName = bakedActorName

        self._sourceActor.name += "_src"
        self._targetActor.name = targetActorName

    def _bakeBindMeshes(self):
        bindMeshes = self._bindSkelShadow.rig[c.ElementSetType.RESOLUTION_BIND_MESHES].elements
        for modoItem in bindMeshes:
            try:
                bmesh = BindMeshItem(modoItem)
            except TypeError:
                continue
            ItemUtils.standardize(bmesh)
            setup = ComponentSetup.getSetupFromModoItem(modoItem)
            setup.removeItem(modoItem)
            modoItem.setParent(self._bindSkelShadow.skeletonRoot)

    def _mergeRigidMeshes(self, monitor=None, monitorTicks=1):
        rigidMeshes = self._bindSkelShadow.rig[c.ElementSetType.RESOLUTION_RIGID_MESHES].elements
        if not rigidMeshes:
            if monitor is not None:
                monitor.tick(monitorTicks)
            return

        if monitor is not None:
            singleMeshTick = float(monitorTicks) / len(rigidMeshes)

        # Merging rigid meshes into first available bind mesh
        # We should be creating bind mesh if there isn't any.
        bindMeshes = self._bindSkelShadow.rig[c.ElementSetType.RESOLUTION_BIND_MESHES].elements
        if len(bindMeshes) > 0:
            bindMesh = BindMeshItem(bindMeshes[0])
        else:
            bindMeshesOp = BindMeshesOperator(self._bindSkelShadow.rig.rootItem)
            bindMesh = bindMeshesOp.addEmptyBindMesh('Rigid Meshes')

        bindMeshesOp = BindMeshesOperator(self._bindSkelShadow.rig.rootItem)

        for modoItem in rigidMeshes:

            if monitor is not None:
                monitor.tick(singleMeshTick)

            try:
                rmesh = RigidMeshItem(modoItem)
            except TypeError:
                continue
            bindMeshesOp.mergeRigidOrProxyMesh(rmesh, bindMesh)

    def _mergeBindProxies(self, monitor=None, monitorTicks=1):
        proxyMeshes = self._bindSkelShadow.rig[c.ElementSetType.RESOLUTION_BIND_PROXIES].elements
        if not proxyMeshes:
            if monitor is not None:
                monitor.tick(monitorTicks)
            return

        if monitor is not None:
            singleMeshTick = float(monitorTicks) / len(proxyMeshes)

        bindMeshesOp = BindMeshesOperator(self._bindSkelShadow.rig.rootItem)
        bindMesh = bindMeshesOp.addEmptyBindMesh('Bind Proxies')
        for modoItem in proxyMeshes:

            if monitor is not None:
                monitor.tick(singleMeshTick)

            try:
                proxyMesh = BindProxyItem(modoItem)
            except TypeError:
                continue
            bindMeshesOp.mergeRigidOrProxyMesh(proxyMesh, bindMesh)

    def _extractDeformersStack(self):
        """
        Extracts all deformers from the rig so they won't get deleted with the rig.
        """
        deformStack = DeformStack(self._bindSkelShadow.rig.rootItem)
        tree = deformStack.modoItems
        for modoItem in tree:
            setup = ComponentSetup.getSetupFromModoItem(modoItem)
            if setup is not None:
                setup.clearItem(modoItem)

    def __init__(self, bindSkeletonShadow):
        try:
            skeletonType = bindSkeletonShadow.skeletonType
        except AttributeError:
            raise TypeError
        if skeletonType == BindSkeletonShadow.Type.SETUP:
            raise TypeError
        
        self._bindSkelShadow = bindSkeletonShadow
        self._sourceActor = self._bindSkelShadow.rig.actor
        self._targetActor = None