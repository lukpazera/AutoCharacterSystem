
import lx
import modo
import modox

from . import const as c
from .item import Item
from .util import run
from .log import log
from .xfrm_link import TransformLink
from .items.space_switcher import SpaceSwitcherItem
from .items.generic import GenericItem
from .item_feature_op import ItemFeatureOperator
from .item_features.controller import ControllerItemFeature


class ControllerDynamicSpaceOperator(object):

    def add(self, targetRigItem=None, replace=True):
        """
        Adds dynamic space setup to given controller.

        Parameters
        ----------
        replace : bool, optional
            When True

        Returns
        -------
        ControllerItemFeature
            Returns new dynamic parent controller

        Raises
        ------
        TypeError
            When bad target item was given.
            This can be either not a rig item or if target item was None
            and the controller does not have any parents to set as dynamic space by default.
        """
        # Remove any previous setup first.
        dynaSpace = self._ctrl.dynamicSpace
        if replace:
            if dynaSpace is not None:
                dynaSpace.remove()
        else:
            if dynaSpace is not None and dynaSpace.isFullSetup:
                return ControllerItemFeature(dynaSpace.dynamicParentModifier)

        if targetRigItem is None:
            parentModoItem = self._item.modoItem.parent
            if parentModoItem is None:
                raise TypeError
            try:
                targetRigItem = Item.getFromModoItem(parentModoItem)
            except TypeError:
                raise

        if issubclass(targetRigItem.__class__, Item):
            targetModoItem = targetRigItem.modoItem
        else:
            targetModoItem = targetRigItem
            try:
                targetRigItem = Item.getFromModoItem(targetModoItem)
            except TypeError:
                targetRigItem = None

        # Set dynamic parent modifier as rig controller
        # so it can be present in actions etc.
        xfrmLink = TransformLink.new(self._item.modoItem,
                                     targetModoItem,
                                     c.TransformLinkType.DYNA_PARENT,
                                     compensation=True)

        dynaParentItem = xfrmLink.setup.dynamicParentSetup.dynamicParentModifier
        return self._setupDynamicParentAsController(dynaParentItem)

    @property
    def animatedDynamicSpace(self):
        """
        Tests whether dynamic space on a controller is animated.

        Returns
        -------
        bool
        """
        return self._ctrl.dynamicSpace.isAnimated

    @animatedDynamicSpace.setter
    def animatedDynamicSpace(self, state):
        """
        Enables/disables animated dynamic space on a controller with dynamic space set.

        Note that this function alters setup mode state as needed to set up/remove the setup.

        Parameters
        ----------
        bool : state
            True will enable animated dynamic space setting initial parent key at current
            action and time.
            False will remove all the animation from dynamic space dyna parent modifier.
        """
        setupMode = modox.SetupMode()
        if state:
            # Add the required setup but only if one doesn't exist yet.
            # Then set the initial keyframe.
            setupMode.state = True
            dynaParentCtrl = self.add(replace=False)
            setupMode.state = False

            # When enabling animated dynamic space for a controller
            # we need to set initial key on the dynamic parent modifier at frame 0.
            # This way when user changes parent at current frame parenting prior
            # to that frame will be preserved.
            # This is not super efficient, I could just set key directly at 0 time
            # but it's just easier like this for now.
            backupTime = run('select.time ?')
            run('select.time 0.0 0 0')
            dynaParentCtrl.setKey()
            run('select.time %f 0 0' % backupTime)

        else:
            # Remove animation
            # or delete entire setup - depending on whether custom space is used or not.
            setupMode.state = False
            dynaParentModifier = self._ctrl.dynamicSpace.dynamicParentModifier
            if dynaParentModifier is not None:
                try:
                    parentCtrl = ControllerItemFeature(dynaParentModifier)
                except TypeError:
                    pass
                else:
                    channels = parentCtrl.animatedChannels
                    modox.ChannelUtils.removeAnimation(channels)
                    modox.ChannelUtils.resetChannelsToDefault(channels)

    def setAnimationSpaceToDynamic(self):
        """
        Sets controller animation space to dynamic one.
        """
        # This really just changes the setting on controller package.
        self._ctrl.animationSpace = ControllerItemFeature.AnimationSpace.DYNAMIC
        # Add dynamic space setup by default.
        self.add(replace=True)

    def setAnimationSpaceToFixed(self):
        """
        Sets controller animation space to fixed one.
        """
        self._ctrl.animationSpace = ControllerItemFeature.AnimationSpace.FIXED

    @property
    def hasDynamicSpace(self):
        """
        Tests whether this controller has dynamic space set.

        Returns
        -------
        bool
        """
        return self._ctrl.dynamicSpace is not None

    def setDefaultSpace(self, targetRigItem):
        """
        Sets custom default space for an item.

        Parameters
        ----------
        targetRigItem : Item
        """
        self.add(targetRigItem, replace=True)

    @property
    def controllerFeature(self):
        """
        Gets the controller feature associated with the controller this object was initialized with.

        Returns
        -------
        ControllerItemFeature
        """
        return self._ctrl

    # -------- Private methods

    def _setupDynamicParentAsController(self, modoItem):
        name = self._item.name + 'SpaceSwitcher'
        rigItem = SpaceSwitcherItem.newFromExistingItem(modoItem, name=name)
        itemFeatureOp = ItemFeatureOperator(rigItem)
        ctrl = itemFeatureOp.addFeature(c.ItemFeatureType.CONTROLLER)

        ctrl.controlledChannels = ControllerItemFeature.ControlledChannels.ITEM

        ctrlChannelNames = modox.DynamicParentSetup.DYNA_PARENT_CHANNELS
        for channelName in ctrlChannelNames:
            ctrl.setChannelState(channelName, ControllerItemFeature.ChannelState.ANIMATED)

        return ctrl

    def _getControllerFromSwitcherModifier(self, dynaParentModoItem):
        dynaModifier = modox.DynamicParentModifier(dynaParentModoItem)
        children = dynaModifier.children
        if not children:
            return None
        try:
            ctrl = ControllerItemFeature(children[0])
        except TypeError:
            return None
        return ctrl

    def __init__(self, controller):
        if controller.item.type == c.RigItemType.SPACE_SWITCHER:
            # get rig item from dyna parent.
            controller = self._getControllerFromSwitcherModifier(controller.modoItem)
            if controller is None:
                raise TypeError

        self._ctrl = controller
        self._item = self._ctrl.item