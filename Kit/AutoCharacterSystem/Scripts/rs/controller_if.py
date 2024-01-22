

import lx
import lxu
import modo
import modox
from modox import TransformToolsUtils
from modox import SetupMode

from .item import Item
from .item_feature import ItemFeature
from .const import EventTypes as e
from .core import service
from .controller_ui import ChannelSet
from .item_settings import SettingsTag
from .util import run
from .log import log
from .debug import debug


class CtrlControlledChannels(object):
    TRANSFORM = 'xfrm'
    USER = 'user'
    ITEM = 'item'


class ControllerOnSelectedActionType(object):
    AUTO = 'auto'
    MOVE = 'move'
    ROTATE = 'rotate'
    SCALE = 'scale'
    TRANSFORM = 'transform'


class Controller(ItemFeature):
    """ Base class for implementing controller item feature.
    
    Controller is an item that is exposed to user and user can
    edit its channels - either transform or user ones.

    Attributes
    ----------
    descChannelStatesClass : class
        This needs to be class containing all the possible channel states.
        for example:
        ANIMATED = 'a'
        STATIC = 's'

    descChannelStatesUsernames : dict of str : str
        This needs to contain usernames that will be shown in UI for all states.
        The key is one of the attributes from descChannelStatesClass, the value
        is the username string.
        
    descChannelStatesUIOrder : list
        A list of descChannelStatesClass attributes in an order in which they are
        meant to be presented in the UI popup.
        
    descDefaultChannelState : one of descChannelStatesClass
        This is the state that will be considered default one, meaning one that is not
        saved as a setting on item. When a channel is not found in the settings it will
        get default value assigned automatically.
        
    descItemCommand : str
        Name of the command that will be assigned as item command when the feature
        is added to an item.
        
    Methods
    -------
    onSetChannelState(chanName, state)
        Allows for performing extra actions when a given state is set.
        chanName is a name of the channel that is being set and state is one
        of predefined state values.
    """
    
    # -------- Static attributes

    _TAG_CONTROLLER = 'RSCH'
    _TAG_CONTROLLER_CODE = lxu.lxID4(_TAG_CONTROLLER)
    
    POS_CHANNELS = ['pos.X', 'pos.Y', 'pos.Z']
    ROT_CHANNELS = ['rot.X', 'rot.Y', 'rot.Z']
    SCALE_CHANNELS = ['scl.X', 'scl.Y', 'scl.Z']

    TRANSFORM_CHANNELS = POS_CHANNELS + ROT_CHANNELS + SCALE_CHANNELS
    
    CHAN_CONTROLLED_CHANNELS = 'rsctControlledChannels'

    ControlledChannels = CtrlControlledChannels
    OnSelectedActionType = ControllerOnSelectedActionType

    # -------- Feature description attributes
    
    descPackages = ['rs.pkg.controller']

    # -------- Controller attributes, need to be assigned by inheriting class
    
    descChannelStatesClass = None # This should be a class
    descChannelStatesUsernames = {} # state key + username value
    descChannelStatesUIOrder = [] # Should be a list of keys
    descDefaultChannelState = None # channel state to use when there's no setting for this channel.

    # -------- Public methods

    @classmethod
    def customTest(cls, modoItem):
        """
        We make controllers work on locators and channel modifiers.
        """
        xitem = modox.Item(modoItem.internalItem)
        return xitem.isOfXfrmCoreSuperType or xitem.isOfChannelModifierSuperType

    def init(self):
        self._channelStates = {}
        self._userChannelChanged = False # This is used for channel haul updates
        self._batchMode = False
        self._load()

    def onRemove(self):
        self._clearSettings()
        if self.controlledChannels == self.ControlledChannels.USER:
            self._deleteChannelSet()

    @property
    def batchEdit(self):
        """ Queries batch edit state.
        """
        return self._batchMode
    
    @batchEdit.setter
    def batchEdit(self, state):
        """ Sets batch mode.
    
        Batch mode is used for editing multiple channels without
        saving changes to item each time.
        Set batch edit to True, perform all editing then set batch
        edit to False and it'll save all changes to an item at that point.
        
        Parameters
        ----------
        state : Boolean
        """
        if state == self._batchMode:
            return

        self._batchMode = state
        if not state:
            self._saveAndUpdate()

    @property
    def controlledChannels(self):
        return self.item.getChannelProperty(self.CHAN_CONTROLLED_CHANNELS)
    
    @controlledChannels.setter
    def controlledChannels(self, value):
        """ Sets whether controller should allow for editing transform or user channels.
        
        Parameters
        ----------
        value : ControlledChannels
        """
        if value not in [self.ControlledChannels.TRANSFORM, self.ControlledChannels.USER, self.ControlledChannels.ITEM]:
            return False
        self.item.setChannelProperty(self.CHAN_CONTROLLED_CHANNELS, value)
        self._clearSettings()
        self._deleteChannelSet()
        
        if not self._batchMode:
            service.events.send(e.ITEM_CHANGED, item=self.modoItem)
        return True

    @property
    def channelSet(self):
        """
        Gets channel set for this controller (if there is any).

        Returns
        -------
        ChannelSet

        Raises
        ------
        LookupError
            When there is no channel set associated with this controller.
        """
        if self.controlledChannels != CtrlControlledChannels.USER:
            raise LookupError
        chanSet = self._getChannelSet(autoCreate=True)
        if chanSet is None:
            raise LookupError
        return chanSet

    def updateChannelSetName(self):
        """
        Updates name for channel set tied to this controller (if any).
        """
        if self.controlledChannels != CtrlControlledChannels.USER:
            return

        chanSet = self._getChannelSet(autoCreate=False)
        if chanSet is None:
            return

        chanSet.name = self._renderChannelSetName()

    @property
    def channelSetChannels(self):
        """ This property should return a list of channels that should appear in
        channel set.
        """
        return []

    def getChannelState(self, chanName):
        """ Gets state of a channel by its name.
        
        Returns
        -------
        ChannelState
            descDefaultChannelState is returned when the channel cannot be found.
        """
        try:
            return self._channelStates[chanName]
        except KeyError:
            return self.descDefaultChannelState

    def setChannelState(self, chanName, state):
        """ Set given channel to a desired state (animated, static, etc.)
        """
        if state == self.descDefaultChannelState:
            if chanName in self._channelStates:
                self._channelStates.pop(chanName)
            else:
                return # no need to do anything if channel is already being ignored
        else:
            self._channelStates[chanName] = state

        try:
            self.onSetChannelState(chanName, state)
        except AttributeError:
            pass

        if chanName not in (self.TRANSFORM_CHANNELS):
            channel = self.modoItem.channel(chanName)
            if channel is not None and modox.ChannelUtils.isUserChannel(channel):
                self._userChannelChanged = True

        if not self._batchMode:
            self._saveAndUpdate()

    def onSelected(self):
        """ Call when controller is selected to perform one of predefined actions.
        
        Parameters
        ----------
        action : OnSelectedAction.XXX
        """
        if self.controlledChannels == self.ControlledChannels.TRANSFORM:
            if SetupMode().state and not self.transformToolsEnabledInSetup:
                pass
            else:
                TransformToolsUtils().autoFromChannels(self.channelSetChannels)
        elif self.controlledChannels == self.ControlledChannels.USER:
            chanSet = self._getChannelSet(autoCreate=True)
            chanSet.open()
            return

        # If a channel set is opened.
        # If it is we are in the 'auto channel set switch mode'
        # meaning we try to keep opened channel set current to the module that is being edited.
        # Set logErrors to False so we don't get output in log when the command is disabled.
        chanSetId = run('group.current ? type:chanset', logErrors=False)  # This is returning empty string when no current chan set
        openNewPanel = False

        if chanSetId:
            groupItem = modox.SceneUtils.findItemFast(chanSetId)
            try:
                currentChanSet = ChannelSet(modo.Group(groupItem))
            except TypeError:
                # This channel set doesn't belong to the ACS3 rig
                # so we'll just open new panel for current module.
                openNewPanel = True
                currentChanSet = None

            if currentChanSet is not None:
                # If rig panel is open we need to see to which module it belongs.
                # If it belongs to different module then the controller that was selected
                # we are going to switch to different channel set.
                currentChanSetSourceModoItem = currentChanSet.channelsSourceModoItem
                try:
                    rigItem = Item.getFromModoItem(currentChanSetSourceModoItem)
                except TypeError:
                    rigItem = None

                if rigItem is not None:
                    modRoot = rigItem.moduleRootItem
                    thisModuleRootModoItem = self.item.moduleRootItem
                    if modRoot != thisModuleRootModoItem:
                        openNewPanel = True

            # just fire command!
            if openNewPanel:
                lx.eval('rs.anim.panel')

    @property
    def transformToolsEnabledInSetup(self):
        """ Returns whether the transform tools should be enabled when controller is selected in Setup.
        
        Returns
        -------
        bool
        """
        return True

    # -------- Private methods
    
    def _clearSettings(self):
        self._channelStates = {}
        self._save()

    def _saveAndUpdate(self):
        """ Saves channel states to an item and does any other required updates.
        
        This should be called whenever channel state is changed.
        """
        self._save()
    
        # Send item changed event
        service.events.send(e.ITEM_CHANGED, item=self.modoItem)
        
        # If this is user channel changed we need to tear down and rebuild
        # channel set.
        if self._userChannelChanged:
            self._rebuildAndOpenChannelSet()
            self._userChannelChanged = False

    def _getChannelByName(self, chanName):
        """ Gets channel object by the channel name.
        """
        if chanName in self.POS_CHANNELS:
            locator = modo.LocatorSuperType(self.modoItem.internalItem)
            return locator.position.channel(chanName)
        elif chanName in self.ROT_CHANNELS:
            locator = modo.LocatorSuperType(self.modoItem.internalItem)
            return locator.rotation.channel(chanName)
        elif chanName in self.SCALE_CHANNELS:
            locator = modo.LocatorSuperType(self.modoItem.internalItem)
            return locator.scale.channel(chanName)
        else:
            return self.modoItem.channel(chanName)

    def _getChannelsWithState(self, state):
        """ Gets a list of channels that have given state.
        
        Returns
        -------
        list : modo.Channel
        """
        channels = []
        for chanName in self._channelStates:
            if self._channelStates[chanName] != state:
                continue
            chan = self._getChannelByName(chanName)
            if chan is None:
                if debug.output:
                    log.out("Referenced channel (%s) does not exist anymore on controller: %s" % (chanName, self.modoItem.name), log.MSG_ERROR)
                continue
            channels.append(chan)
        return channels

    def _renderChannelSetName(self):
        return self.item.rigRootItem.name + ' ' + self.item.referenceUserName

    def _getChannelSet(self, autoCreate=True):
        chanSet = None
        try:
            chanSet = ChannelSet(self.modoItem)
        except TypeError:
            # Channel set doesn't exist yet
            if autoCreate:
                name = self._renderChannelSetName()
                chanSet = ChannelSet.new(name, self.channelSetChannels, self.modoItem)
        return chanSet

    def _rebuildAndOpenChannelSet(self):
        chanSet = self._getChannelSet(autoCreate=True)
        chanSet.rebuild(self.channelSetChannels)
        chanSet.open()
        
    def _deleteChannelSet(self):
        chanSet = self._getChannelSet(autoCreate=False)
        if chanSet is not None:
            chanSet.selfDelete()

    def _load(self):
        """ Loads channel states from item settings.
        """
        self._channelStates = SettingsTag(self.modoItem, self._TAG_CONTROLLER_CODE).get(str, str)

    def _save(self):
        """ Saves all channel settings to an item.
        """
        if self._channelStates:
            self._verifyChannelStates()
            SettingsTag(self.modoItem, self._TAG_CONTROLLER_CODE).set(self._channelStates)
        else:
            SettingsTag(self.modoItem, self._TAG_CONTROLLER_CODE).clear()

    def _verifyChannelStates(self):
        """
        Call this to verify if user or item channels referenced in channel states settings still exist.

        Right now this is called right before each save to make sure there are no bad channel references.
        """
        # No reason to validate transform channels since these don't change names anyway.
        if self.controlledChannels == self.ControlledChannels.TRANSFORM:
            return

        deleteKeys = []
        for chanName in self._channelStates:
            chan = self.modoItem.channel(chanName)
            if chan is None:
                deleteKeys.append(chanName)

        for key in deleteKeys:
            del self._channelStates[key]
