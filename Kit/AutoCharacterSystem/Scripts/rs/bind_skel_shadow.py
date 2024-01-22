

import lx
import modo
import modox

from . import const as c
from .items.bind_loc_shadow import BindLocatorShadow
from .items.bind_loc import BindLocatorItem
from .bind_skel import BindSkeleton
from .log import log
from .util import run
from .module import Module


class BindSkeletonShadowType(object):
    SETUP = 1
    ANIMATED = 2


class BindSkeletonShadowDescription(object):
    """
    Describes properties of the bind skeleton shadow.
    Pass this object to BindSkeletonShadow.build() and according shadow will be built.

    Attributes
    ----------
    shadowType : int
        one of BindSkeletonShadowType

    visible : bool
        When False built shadow hierarchy will be hidden in viewport.
        Default is False.
    """

    username = 'Shadow'
    shadowType = BindSkeletonShadowType.SETUP
    supportStretching = False
    visible = False
    skipHidden = True  # don't add hidden items

    def test(self, bindloc):
        """
        Custom testing needed to determine whether bind locator should be part of
        shadow hierarchy or not.

        This method is called when the shadow skeleton is being built.

        Parameters
        ----------
        bindloc : BindLocatorItem
            Bind locator that needs to be tested.

        Returns
        -------
        bool
        """
        return True

    def getName(self, bindloc):
        """
        This should return the name of the bind skeleton shadow joint

        Parameters
        ----------
        bindloc : BindLocatorItem
            Bind locator that needs to be tested.

        Returns
        -------
        str
        """
        nameTokens = [c.NameToken.MODULE_NAME, c.NameToken.SIDE, c.NameToken.BASE_NAME]
        return bindloc.renderNameFromTokens(nameTokens)


class BindShadowDescription(BindSkeletonShadowDescription):
    username = 'Bind Shadow'
    shadowType = BindSkeletonShadowType.SETUP
    visible = False

    def test(self, bindloc):
        # for bind skeleton we skip non effector joints but only if they are not leaves.
        if not bindloc.isEffector and not bindloc.isLeaf:
            return False
        return True


class BakeShadowDescription(BindSkeletonShadowDescription):
    username = 'Bake Shadow'
    shadowType = BindSkeletonShadowType.ANIMATED
    visible = True

    def test(self, bindloc):
        # for baking we only skip leaves.
        # later this should skip leaves that don't have anything attached!
        if bindloc.isLeaf:
            return False
        return True

    def getName(self, bindloc):
        exportName = bindloc.exportName
        if not exportName:
            exportName = BindSkeletonShadowDescription.getName(self, bindloc)
        return exportName


class RetargetShadowDescription(BindSkeletonShadowDescription):
    username = 'Retarget Shadow'
    shadowType = BindSkeletonShadowType.ANIMATED
    visible = True

    def test(self, bindloc):
        # Retarget skeleton bind locators need to have at least one
        # retargeting tag.
        mitem = bindloc.modoItem
        if mitem.hasTag('BVHN') or mitem.hasTag('BVHA'):
            return True
        return False

    def getName(self, bindloc):
        exportName = bindloc.exportName
        if not exportName:
            exportName = BindSkeletonShadowDescription.getName(self, bindloc)
        return exportName


class BindSkeletonShadow(object):
    """ Bind skeleton shadow is a temporary skeleton created from bind skeleton.
    
    It can be used to obtain a continuous hierarchy that is good for binding command.
    It can also be used for exporting the rig. Animation can be baked onto the shadow,
    the shadow will have its own actor and the rig can safely be deleted in entirety.
    
    Parameters
    ----------
    rig : Rig
    """
    
    Type = BindSkeletonShadowType

    def build(self,
              description=BindSkeletonShadowDescription(),
              monitor=None,
              availableTicks=0):
        """ Builds new bind skeleton shadow hierarchy.
        
        The skeleton type can be static or animated.
        Animated one has all the motion baked into shadow skeleton.

        This involves:
        - building skeleton in the same setup pose as bind skeleton.
        - apply export names to each joint.
        - in animation version:
            - plug each shadow joint to the same driver item as real bind skeleton
            - set up an actor
            - create and bake all the actions
            - remove connections to driving items
        """
        setup = modox.SetupMode()
        setup.store()
        setup.state = True

        if description.visible:
            visible = modox.c.ItemVisible.DEFAULT
        else:
            visible = modox.c.ItemVisible.NO_CHILDREN

        if monitor is not None:            
            steps = 5.0
            tick = float(availableTicks) / steps
    
            monitor.tick(tick)
        
        self._shadowRoot = modo.Scene().addItem('groupLocator', '%s_Skeleton' % self._rig.name)
        self._shadowRoot.channel('visible').set(visible, time=0.0, action=lx.symbol.s_ACTIONLAYER_SETUP)
        
        if monitor is not None:   
            monitor.tick(tick)

        self._buildShadowHierarchy(description)

        if monitor is not None:   
            monitor.tick(tick)
        
        self._matchShadowSkeletonToSource()
        
        if monitor is not None:   
            monitor.tick(tick)
        
        if description.shadowType == self.Type.ANIMATED:
            self._linkShadowTransformsToSource(description.supportStretching)

        setup.restore()
    
        if monitor is not None:   
            monitor.tick(tick)
        
        self._type = description.shadowType

    def moveDeformerConnections(self):
        """ Moves over all deformer connections from source bind skeleton to shadow one.

        Use this ONLY after the shadow is built and only in case you need the shadow
        to affect rig meshes (such as during bake).
        """
        for shadow in self._shadows:
            sourceEff = modox.Effector(shadow.sourceBindLocator.modoItem)
            deformers = sourceEff.deformers
            sourceEff.setDeformers(None)
            targetEff = modox.Effector(shadow.modoItem)
            targetEff.setDeformers(deformers, replace=True)

    def applyRestPose(self):
        """
        Applies pos/rot/scale for all the shadow bind locators.

        This is crucial for the shadow skeleton to have correct rest pose.
        """
        for shadow in self._shadows:
            run('item.apply type:pos item:{%s}' % shadow.modoItem.id)
            run('item.apply type:rot item:{%s}' % shadow.modoItem.id)
            run('item.apply type:scl item:{%s}' % shadow.modoItem.id)

    @property
    def rig(self):
        """ Gets rig this bind skeleton shadow is built for.
        
        Returns
        -------
        Rig
        """
        return self._rig

    @property
    def hierarchyRootModoItems(self):
        """ Gets a list of shadow skeleton root items.
    
        There really should only be one root but in case user
        built some kind of weird rig we need to account for that.
        """
        children = self._shadowRoot.children(recursive=False)
        skeletonRoots = []
        # We need to make sure we only take bind locator shadows into account.
        # Meshes are parented to bind skeleton shadow too.
        for child in children:
            try:
                BindLocatorShadow(child)
            except TypeError:
                continue
            skeletonRoots.append(child)
        return skeletonRoots

    @property
    def skeletonType(self):
        """ Gets what type of the bind skeleton shadow that is.
        
        Returns
        -------
        BindSkeletonShadow.Type.XXX
        """
        return self._type

    @property
    def skeleton(self):
        """ Gets a list of all locators in bind skeleton shadow hierarchy.
        
        Returns
        -------
        list of BindLocatorShadow
        """
        return self._shadows
    
    @property
    def skeletonModoItems(self):
        """ Gets a list of all modo items in bind skeleton shadow hierarchy.
        
        Returns
        -------
        list of modo.Item
        """
        skel = self.skeleton
        return [bindloc.modoItem for bindloc in skel]

    @property
    def skeletonRoot(self):
        """ Gets the root item, which is the folder under which the skeleton is parented.
        
        Returns
        -------
        modo.Item
        """
        return self._shadowRoot

    def addActor(self):
        """ Creates an actor for the bind skeleton shadow.

        Returns
        -------
        modo.Actor
        """
        scene = modo.Scene()
        actorItems = self.skeletonModoItems
        self._actor = scene.addActor('BindSkeletonShadow', items=actorItems, makeActive=False)
        return self._actor

    @property
    def actor(self):
        """ Gets bind skeleton shadow actor, if one was created.
        
        Returns
        -------
        modo.Actor, None
        """
        try:
            return self._actor
        except AttributeError:
            return None

    def delete(self):
        """ Bind skeleton shadow deletes itself.

        Note that if there are weight maps that have names set to reference bind skeleton joints
        these weight maps will also be deleted together with items that they are referencing!!!
        """
        lx.eval('!item.delete child:1 item:{%s}' % self._shadowRoot.id)

    @property
    def bindMeshes(self):
        """
        Gets a list of bind meshes that are part of the bind skeleton shadow.

        All meshes that are directly under the root folder are considered to be bind meshes
        since they won't move by themselves.

        Returns
        -------
        [modo.Item]
        """
        return self.skeletonRoot.childrenByType(modo.c.MESH_TYPE)

    def unlinkFromSource(self):
        """
        Unlinks shadow skeleton from the source one.
        Source skeleton will not drive shadow anymore.
        """
        self._unlinkShadowTransforms()

    # -------- Private methods

    def _buildShadowHierarchy(self, description):
        """ Builds hierarchy of shadow bind locators.
        
        This is unified hierarchy that should link hierarchies from individual modules.

        Parameters
        ----------
        description : BindSkeletonShadowDescription
        """
        self._shadows = []
        shadowsBySourceIdentifiers = {}
        
        bindSkeleton = BindSkeleton(self._rig)
        bindLocators = bindSkeleton.itemsHierarchy # type : BindLocatorItem
        shadowsWithExternalParents = []

        baseModule = self._rig.modules.baseModule
        rootMotionShadow = None

        # The first loop creates all shadows and replicates the hierarchy.
        # It also finds all the shadows that are roots within modules and that will need
        # to be parented to some other shadow eventually to form a single skeleton hierarchy.
        for bindloc in bindLocators:
            # Skip hidden bind locators. We don't want them to be part of the shadow.
            if bindloc.hidden:
                continue
            if not description.test(bindloc):
                continue

            # Create shadow here
            shadow = BindLocatorShadow.newFromBindLocator(bindloc, description.getName(bindloc))
            self._shadows.append(shadow)
            shadowsBySourceIdentifiers[shadow.identifier] = shadow

            # Find root motion if we support stretching.
            # We will need to parent all shadow bind locators to root motion.
            if description.supportStretching and Module(bindloc.moduleRootItem) == baseModule:
                rootMotionShadow = shadow

            if description.supportStretching:
                # With stretching we just need a flat hierarchy so parent every
                # joint to the shadow root for now.
                # If root motion is found we will parent to root motion in the next step.
                shadow.modoItem.setParent(self._shadowRoot, -1)

            else:
                # Now we need to parent new shadow to its correct shadow parent.
                # This only happens if new shadow bind locator has direct parent
                # (another bind locator).
                # If it has external parent, from another module we only cache parent
                # and parenting will be done once all bind locators are processed.
                parentBindLoc, external = shadow.sourceBindLocator.nonHiddenParentBindLocator

                # Bind locators with no parent means that shadow needs to be
                # parented to root.
                if parentBindLoc is None:
                    shadow.modoItem.setParent(self._shadowRoot, -1)
                    continue

                # Do direct parenting here.
                # Note since we are iterating bind locators in hierarchical order
                # this shadow parent shadow should already be on the list.
                # If it's not then it's a problem.
                if not external:
                    try:
                        parentShadow = shadowsBySourceIdentifiers[parentBindLoc.modoItem.id]
                    except KeyError:
                        continue
                    shadow.modoItem.setParent(parentShadow.modoItem, -1)
                else:
                    # Store this shadow for setting up external parent later.
                    shadowsWithExternalParents.append(shadow)

        if description.supportStretching:
            # parenting to root motion if one is found.
            if rootMotionShadow is not None:
                for shadow in self._shadows:
                    if shadow == rootMotionShadow:
                        continue
                    shadow.modoItem.setParent(rootMotionShadow.modoItem, -1)
        else:
            # This is where fragments of hierarchies from separate modules
            # are connected together into single bind skeleton hierarchy
            for shadow in shadowsWithExternalParents:
                parentBindLoc, external = shadow.sourceBindLocator.nonHiddenParentBindLocator
                if not external:
                    continue
                try:
                    parentShadowModoItem = shadowsBySourceIdentifiers[parentBindLoc.modoItem.id].modoItem
                except KeyError:
                    parentShadowModoItem = self._shadowRoot
                shadow.modoItem.setParent(parentShadowModoItem, -1)

            if description.shadowType == BindSkeletonShadowType.ANIMATED:
                self._applyBakedHierarchy(shadowsBySourceIdentifiers)

    def _matchShadowSkeletonToSource(self):
        """ Matches all bind skeleton shadows transforms to their bind locator counterparts.
        """
        hierarchy = modox.Item(self._shadowRoot.internalItem).getOrderedHierarchy(includeRoot=False)
        for item in hierarchy:
            try:
                BindLocatorShadow(item).matchToSource()
            except TypeError:
                continue

    def _linkShadowTransformsToSource(self, linkScale=False):
        """ Links shadow skeleton transforms to source bind locators.
        
        This will make shadow skeleton move exactly the same as the original
        bind skeleton.

        This method will also set up rotation constraints between source and shadow
        bind locators and apply rotation offsets on joints that have offset
        values different from 0.
        """
        for shadow in self._shadows:
            sourceBindLoc = shadow.sourceBindLocator
            if sourceBindLoc is None:
                continue
            sourceItem = sourceBindLoc.modoItem
            targetItem = shadow.modoItem
            modox.TransformUtils.linkWorldTransforms(sourceItem, targetItem, linkPos=True, linkRot=False, linkScale=linkScale)
            self._applyOrientationOffsets(sourceBindLoc, shadow)

    def _unlinkShadowTransforms(self):
        """
        This unlinks bind skeleton shadow from source and makes it independent thing.
        """
        for shadow in self._shadows:
            wpos = modox.LocatorUtils.getItemWorldPositionMatrixChannel(shadow.modoItem)
            wrot = modox.LocatorUtils.getItemWorldRotationMatrixChannel(shadow.modoItem)
            wscl = modox.LocatorUtils.getItemWorldScaleMatrixChannel(shadow.modoItem)
            modox.ChannelUtils.removeAllReverseConnections([wpos, wrot, wscl])

    def _applyOrientationOffsets(self, sourceBindLoc, targetShadow):
        """
        Orientation offsets allow for aligning the bind skeleton in a different way
        to match requirements of the application that we export to.
        """
        offsetVec = sourceBindLoc.orientationOffset

        # If there's no offset just link transforms in normal way
        # NOTE: For the time being we set up constraints for bind skeleton shadow.
        # if offsetVec.x == 0.0 and offsetVec.y == 0.0 and offsetVec.z == 0.0:
        #     modox.TransformUtils.linkWorldTransforms(sourceBindLoc.modoItem,
        #                                              targetShadow.modoItem,
        #                                              linkPos=False,
        #                                              linkRot=True,
        #                                              linkScale=False)
        #     return

        # Otherwise insert transform constraint and set offset on it.
        # We assume transforms are linked already
        sourceWRotChan = modox.LocatorUtils.getItemWorldRotationMatrixChannel(sourceBindLoc.modoItem)
        shadowWRotChan = modox.LocatorUtils.getItemWorldRotationMatrixChannel(targetShadow.modoItem)

        constraint = modox.CMTransformConstraint.new(self._rig.setup.rootAssembly,
                                                     targetShadow.modoItem,
                                                     targetShadow.modoItem.name + '_rotCns')

        sourceWRotChan >> constraint.inputChannel
        constraint.outputChannel >> shadowWRotChan
        constraint.offset = offsetVec

    def _applyBakedHierarchy(self, shadowsBySourceIdentifiers):
        for shadow in self._shadows:
            bakedParent = shadow.sourceBindLocator.bakedParent
            if bakedParent is None:
                continue

            try:
                parentShadow = shadowsBySourceIdentifiers[bakedParent.id]
            except KeyError:
                continue

            shadow.modoItem.setParent(parentShadow.modoItem, 0)

    def __init__(self, rig):
        self._rig = rig
        self._shadows = []
