

import lx
import modo
import modox
from modox import TransformToolsUtils
from modox import ChannelUtils

from ..const import ItemFeatureType
from ..const import EventTypes as e
from ..core import service
from ..controller_if import Controller
from ..controller_dyna_space import ControllerDynamicSpace
from .. import const as c


class ControllerChannelState(object):
    ANIMATED = 'a'
    STATIC = 's'
    SETTING = 't'
    LOCKED = 'l'
    IGNORE = 'i'


class ContentType(object):
    ITEM = 'item'
    CHANNELS = 'chans'


class ControllerAnimationSpace(object):
    FIXED = 'fixed'
    DYNAMIC = 'dynamic'

class ControllerAnimationSpaceInt(object):
    FIXED = 0
    DYNAMIC = 1


class ControllerItemFeature(Controller):

    CHAN_ACTOR_CONTENT_ITEM = 'rsacActorItem'
    CHAN_ACTOR_CONTENT_CHANNELS = 'rsacActorChannels'
    CHAN_ANIMATION_SPACE = 'rsacAnimationSpace'
    CHAN_IN_DEFAULT_SET = 'rsacInDefaultSet'
    CHAN_IN_POSE = 'rsacInPose'
    CHAN_LOCKED = 'rsacLocked'
    CHAN_ALIAS = 'rsacAlias'

    ActorContentType = ContentType
    ChannelState = ControllerChannelState
    AnimationSpace = ControllerAnimationSpace
    AnimationSpaceInt = ControllerAnimationSpaceInt
    _AnimationSpaceInt = ControllerAnimationSpaceInt
    _AnimationSpaceStrToInt = {
        ControllerAnimationSpace.DYNAMIC: ControllerAnimationSpaceInt.DYNAMIC,
        ControllerAnimationSpace.FIXED: ControllerAnimationSpaceInt.FIXED}

    # -------- Feature description
    
    descIdentifier = ItemFeatureType.CONTROLLER
    descUsername = 'Controller'
    descExclusiveItemType = c.RigItemType.GENERIC
    
    descDefaultChannelState = ChannelState.IGNORE
    descChannelStatesClass = ControllerChannelState
    descChannelStatesUsernames = {ChannelState.ANIMATED: 'Animated',
                                  ChannelState.STATIC: 'Static',
                                  ChannelState.SETTING: 'Setting',
                                  ChannelState.LOCKED: 'Locked',
                                  ChannelState.IGNORE: 'Ignore'}
    descChannelStatesUIOrder = [ChannelState.IGNORE,
                                ChannelState.ANIMATED,
                                ChannelState.STATIC,
                                ChannelState.SETTING,
                                ChannelState.LOCKED]
    
    descPackages = Controller.descPackages + ['rs.pkg.animController']
        
    # -------- Public methods
    
    def onAdd(self):
        try:
            Controller.onAdd(self)
        except AttributeError:
            pass
        self._setInitialProperties()

    def onSetChannelState(self, chanName, state):
        if state in [self.ChannelState.ANIMATED, self.ChannelState.STATIC]:
            channel = self._getChannelByName(chanName)
            ChannelUtils.setChannelSetupValue(channel)

    @property
    def transformToolsEnabledInSetup(self):
        return False

    @property
    def addItemToActor(self):
        """ Read actor content state from the item.

        The value comes as a string hint so it has to be converted into the integer value
        that is one of ControllerActorContent constants.
        """
        return self.item.getChannelProperty(self.CHAN_ACTOR_CONTENT_ITEM)

    @addItemToActor.setter
    def addItemToActor(self, state):
        self.item.setChannelProperty(self.CHAN_ACTOR_CONTENT_ITEM, state)
        if not self.batchEdit:
            service.events.send(e.ITEM_CHANGED, item=self.modoItem)

    @property
    def addChannelsToActor(self):
        return self.item.getChannelProperty(self.CHAN_ACTOR_CONTENT_CHANNELS)

    @addChannelsToActor.setter
    def addChannelsToActor(self, state):
        self.item.setChannelProperty(self.CHAN_ACTOR_CONTENT_CHANNELS, state)
        if not self.batchEdit:
            service.events.send(e.ITEM_CHANGED, item=self.modoItem)

    @property
    def animationSpace(self):
        return self.item.getChannelProperty(self.CHAN_ANIMATION_SPACE)
    
    @animationSpace.setter
    def animationSpace(self, value):
        """ Gets/sets animation space type for a controller.
        
        Parameters
        ----------
        value : str, int
            AnimationSpace.XXX

        Returns
        -------
        AnimationSpace.XXX
            One of animation space string hints.
        """
        if isinstance(value, str):
            value = self._AnimationSpaceStrToInt[value]
        self.item.setChannelProperty(self.CHAN_ANIMATION_SPACE, value)

        # If we change space to fixed the entire dynamic space setup
        # has to be removed from controller.
        if value == self._AnimationSpaceInt.FIXED:
            dynaSpace = ControllerDynamicSpace(self.item)
            dynaSpace.remove()

        if not self.batchEdit:
            service.events.send(e.ITEM_CHANGED, item=self.modoItem)

    @property
    def isVisibleInDefaultSet(self):
        """ Returns whether controller should be visible in default set.
        
        Default set is a set of controllers that should be visible in animate
        context when no other specific set is selected.
        
        Returns
        -------
        bool
        """
        return self.item.getChannelProperty(self.CHAN_IN_DEFAULT_SET)

    @property
    def locked(self):
        """
        Gets the locked state of a controller.

        Returns
        -------
        bool
        """
        return self.item.getChannelProperty(self.CHAN_LOCKED)

    @locked.setter
    def locked(self, state):
        """
        Sets locked state for the controller.

        Locked controller should be skipped by keyframe editing commands.

        Parameters
        ----------
        state : bool
        """
        self.item.setChannelProperty(self.CHAN_LOCKED, state)

    @property
    def isStoredInPose(self):
        """ Returns whether controller should be saved in pose presets.
        Returns
        -------
        bool
        """
        return self.item.getChannelProperty(self.CHAN_IN_POSE)
    
    @property
    def dynamicSpace(self):
        """ Gives access to dynamic space interface.
        
        Returns
        -------
        ControllerDynamicSpace, None
            None is returned when controller has fixed animation space.
        """
        if self.animationSpace == self.AnimationSpace.DYNAMIC:
            return ControllerDynamicSpace(self.item)
        return None
        
    @property
    def animatedChannels(self):
        """ Gets list of channels that can be animated (keyframed).

        Returns
        -------
        list : modo.Channel
        """
        channels = self._getChannelsWithState(self.ChannelState.ANIMATED)
        return channels

    @property
    def staticChannels(self):
        """ Gets list of channels that should be part of an actor
        but should not be animated (keyframed).

        Returns
        -------
        list : modo.Channel
        """
        return self._getChannelsWithState(self.ChannelState.STATIC)

    @property
    def settingChannels(self):
        """ Gets list of channels that can be changed but should not be part of an actor.

        These channels are settings, they are not action-based.
        Their values should exist on setup only.

        Returns
        -------
        list : modo.Channel
        """
        return self._getChannelsWithState(self.ChannelState.SETTING)

    @property
    def actorChannels(self):
        """ Gets list of channels that should be added to an actor.

        The list will not include transform/user channels
        if Add Channels To Actor is False.

        Returns
        -------
        list : modo.Channel
        """
        if self.addChannelsToActor:
            chans = self.animatedChannels
            chans.extend(self.staticChannels)
        else:
            chans = []

        if self.animationSpace == self.AnimationSpace.DYNAMIC:
            dynaSpace = ControllerDynamicSpace(self.item)
            chans.extend(dynaSpace.animatedChannels)

        return chans

    @property
    def lockedChannels(self):
        """ Gets list of channels that should be locked.

        Returns
        -------
        list : modo.Channel
        """
        return self._getChannelsWithState(self.ChannelState.LOCKED)

    @property
    def channelSetChannels(self):
        chans = self.animatedChannels
        chans.extend(self.staticChannels)
        chans.extend(self.settingChannels)
        return chans
    
    def getChannelState(self, chanName):
        """ Gets state of a channel by its name.
        
        Returns
        -------
        ChannelState
            IGNORE is returned when the channel cannot be found.
        """
        try:
            return self._channelStates[chanName]
        except KeyError:
            return self.ChannelState.IGNORE

    def updateRestValues(self):
        """ Updates rest values for all animated and static channels.
        
        This should be done every time setup pose or other setup values
        change for the controller.
        """
        for channel in self.actorChannels:
            ChannelUtils.setChannelSetupValue(channel)

    def setKey(self):
        """
        Sets key for the controller at current time and action.
        """
        for chan in self.animatedChannels:
            chanString = "%s:%s" % (chan.item.id, chan.name)
            lx.eval('!channel.key mode:add channel:{%s}' % (chanString))

    def onSelected(self):
        """ Call when controller is selected to perform one of predefined actions.
        
        Parameters
        ----------
        action : OnSelectedAction.XXX
        """
        Controller.onSelected(self)
        
        # Unselect any hanging dynamic parents - this is to make sure
        # their keys will not show up.
        # Hanging parent modifiers happen because selecting an item in viewport
        # does not deselect dynamic modifier if one was selected.
        # Note that this is not ideal place to do this since these parents
        # will remain handing
        # scene = modo.Scene()
        # selected = scene.selected
        # ctrlIdents = []
        # dynaParents = []
        # for item in selected:
        #     if item.type == 'cmDynamicParent':
        #         dynaParents.append(item)
        #     else:
        #         try:
        #             ctrl = ControllerItemFeature(item)
        #         except TypeError:
        #             continue
        #         ctrlIdents.append(item.id)
        #
        # if dynaParents:
        #     for parent in dynaParents:
        #         children = modox.DynamicParentModifier(parent).children
        #         if not children:
        #             continue
        #         childSelected = False
        #         for child in children:
        #             if child.id in ctrlIdents:
        #                 childSelected = True
        #                 break
        #         # At this point we've got dyna parent that has no children selected.
        #         # Deselect it.
        #         if not childSelected:
        #             scene.deselect(parent)
        #
        # # Select dynamic parent if controller has dynamic space and that space is animated.
        # if self.animationSpace == self.AnimationSpace.DYNAMIC and self.dynamicSpace.isAnimated:
        #     dynaParent = ControllerDynamicSpace(self.item).dynamicParentModifier
        #     if dynaParent is not None:
        #         modo.Scene().select(dynaParent, add=True)

    @property
    def bakedItemCommandString(self):
        """
        Gets baked item command string, the actual MODO command that will be run on selected controller.

        Baked command is possible to run on vanilla MODO.

        Returns
        -------
        str, None
            None is returned when item command cannot be baked (it has to be rig system command
            and it won't run on vanilla MODO).
        """
        controlledChannels = self.controlledChannels
        if controlledChannels == self.ControlledChannels.TRANSFORM:
            return modox.TransformToolsUtils().getToolItemCommandStringFromChannels(self.channelSetChannels)

        if controlledChannels == self.ControlledChannels.USER:
            chanSet = self.channelSet
            chanSetModoItem = chanSet.channelSetModoItem
            if chanSetModoItem:
                return 'group.current {%s} chanset' % chanSetModoItem.id

        return None

    def onStandardize(self):
        """
        When standardizing controller we want to set its item command to the tool that
        is automatically enabled when controller feature is on the item.

        We also want to make sure the controller has channel set created.
        """
        vanillaCommand = self.bakedItemCommandString
        if vanillaCommand:
            modox.ItemUtils.setItemCommandManually(self.modoItem, vanillaCommand, denyDropAction=True)

        if self.controlledChannels == self.ControlledChannels.USER:
            # This will force create channel set and free it from the rig
            # if this is user channel controller and channel set is not created yet.
            try:
                self.channelSet.freeFromRig()
            except LookupError:
                pass

    # -------- Private methods
    
    def _setInitialProperties(self):
        """ Sets initial properties for controller.
        """
        
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor magenta')

        # Set custom shape only if one is not set yet and only if we're dealing with locator type item.
        if modox.Item(self.modoItem.internalItem).isOfXfrmCoreSuperType:
            chanVal = lx.eval('!channel.value ? channel:{%s:drawShape}' % self.modoItem.id)
            if chanVal == "custom":
                return

            if not self.modoItem.internalItem.PackageTest("glItemShape"):
                self.modoItem.internalItem.PackageAdd("glItemShape")

            lx.eval('!channel.value custom channel:{%s:drawShape}' % self.modoItem.id)
            lx.eval('!channel.value false channel:{%s:isSolid}' % self.modoItem.id)
            lx.eval('!channel.value .1 channel:{%s:isSize.X}' % self.modoItem.id)
            lx.eval('!channel.value .1 channel:{%s:isSize.Y}' % self.modoItem.id)
            lx.eval('!channel.value .1 channel:{%s:isSize.Z}' % self.modoItem.id)