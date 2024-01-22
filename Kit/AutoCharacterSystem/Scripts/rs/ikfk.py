
""" This module implements seamless IK/FK workflow.

    The current design is:
    - add match link feature to each item that is part of the match chain,
    such as the ik->fk chain.
    - items that need to be matched to something need to have the match link item set.
    - items that do not have the link set are considered ones that trigger the match,
    so in case of ik->fk chain these are controllers that change the pose of ik setup.
    - chain item feature needs to be added to any item that will be chain owner.
    - all chain items need to point to this chain via their match link item feature property.
    - ikfk switcher item feature has to be added to an item that will act as switcher.
    - switcher needs to have its ik->fk and fk->ik chains set.
    - an IKBlending channel needs to be set as well, this channel will be controlled
    by the switcher. This channel should be part of controller user channels so it's in actor.
"""


import lx
import modo
import modox

from . import item_feature
from . import scene_event
from . import const as c
from .log import log
from .module import Module
from .item import Item
from .item_features.controller import ControllerItemFeature
from .util import run
from .context_op import ContextOperator
from .module_feature_op import FeaturedModuleOperator


class MatchTarget(object):
    FK = 'fk'
    IK = 'ik'


class IKFKMatchingSyncMode(object):
    CURRENT_TIME = 0
    EXPLICIT_TIME = 1
    ENVELOPE = 2


class IKSolverMatchExtras(item_feature.ItemFeature):
    """
    This item feature needs to be applied to IK solver that is meant to work with IK/FK matching.

    Hopefully, the functionality of this item feature will not be needed once MODO's native
    FK->IK matching allows for setting matched transforms to some other item then the IK goal.
    Until this happens this feature provides a way to set up items required for FK->IK matching.

    3 items are needed to perform FK->IK matching on an item different the goal properly.

    TargetItem - the item to which matched transform will be applied instead of to the goal.
    TargetReferenceItem - the item attached to FK chain showing where the target item should be assuming there's no soft ik.
    GoalReference - the item from FK chain showing where the goal would be if there's no soft ik.

    The idea is that we measure the offset between goal reference and target reference in world space.
    Then after the IK is matched to FK we take goal position, add calculated offset to the goal position and we
    receive world position of the target item. Final transform is applied to target item.
    """

    descIdentifier = c.ItemFeatureType.IKFK_SOLVER_MATCH
    descUsername = 'IK Solver Match Extras'
    descListed = True
    descCategory = c.ItemFeatureCategory.GENERAL
    descExclusiveModoItemType = modox.c.ItemType.IK_23BAR_SOLVER

    _GRAPH_IK_TARGET = 'rs.ikMatchTarget'
    _GRAPH_IK_TARGET_REF = 'rs.ikMatchTgtRef'
    _GRAPH_IK_GOAL_REF = 'rs.ikMatchGoalRef'

    @property
    def ikMatchTargetItem(self):
        return modox.ItemUtils.getFirstForwardGraphConnection(self.item.modoItem, self._GRAPH_IK_TARGET)

    @ikMatchTargetItem.setter
    def ikMatchTargetItem(self, modoItem):
        modox.ItemUtils.clearForwardGraphConnections(self.item.modoItem, self._GRAPH_IK_TARGET)

        if modoItem is None:
            return

        modox.ItemUtils.addForwardGraphConnections(self.item.modoItem, modoItem, self._GRAPH_IK_TARGET)

    @property
    def ikMatchTargetReferenceItem(self):
        return modox.ItemUtils.getFirstForwardGraphConnection(self.item.modoItem, self._GRAPH_IK_TARGET_REF)

    @ikMatchTargetReferenceItem.setter
    def ikMatchTargetReferenceItem(self, modoItem):
        modox.ItemUtils.clearForwardGraphConnections(self.item.modoItem, self._GRAPH_IK_TARGET_REF)

        if modoItem is None:
            return

        modox.ItemUtils.addForwardGraphConnections(self.item.modoItem, modoItem, self._GRAPH_IK_TARGET_REF)

    @property
    def ikMatchGoalReference(self):
        return modox.ItemUtils.getFirstForwardGraphConnection(self.item.modoItem, self._GRAPH_IK_GOAL_REF)

    @ikMatchGoalReference.setter
    def ikMatchGoalReference(self, modoItem):
        modox.ItemUtils.clearForwardGraphConnections(self.item.modoItem, self._GRAPH_IK_GOAL_REF)

        if modoItem is None:
            return

        modox.ItemUtils.addForwardGraphConnections(self.item.modoItem, modoItem, self._GRAPH_IK_GOAL_REF)

    def onRemove(self):
        # Clear graphs
        self.ikMatchTargetItem = None
        self.ikMatchTargetReferenceItem = None
        self.ikMatchGoalReference = None


class IKFKChainGroup(Item):
    """
    Defines group item that is used to collect all the FK or IK chain items together.
    """
    descType = c.RigItemType.IKFK_CHAIN_GROUP
    descUsername = 'IKFK Chain Group'
    descModoItemType = 'group'
    descDefaultName = 'Chain'
    descPackages = ['rs.pkg.generic']

    # -------- Public interface

    @property
    def items(self):
        """
        Gets a list of all items that are included this chain.

        Returns
        -------
        [modo.Item]
        """
        return modo.Group(self.modoItem.internalItem).items

    @property
    def channels(self):
        """
        Gets a list of all channels that are in this group.

        Returns
        -------
        [modo.Item]
        """
        return modo.Group(self.modoItem.internalItem).groupChannels

    @property
    def matchLinks(self):
        """
        Gets a list of match links contained in this chain.

        Match links are Match Item Transform item features.
        

        Returns
        -------
        [MatchTransformItemFeature]
        """
        return self._matchLinks

    @property
    def ikSolvers(self):
        """
        Returns
        -------
        [modox.IK23BarSolver]
        """
        return self._ikSolvers

    def getKeyItem(self, identifier):
        try:
            return self._keyItems[identifier]
        except KeyError:
            pass
        return None

    def onAdd(self, subtype):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor yellow')

    def init(self):
        self._matchLinks = []
        self._ikSolvers = []
        self._allItems = []
        self._keyItems = {}

        self._scan()

    # -------- Private methods

    def _scan(self):
        self._allItems = modo.Group(self.modoItem.internalItem).items
        for modoItem in self._allItems:

            # Cache key items
            try:
                rigItem = Item.getFromModoItem(modoItem)
            except TypeError:
                pass
            else:
                ident = rigItem.identifier
                if ident:
                    self._keyItems[ident] = rigItem

            # IK solver
            if modoItem.type == modox.c.ItemType.IK_23BAR_SOLVER:
                self._ikSolvers.append(modox.IK23BarSolver(modoItem))
            # Match item
            else:
                try:
                    matchLink = MatchTransformItemFeature(modoItem)
                except TypeError:
                    continue
                self._matchLinks.append(matchLink)


class MatchTransformItemFeature(item_feature.LocatorSuperTypeItemFeature):
    """
    Add this feature to every item in a chain that needs to be matched to some other chain.
    """

    descIdentifier = c.ItemFeatureType.ITEM_MATCH_XFRM
    descUsername = "Match Item Transforms"
    descPackages = "rs.pkg.matchItemXfrmIF"

    _MATCH_GRAPH = "rs.itemMatchX"

    @property
    def referenceItem(self):
        graph = self.modoItem.itemGraph(self._MATCH_GRAPH)
        try:
            return graph.forward(0)
        except LookupError:
            return None
    
    @referenceItem.setter
    def referenceItem(self, modoItem):
        """ Gets/sets the item to which transforms will be matched.
        
        Returns
        -------
        modo.Item
        """
        modox.ItemUtils.clearForwardGraphConnections(self.modoItem, self._MATCH_GRAPH)
        if modoItem is None:
            return
        modox.ItemUtils.addForwardGraphConnections(self.modoItem, modoItem, self._MATCH_GRAPH)

    @property
    def matchPosition(self):
        """
        Checks whether position should be matched.

        Returns
        -------
        bool
        """
        return self.item.getChannelProperty("rsmxMatchPos")

    @property
    def matchRotation(self):
        """
        Checks whether rotation should be matched.

        Returns
        -------
        bool
        """
        return self.item.getChannelProperty("rsmxMatchRot")

    @property
    def matchPositionInLocalSpace(self):
        """
        Checks whether position should be matched in local space.

        Returns
        -------
        bool
        """
        try:
            return self.item.getChannelProperty('rsmxMatchPosLocal')
        except LookupError:
            return False

    @property
    def matchRotationInLocalSpace(self):
        """
        Checks whether rotation should be matched in local space.

        Returns
        -------
        bool
        """
        try:
            return self.item.getChannelProperty('rsmxMatchRotLocal')
        except LookupError:
            return False

    def onRemove(self):
        self.referenceItem = None

        
class MatchChainItemFeature(item_feature.LocatorSuperTypeItemFeature):

    descIdentifier = c.ItemFeatureType.CHAIN_MATCH_XFRM
    descUsername = "Match Chain Transforms"

    _MATCH_GRAPH = "rs.itemMatchX"
    _CHAIN_MATCH_GRAPH = "rs.chainMatchX"
    _IKFK_CHAIN_GRAPH = 'rs.ikfkChain'
    
    # -------- Public methods
    
    @property
    def switcherModoItem(self):
        graph = self.modoItem.itemGraph(self._IKFK_CHAIN_GRAPH)
        try:
            return graph.reverse(0)
        except LookupError:
            return None


class IKFKSwitcherItemFeature(item_feature.LocatorSuperTypeItemFeature):
    """
    Main item feature that controls switching between chains.

    Apply this feature to an item that will act as a switcher.
    Selecting this item will switch between IK->IK and vice versa.
    """

    SyncMode = IKFKMatchingSyncMode

    descIdentifier = c.ItemFeatureType.IKFK_SWITCHER
    descUsername = 'IK/FK Switcher'
    descPackages = ['rs.pkg.ikfkIF']

    _CHAN_ENABLE = 'rsikEnable'
    _CHAN_MATCH_IK = 'rsikMatchIK'
    _CHAN_MATCH_FK = 'rsikMatchFK'
    _CHAN_BLEND_CHANNEL_NAME = 'rsikBlendChanName'

    _CHAN_BLEND_DEFAULT_NAME = 'IKFKBlend'

    _IKFK_CHAIN_GRAPH = 'rs.ikfkChain' # use this graph to connect fk and ik chains.
    _IKFK_BLEND_GRAPH = 'rs.ikfkBlend' #
    _IKFK_SOLVER_DRIVERS_GRAPH = 'rs.matchDrivers'
    
    # -------- Public methods

    @property
    def enabled(self):
        """
        Checks whether switcher is enabled in properties.

        Returns
        -------
        bool
        """
        if not self.modoItem.channel(self._CHAN_ENABLE).get():
            return False
        return True

    @property
    def matchIK(self):
        """
        Checks whether switcher is enabled in properties.

        Returns
        -------
        bool
        """
        if not self.modoItem.channel(self._CHAN_MATCH_IK).get():
            return False
        return True

    @property
    def matchFK(self):
        """
        Checks whether switcher is enabled in properties.

        Returns
        -------
        bool
        """
        if not self.modoItem.channel(self._CHAN_MATCH_FK).get():
            return False
        return True

    @property
    def fkChain(self):
        """
        Returns
        -------
        IKFKChainGroup, None
        """
        connected = modox.ItemUtils.getReverseGraphConnections(self.modoItem, self._IKFK_CHAIN_GRAPH)
        if not connected:
            return None
        try:
            return IKFKChainGroup(connected[0])
        except TypeError:
            pass
        return None

    @fkChain.setter
    def fkChain(self, chainGroup):
        """ Gets/sets the group item containing all the FK chain items.

        Parameters
        ----------
        IKFKChainGroup, modo.Item
        """
        # FK chain group item is connected via forward connection from the group item
        # to the IKFK switcher item.
        if isinstance(chainGroup, IKFKChainGroup):
            chainGroup = chainGroup.modoItem

        modox.ItemUtils.clearReverseGraphConnections(self.modoItem, self._IKFK_CHAIN_GRAPH)
        if chainGroup is None:
            return
        modox.ItemUtils.addReverseGraphConnections(self.modoItem, chainGroup, self._IKFK_CHAIN_GRAPH)

    @property
    def ikChain(self):
        """
        Returns
        -------
        IKFKChainGroup, None
        """
        connected = modox.ItemUtils.getForwardGraphConnections(self.modoItem, self._IKFK_CHAIN_GRAPH)
        if not connected:
            return None
        try:
            return IKFKChainGroup(connected[0])
        except TypeError:
            pass
        return None

    @ikChain.setter
    def ikChain(self, chainGroup):
        """ Gets/sets the group item containing all the IK chain items.

        Parameters
        ----------
        IKFKChainGroup, modo.Item
        """
        # IK chain group item is connected via reverse connection from the group item
        # to the IKFK switcher item.
        if isinstance(chainGroup, IKFKChainGroup):
            chainGroup = chainGroup.modoItem

        modox.ItemUtils.clearForwardGraphConnections(self.modoItem, self._IKFK_CHAIN_GRAPH)
        if chainGroup is None:
            return
        modox.ItemUtils.addForwardGraphConnections(self.modoItem, chainGroup, self._IKFK_CHAIN_GRAPH)

    @property
    def ikSolverDriver(self):
        """
        Returns
        -------
        IKFKChainGroup, None
        """
        connected = modox.ItemUtils.getForwardGraphConnections(self.modoItem, self._IKFK_SOLVER_DRIVERS_GRAPH)
        if not connected:
            return None
        try:
            return IKFKChainGroup(connected[0])
        except TypeError:
            pass
        return None

    @ikSolverDriver.setter
    def ikSolverDriver(self, chainGroup):
        """ Gets/sets the group item containing all the items which channels drive IK solver properties.

        This group item needs to be part of the module only if solver has driver channels that do not
        connect to it directly (channels that go through some other nodes between them and the solver).
        Automatic lookup only goes to nearest input connection from solver and assumes it to be the driver.

        Parameters
        ----------
        IKFKChainGroup, modo.Item
        """
        # IK chain group item is connected via reverse connection from the group item
        # to the IKFK switcher item.
        if isinstance(chainGroup, IKFKChainGroup):
            chainGroup = chainGroup.modoItem

        modox.ItemUtils.clearForwardGraphConnections(self.modoItem, self._IKFK_SOLVER_DRIVERS_GRAPH)
        if chainGroup is None:
            return
        modox.ItemUtils.addForwardGraphConnections(self.modoItem, chainGroup, self._IKFK_SOLVER_DRIVERS_GRAPH)

    @property
    def ikfkChainModoItem(self):
        graph = self.modoItem.itemGraph(self._IKFK_CHAIN_GRAPH)
        try:
            return graph.forward(0)
        except LookupError:
            return None

    @property
    def ikfkBlendControllerModoItem(self):
        """
        Gets IKFK Blend controller modo item.

        Returns
        -------
        modo.Item, None
            None is returned if blend controller is not set.
        """
        graph = self.modoItem.itemGraph(self._IKFK_BLEND_GRAPH)
        try:
            return graph.forward(0)
        except LookupError:
            return None

    @property
    def ikfkBlendController(self):
        """
        
        Returns
        -------
        ControllerItemFeature
        """
        modoItem = self.ikfkBlendControllerModoItem
        if modoItem is None:
            return None
        
        try:
            return ControllerItemFeature(modoItem)
        except TypeError:
            return None
        
    @ikfkBlendController.setter
    def ikfkBlendController(self, controller):
        """ Gets/sets the controller that contains the ik/fk blend channel.
        
        It has to be controller so this channel is part of an actor.

        Parameters
        ----------
        MatchChainItemFeature, modo.Item
        """
        if isinstance(controller, ControllerItemFeature):
            controller = controller.modoItem

        modox.ItemUtils.clearForwardGraphConnections(self.modoItem, self._IKFK_BLEND_GRAPH)
        if controller is None:
            return
        modox.ItemUtils.addForwardGraphConnections(self.modoItem, controller, self._IKFK_BLEND_GRAPH)

    @property
    def blendingChannelName(self):
        """
        Returns
        -------
        str
        """
        return self.item.getChannelProperty(self._CHAN_BLEND_CHANNEL_NAME)

    @property
    def blendingChannel(self):
        """ Gets the channel that should be used for IK blending.
        
        Returns
        -------
        modo.Channel

        Raises
        ------
        LookupError
            When channel cannot be found or is not set yet.
        """
        blendCtrl = self.ikfkBlendControllerModoItem
        if blendCtrl is None:
            raise LookupError

        chanName = self.item.getChannelProperty(self._CHAN_BLEND_CHANNEL_NAME)
        chan = blendCtrl.channel(chanName)
        if chan is None:
            chan = blendCtrl.channel(self._CHAN_BLEND_DEFAULT_NAME)
        if chan is None:
            raise LookupError
        return chan

    @blendingChannel.setter
    def blendingChannel(self, chanName):
        """
        Sets name of the IK blending channel.

        Parameters
        ----------
        chanName : str, None
            Pass None to clear out blending channel setting
        """
        if chanName is None:
            chanName = self._CHAN_BLEND_DEFAULT_NAME
        self.item.setChannelProperty(self._CHAN_BLEND_CHANNEL_NAME, chanName)

    def getIKBlendingValue(self, time=None, action=lx.symbol.s_ACTIONLAYER_EDIT):
        return self.blendingChannel.get(time=time, action=action)

    def setIKBlendingValue(self, value, time=None, action=lx.symbol.s_ACTIONLAYER_EDIT):
        self.blendingChannel.set(value, time=time, key=True, action=action)

    def sync(self, syncMode=IKFKMatchingSyncMode.CURRENT_TIME, time=None):
        """
        Synchronizes IK and FK chains.

        Parameters
        ----------
        time : float, None
        """
        try:
            blendEnvelope = self.blendingChannel.envelope
        except LookupError:
            # not animated, skip
            return

        op = IKFKChainOperator(self.item.moduleRootItem)
        keyframes = blendEnvelope.keyframes
        selectionService = lx.service.Selection()
        currentTime = selectionService.GetTime()

        if syncMode == self.SyncMode.CURRENT_TIME:
            try:
                keyframes.Find(currentTime, lx.symbol.iENVSIDE_BOTH)
            except LookupError:
                return
            self._matchFrame(op, keyframes)

        elif syncMode == self.SyncMode.EXPLICIT_TIME:
            try:
                keyframes.Find(time, lx.symbol.iENVSIDE_BOTH)
            except LookupError:
                return
            self._matchFrame(op, keyframes)

        elif syncMode == self.SyncMode.ENVELOPE:
            for x in range(keyframes.numKeys):
                keyframes.setIndex(x)
                self._matchFrame(op, keyframes)

        selectionService.SetTime(currentTime)

    def _matchFrame(self, operator, keyframes):
        blendVal = keyframes.value
        keyTime = keyframes.time

        if blendVal > 0.5:
            matchTarget = MatchTarget.FK
        else:
            matchTarget = MatchTarget.IK

        # Have to use command here, going via selection service doesn't seem to change time fully.
        # IK/FK switch commands still act on current time then I think.
        run('select.time %f 0 0' % keyTime)

        operator.match(self, matchTarget)

    def onSelected(self):
        """ Switches between IK and FK.
        
        When going from IK to FK - match the FK chain first.
        Then make blending switch.
        """
        # Don't switch if the switcher is not enabled.
        if not self.enabled:
            return

        # Switch in animate context only.
        if ContextOperator.getContextIdentFast() != c.Context.ANIMATE:
            return

        # Don't switch if we are in setup mode.
        if modox.SetupMode().state:
            return

        blendVal = self.getIKBlendingValue()
        if blendVal < 1.0:
            newBlendVal = 1.0
            matchTarget = MatchTarget.IK
        else:
            newBlendVal = 0.0
            matchTarget = MatchTarget.FK

        op = IKFKChainOperator(self.item.moduleRootItem)
        op.match(self, matchTarget)
        
        self.setIKBlendingValue(newBlendVal)

        run('!tool.drop')
        run('!select.drop item')

    def onRemove(self):
        # Clear graphs
        self.ikChain = None
        self.ikfkChain = None


class IKFKChainOperator(object):
    """ Class to use to manage chains and ik/fk switching for a module.
    
    Paramters
    ---------
    moduleInitializer: Module, other
        Module or any other object Module can be initalized with.
    
    Raises
    ------
    TypeError:
        When bad initializer was passed.
    """

    _CHAIN_MATCH_GRAPH = "rs.chainMatchX"
    
    @property
    def chainModoItems(self):
        return modox.ItemUtils.getReverseGraphConnections(self._module.rootModoItem, self._CHAIN_MATCH_GRAPH)

    @property
    def chainItemGroups(self):
        """
        Gets a list of groups that hold chain items.

        Returns
        -------
        [IKFKChainGroup]
        """
        return self._module.getSubassembliesOfItemType(c.RigItemType.IKFK_CHAIN_GROUP)

    @property
    def chains(self):
        """ Gets all the chains in the module.
        
        Returns
        -------
        MatchChainItemFeature
        """
        modoItems = self.chainModoItems
        return [MatchChainItemFeature(modoItem) for modoItem in modoItems]

    def match(self, switcherFeature, targetItem):
        """
        This is the main IK/FK switching function.

        # TODO: Matching will currently work for setup with single IK chain only!
        # It's possible to enhance it to work on multiple solvers.
        # This code has to be updated for that first though!
        """
        try:
            featuredModule = FeaturedModuleOperator.getAsFeaturedModule(self._module)
        except TypeError:
            featuredModule = None

        # === Match to IK
        if targetItem == MatchTarget.IK and switcherFeature.matchIK:
            ikChain = switcherFeature.ikChain
            if ikChain is None:
                return

            # 1/3
            # First block of code that concerns switching using the IKFK Match Extras feature.
            # In involves using MODO's native FK->IK switching.
            # This code however doesn't work properly it needs to be fixed.
            ikSolvers = ikChain.ikSolvers
            solverExtras = None
            # We have 2 paths, one includes processing ik solvers
            # the other is for chains that do not feature ik solvers.
            if ikSolvers:
                solver = ikSolvers[0]

                try:
                    solverExtras = IKSolverMatchExtras(solver.modoItem)
                except TypeError:
                    #log.out("There is no Match Extras item feature on IK solver!", log.MSG_ERROR)
                    pass

                # If solver extras is set up that means that we do want to employ
                # MODO's native FK->IK switching.
                if solverExtras is not None:
                    targetItem = solverExtras.ikMatchTargetItem
                    targetRefItem = solverExtras.ikMatchTargetReferenceItem
                    targetGoalRefItem = solverExtras.ikMatchGoalReference

                    if targetItem is None or targetGoalRefItem is None:
                        return

                    targetRefWPos = modox.LocatorUtils.getItemWorldPositionVector(targetRefItem)
                    goalRef = targetGoalRefItem
                    goalRefWPos = modox.LocatorUtils.getItemWorldPositionVector(goalRef)
                    offset = targetRefWPos - goalRefWPos

                    #log.out("Target: %s    TargetParent: %s " % (target.modoItem.name, goalRef.name))
                    #log.out("Goal reference position: %s" % str(goalRefWPos))
                    #log.out("Offset from goal to target in world space: %s" % str(offset))

            # We match item transforms from match links first.
            # These 2 lines get executed on each IK/FK chain, regardless of whether
            # there are ik solvers involved or not.

            # Set IK to disabled, just in case.
            # This doesn't seem to be required.
            # for solver in ikSolvers:
            #     solver.setEnabled(False, time=None, key=False, action=lx.symbol.s_ACTIONLAYER_EDIT)

            self._matchItemTransforms(ikChain.matchLinks)
            self._switchSolversToIK(switcherFeature, solverExtras is not None)

            # Fix IK goal to old transforms.
            # need to reference goal somehow.
            # This should only be evaluated if ik chains are involved that need
            # matching items other than IK goals.

            # 2/3
            # IKFK Matching extras related code.
            if solverExtras is not None:
                goalModoItem = solver.goal
                matchedGoalWPos = modox.LocatorUtils.getItemWorldPositionVector(goalModoItem)
                newtargetWPos = matchedGoalWPos + offset

                itemSel = modox.ItemSelection()
                bkp = itemSel.getRaw()
                itemSel.set(targetItem, modox.SelectionMode.REPLACE)
                lx.eval("item.setPosition %f %f %f world" % (newtargetWPos.x, newtargetWPos.y, newtargetWPos.z))
                itemSel.set(bkp, modox.SelectionMode.REPLACE)

                # Now reset goal
                goalPosItem = modox.LocatorUtils.getTransformItem(goalModoItem, modox.c.TransformType.POSITION)
                #log.out("goal pos item: %s" % goalPosItem.id)
                run('!channel.restoreSetup channel:{%s:pos.X}' % goalPosItem.id)
                run('!channel.restoreSetup channel:{%s:pos.Y}' % goalPosItem.id)
                run('!channel.restoreSetup channel:{%s:pos.Z}' % goalPosItem.id)

                # Restore joints to setup values after matching.
                # We want to keep ik joint channels clean at all times.
                modox.IK23BarSetup(solver).restoreJointsToSetupPose()

            #log.out("Matched goal world position: %s" % str(matchedGoalWPos))
            #log.out("Target world position: %s" % str(newtargetWPos))

        # === Match to FK
        elif targetItem == MatchTarget.FK and switcherFeature.matchFK:
            fkChain = switcherFeature.fkChain
            if fkChain is None:
                return

            # Switching to FK doesn't really use IK solver switching at all.
            # It's just matching fk items to IK ones (provided they are added to fk chain group).
            # Using solver changes solver Blend value to 0%, keyframes all channels, etc.
            # so it requires additional handling which is not needed with simple matching.
            self._matchItemTransforms(fkChain.matchLinks)

            if featuredModule is not None:
                try:
                    featuredModule.onSwitchToFK(switcherFeature)
                except AttributeError:
                    pass

        # === Keyframe all IK/FK chain controller items
        # The idea is to always keyframe the entire IK/FK chain when matching.
        self._keyframeIKFKChainItems(switcherFeature)

    # -------- Private methods

    def _keyframeIKFKChainItems(self, switcherFeature):
        items = []
        ikChain = switcherFeature.ikChain
        if ikChain is not None:
            items.extend(ikChain.items)
        fkChain = switcherFeature.fkChain
        if fkChain is not None:
            items.extend(fkChain.items)

        for modoItem in items:
            self._keyframeItem(modoItem, True, True)

    def _switchSolversToFK(self, switcherFeature):
        ikChain = switcherFeature.ikChain
        solverItems = ikChain.ikSolvers

        for solver in solverItems:
            solver.switch(modox.IKSwitchDirection.TO_FK)

    def _switchSolversToIK(self, switcherFeature, useNativeSwitching=False):
        ikChain = switcherFeature.ikChain
        ikSolverDriverGroup = switcherFeature.ikSolverDriver

        solverItems = ikChain.ikSolvers
        # 3/3
        if useNativeSwitching:
            for solver in solverItems:
                log.out('gonna use native swtiching!')
                solver.switch(modox.IKSwitchDirection.TO_IK)

        try:
            blendingChannel = switcherFeature.blendingChannel
        except LookupError:
            blendingChannel = None
        self._applySolverValuesToDrivers(solverItems, ikSolverDriverGroup, blendingChannel)

    def _applySolverValuesToDrivers(self, solverItems, ikSolverDriverGroup, blendingChannel):
        """
        Use this method to copy values from driven channels to rig channels that drive them (if any).
        This is used on IK solvers because they are keyframed during switching but we do not want that.
        We want to keyframe controller channels that drive these.
        So we have to copy values from solvers and apply them to drivers and then values on solver
        should actually be removed.

        NOTE: Using group with driven-driver channel pairs allows for fixing any kind of channels, not
        just IK solver ones.

        TODO: All this code is a mess, needs to be cleaned up.

        Parameters
        ----------
        driverItems : [modo.Item]
        """
        # Store blending channel if given.
        # We need to make sure we don't process it in a wrong way.
        if blendingChannel:
            blendId = blendingChannel.item.id + blendingChannel.name
        else:
            blendId = None

        # Apply driver channel pairs first.
        # These are predefined pairs that tell which controller channel from the rig
        # drives which channel on the ik setup.
        # After switching to IK we need to copy values from solver to driver channels
        # in rig - to update rig pose properly.
        appliedChannels = []
        if ikSolverDriverGroup:
            channels = ikSolverDriverGroup.channels
            for x in range(0, len(channels), 2):
                chanFrom = channels[x]
                try:
                    chanTo = channels[x + 1]
                except IndexError:
                    break

                # Mark channel as applied. We can still skip this channel
                # if it appears to be driven by the blending channel.
                appliedChannels.append(chanFrom.item.id + chanFrom.name)

                v = chanFrom.get()
                # Clear keyframe from source channel.
                run('!channel.key mode:remove channel:{%s}' % modox.ChannelUtils.getChannelIdent(chanFrom))

                # Skip blending channel, no need to overwrite it.
                chanToId = chanTo.item.id + chanTo.name
                if blendId and chanToId == blendId:
                    continue

                chanTo.set(v, time=None, key=True, action=lx.symbol.s_ACTIONLAYER_EDIT)

        # Do automatic application for solver channels that were not applied yet.
        # This can probably go with the requirement of putting all solver channels into
        # the driven-driver group.
        for solver in solverItems:
            for solverChan in solver.switchKeyChannels:

                # Skip channels that were already processed as part of pairs processing above.
                chanId = solverChan.item.id + solverChan.name
                if chanId in appliedChannels:
                    continue

                # Backup channel value and remove key from the channel immediately.
                v = solverChan.get()
                run('!channel.key mode:remove channel:{%s}' % modox.ChannelUtils.getChannelIdent(solverChan))

                # Skip channels with no connections
                if solverChan.revCount < 1:
                    continue

                # Skip channel if it doesn't have driver channel.
                driverChannel = modox.ChannelUtils.getSourceDrivingChannel(solverChan)
                if driverChannel is None:
                    continue

                # Skip channel if it's blending channel
                if blendId is not None and blendId == (driverChannel.item.id + driverChannel.name):
                    continue

                driverChannel.set(v, time=None, key=True, action=lx.symbol.s_ACTIONLAYER_EDIT)

    def _matchItemTransforms(self, itemList):
        """
        Matches items from the list to their reference items.
        Items to match need to have the MatchTransform item feature added.

        itemList : [MatchTransformItemFeature]
        """
        matchDict = {}
        minLevel = 1000000
        maxLevel = -1

        for matchLink in itemList:
            refItem = matchLink.referenceItem
            # None ref item means we want to match item to itself which essentialy means
            # baking its transforms into values on channels.
            if refItem is None:
                refItem = matchLink.modoItem

            modoItem = matchLink.modoItem
            matchItemLevel = modox.ItemUtils.getHierarchyLevel(modoItem)
            if matchItemLevel not in matchDict:
                matchDict[matchItemLevel] = []
            matchDict[matchItemLevel].append((modoItem,
                                              refItem,
                                              matchLink.matchPosition,
                                              matchLink.matchRotation,
                                              matchLink.matchPositionInLocalSpace,
                                              matchLink.matchRotationInLocalSpace))

            if matchItemLevel < minLevel:
                minLevel = matchItemLevel
            if matchItemLevel > maxLevel:
                maxLevel = matchItemLevel

        #log.out('------ IKFK Matching')
        #log.startChildEntries()
        for x in range(minLevel, maxLevel + 1, 1):
            if x not in matchDict:
                continue
            for entry in matchDict[x]:
                #log.out('Matching %s to %s' % (entry[0].name, entry[1].name))
                if entry[2]: # match position
                    if entry[4]:  # match in local space
                        # This is ABSOLUTELY CRUCIAL to get evaluated local position by setting action to None here!
                        # Otherwise it matching won't work if any of position channels are driven.
                        posVec = modox.LocatorUtils.getItemPosition(entry[1], time=None, action=None)
                        modox.LocatorUtils.setItemPosition(entry[0], posVec, time=None, key=True, action=lx.symbol.s_ACTIONLAYER_EDIT)
                    else:
                        lx.eval('item.match mode:item type:pos axis:all average:0 item:{%s} itemTo:{%s}' % (entry[0].id, entry[1].id))
                if entry[3]: # match rotation
                    if entry[5]:  # match in local space
                        # This is ABSOLUTELY CRUCIAL to get evaluated local rotation by setting action to None here!
                        # Otherwise it matching won't work if any of rotation channels are driven.
                        rotVec = modox.LocatorUtils.getItemRotation(entry[1], time=None, action=None)
                        modox.LocatorUtils.setItemRotation(entry[0],
                                                           rotVec,
                                                           time=None,
                                                           key=True,
                                                           action=lx.symbol.s_ACTIONLAYER_EDIT)
                    else:
                        lx.eval('item.match mode:item type:rot axis:all average:0 item:{%s} itemTo:{%s}' % (entry[0].id, entry[1].id))
                        lx.eval('!item.adjustEuler item:{%s}' % (entry[0].id))

                    # Not completely working code for manual matching.
                    # matchedItem = entry[0]
                    # refModoItem = entry[1]
                    #
                    # targetWRotM4 = modox.LocatorUtils.getItemWorldTransform(refModoItem)
                    # targetWRotM4.position = [0., 0., 0.]
                    # log.out("Target world rotation we are matching to: %s" % str(targetWRotM4))
                    #
                    # matchedItemParentWRotM4 = modox.LocatorUtils.getItemParentWorldTransform(matchedItem)
                    # matchedItemParentWRotM4.position = [0., 0., 0.]
                    # log.out("Matched parent world rotation: %s" % str(matchedItemParentWRotM4))
                    #
                    # # Let's invert parent.
                    # invParentRotM4 = matchedItemParentWRotM4.inverted()
                    # matchedLocalRotM4 = targetWRotM4 * invParentRotM4
                    #
                    # # Need to use this to convert my matched local mtx to what I actually need
                    # # this accounts for zero rotations, etc.
                    # # Feed matchedLocalRotM4 to the method below
                    # lx.object.Locator.ExtractLocalRotation()
                    #
                    # log.out("Matched local rotation: %s" % str(matchedLocalRotM4))
                    #
                    # matchedItemRotOrder = modox.TransformUtils.getRotationOrder(matchedItem)
                    # log.out("Matched item rot order: %s" % matchedItemRotOrder)
                    # rotAngles = matchedLocalRotM4.asEuler(degrees=False, order=matchedItemRotOrder)
                    # rotDegAngles = matchedLocalRotM4.asEuler(degrees=True, order=matchedItemRotOrder)
                    # log.out(str(rotDegAngles))
                    # modox.LocatorUtils.setItemRotation(matchedItem, modo.Vector3(rotAngles), time=None, key=True, action=lx.symbol.s_ACTIONLAYER_EDIT)

        log.stopChildEntries()

    def _keyframeItem(self, modoItem, keyPos=False, keyRot=False):
        # We are goingt to keyframe controllers only
        try:
            ctrl = ControllerItemFeature(modoItem)
        except TypeError:
            return

        # And we are going to set a key on animated channels
        # that belong to requested set only.
        chanNamesToKey = []
        if keyPos:
            chanNamesToKey.extend(modox.c.TransformChannels.PositionAll)
        if keyRot:
            chanNamesToKey.extend(modox.c.TransformChannels.RotationAll)

        for channel in ctrl.animatedChannels:
            if channel.name in chanNamesToKey:
                run('channel.key mode:add channel:{%s}' % modox.ChannelUtils.getChannelIdent(channel))

    def __init__(self, moduleInitializer):
        if isinstance(moduleInitializer, Module):
            self._module = moduleInitializer
        else:
            try:
                self._module = Module(moduleInitializer)
            except TypeError:
                raise
    
    
class event_MatchChainItemChanged(scene_event.SceneEvent):
    
    descIdentifier = 'matchChain'
    descUsername = 'Match Chain Item Transform Changed'
    
    def process(self, arguments):
        switcherItem = modox.SceneUtils.findItemFast(arguments[0])
        targetChain = arguments[1]

        try:
            switcher = IKFKSwitcherItemFeature(switcherItem)
        except TypeError:
            return

        if not switcher.enabled:
            return

        if modox.SetupMode().state:
            return

        if ContextOperator.getContextIdentFast() != c.Context.ANIMATE:
            return

        blendChan = switcher.blendingChannel
        if not modox.ChannelUtils.hasKeyframeOnTimeAndAction(blendChan): # test current time and action
            return

        # Matching should only happen if the chain is in the inverse mode.
        op = IKFKChainOperator(switcher.item.moduleRootItem)
        op.match(switcher, targetChain)
