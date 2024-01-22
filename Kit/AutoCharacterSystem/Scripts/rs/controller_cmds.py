

import lx
import modo
import modox

from . import const as c
from . import command as cmd
from .controller_if import Controller
from .core import service


class CmdControllerChannels(cmd.base_OnItemFeatureCommand):
    """ Sets a set of channels that will be editable via controller.
    
    These will be either transform, user or own channels of an item.
    
    Attributes
    ----------
    descControllerClass : class inheriting from Controller
    """

    # -------- Attributes to assign by inheriting class
    
    descControllerClass = None

    @property
    def descIFClassOrIdentifier(self):
        """ Make sure descIFClassOrIdentifier is set to the same class as descControllerClass
        """
        return self.descControllerClass

    # -------- Command body

    ARG_CHANNELS = 'chans'

    UI_HINT = (
        (0, Controller.ControlledChannels.TRANSFORM),
        (1, Controller.ControlledChannels.USER),
        (2, Controller.ControlledChannels.ITEM)
    )

    CHANSET_TO_INT = {Controller.ControlledChannels.TRANSFORM: 0,
                      Controller.ControlledChannels.USER: 1,
                      Controller.ControlledChannels.ITEM: 2}

    INT_TO_CHANSET = {0: Controller.ControlledChannels.TRANSFORM,
                      1: Controller.ControlledChannels.USER,
                      2: Controller.ControlledChannels.ITEM}

    def arguments(self):
        superArgs = cmd.base_OnItemFeatureCommand.arguments(self)
        
        content = cmd.Argument(self.ARG_CHANNELS, 'integer')
        content.flags = 'query'
        content.defaultValue = Controller.ControlledChannels.TRANSFORM
        content.hints = self.UI_HINT

        return [content] + superArgs

    def execute(self, msg, flags):
        chans = self.getArgumentValue(self.ARG_CHANNELS)
        for ctrl in self.itemFeaturesToEdit:
            ctrl.controlledChannels = self.INT_TO_CHANSET[chans]
        self._notify()

    def query(self, argument):
        if argument == self.ARG_CHANNELS:
            ctrl = self.itemFeatureToQuery
            if ctrl is not None:
                return self.CHANSET_TO_INT[ctrl.controlledChannels]

    def _notify(self):
        service.notify(c.Notifier.CONTROLLER, c.Notify.DATATYPE)


class CmdControllerChannelState(cmd.base_OnItemFeatureCommand):
    """ Base class for setting or querying the state of controller channel.

    Attributes
    ----------
    descControllerClass : class inheriting from Controller (item feature)
    """

    # -------- Attributes
    
    descControllerClass = None
    
    @property
    def descIFClassOrIdentifier(self):
        return self.descControllerClass

    # -------- Command body
    
    ARG_CHAN_NAME = 'chanName'
    ARG_STATE = 'state'

    XFRM_MAP = {'pos.X': 'Position X',
                'pos.Y': 'Y',
                'pos.Z': 'Z',
                'rot.X': 'Rotation X',
                'rot.Y': 'Y',
                'rot.Z': 'Z',
                'scl.X': 'Scale X',
                'scl.Y': 'Y',
                'scl.Z': 'Z'}

    def arguments(self):
        superArgs = cmd.base_OnItemFeatureCommand.arguments(self)
        
        chanName = cmd.Argument(self.ARG_CHAN_NAME, 'string')
        chanName.defaultValue = ''

        state = cmd.Argument(self.ARG_STATE, 'integer')
        state.flags = 'query'
        state.defaultValue = 0
        state.valuesList = self._buildPopup()
        state.valuesListUIType = cmd.ArgumentValuesListType.POPUP

        return [chanName, state] + superArgs

    def basic_ButtonName(self):
        chanName = self.getArgumentValue(self.ARG_CHAN_NAME)
        chanUsername = ''

        try:
            chanUsername = self.XFRM_MAP[chanName]
        except KeyError:
            ctrl = self.itemFeatureToQuery
            index = ctrl.modoItem.channel(chanName).index
            chanService = lx.service.ChannelUI()
            chanUsername = chanService.ChannelUserName(ctrl.modoItem.internalItem, index)

        if not chanUsername:
            chanUsername = chanName
        return chanUsername
    
    def setupMode(self):
        return True

    def execute(self, msg, flags):
        chanName = self.getArgumentValue(self.ARG_CHAN_NAME)
        if not chanName:
            return
        # Note that state is an index here.
        stateIndex = self.getArgumentValue(self.ARG_STATE)

        try:
            stateKey = self.descControllerClass.descChannelStatesUIOrder[stateIndex]
        except ValueError:
            return
        
        for ctrl in self.itemFeaturesToEdit:
            ctrl.setChannelState(chanName, stateKey)

    def query(self, argument):
        ident = self.getArgumentValue(self.ARG_CHAN_NAME)
        if not ident:
            return 0

        if argument == self.ARG_STATE:
            ctrl = self.itemFeatureToQuery
            if ctrl is not None:
                state = ctrl.getChannelState(ident)
                try:
                    return self.descControllerClass.descChannelStatesUIOrder.index(state)
                except ValueError:
                    pass
        return 0

    def notifiers(self):
        notifiers = cmd.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers

    # -------- Private methods
    
    def _buildPopup(self):
        """ Builds a list of two element tuples.
        """
        popup = []
        for stateKey in self.descControllerClass.descChannelStatesUIOrder:
            entry = (stateKey, self.descControllerClass.descChannelStatesUsernames[stateKey])
            popup.append(entry)
        return popup


class CmdControllerChannelsFCL(cmd.base_OnItemFeatureCommand):
    """ Generate command list with all the channels that a controller can drive.

    Attributes
    ----------
    descControllerClass : class inheriting from Controller
    
    descChannelStateCommand : str
        Name of the command that allows for querying/setting states of individual
        item channels.
    """

    # -------- Attributes

    descControllerClass = None 
    descChannelStateCommand = ''

    @property
    def descIFClassOrIdentifier(self):
        """ Make sure descIFClassOrIdentifier is set to the same class as descControllerClass
        """
        return self.descControllerClass

    # -------- Command body

    FCL_DIVIDER = '- '

    ARG_CHAN_SET = 'chanSet'
    ARG_CMD_LIST = 'cmdList'
    ARG_DIVIDER = 'divider'

    POS_CHANNELS = ['pos.X', 'pos.Y', 'pos.Z'] 
    ROT_CHANNELS = ['rot.X', 'rot.Y', 'rot.Z']
    SCL_CHANNELS = ['scl.X', 'scl.Y', 'scl.Z']

    SET_MAP = {'pos': POS_CHANNELS,
               'rot': ROT_CHANNELS,
               'scl': SCL_CHANNELS}

    def arguments(self):
        superArgs = cmd.base_OnItemFeatureCommand.arguments(self)
                
        chanSet = cmd.Argument(self.ARG_CHAN_SET, 'string')
        chanSet.defaultValue = 'user'

        cmdList = cmd.Argument(self.ARG_CMD_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFromCommandList
        cmdList.valuesListUIType = cmd.ArgumentValuesListType.FORM_COMMAND_LIST
        
        divider = cmd.Argument(self.ARG_DIVIDER, 'boolean')
        divider.flags = 'optional'
        divider.defaultValue = False

        return [chanSet, cmdList, divider] + superArgs

    def execute(self, msg, flags):
        pass

    def query(self, argIndex):
        pass

    def notifiers(self):
        notifiers = []
        notifiers.append(('select.event', 'item element+t'))
        notifiers.append((c.Notifier.CONTROLLER, ''))
        return notifiers

    def _buildFromCommandList(self):
        """
        Builds a list of channels that can be edited on a controller.
        The list depends on what kind of channels are set to be controlled:
        transform, user or item channels.
        """
        commandList = []
        setName = self.getArgumentValue(self.ARG_CHAN_SET)

        chanNames = []
        ctrl = self.itemFeatureToQuery
        if ctrl is None:
            return []

        if (setName in ('pos', 'rot', 'scl') and
              ctrl.controlledChannels == self.descControllerClass.ControlledChannels.TRANSFORM):
            try:
                chanNames = self.SET_MAP[setName]
            except KeyError:
                pass

        elif (setName == self.descControllerClass.ControlledChannels.USER and
            ctrl.controlledChannels == self.descControllerClass.ControlledChannels.USER):
            # We can only allow numeric user channels and dividers
            item = modox.Item(ctrl.modoItem.internalItem)
            channels = item.getUserChannels(sort=True)
            chanNames = []
            chanUtils = modox.ChannelUtils
            for chan in channels:
                if chanUtils.isNumericChannel(chan):
                    chanNames.append(chan.name)
                elif chanUtils.isDivider(chan):
                    chanNames.append(self.FCL_DIVIDER)

        elif (setName == self.descControllerClass.ControlledChannels.ITEM and
              ctrl.controlledChannels == self.descControllerClass.ControlledChannels.ITEM):
            chanNames = modox.ChannelUtils.getNumericItemChannelNames(ctrl.modoItem)

        if chanNames:
            if self.getArgumentValue(self.ARG_DIVIDER):
                commandList.append(self.FCL_DIVIDER)
            for chanName in chanNames:
                if chanName == self.FCL_DIVIDER:
                    commandList.append(self.FCL_DIVIDER)
                    continue
                commandList.append("%s chanName:{%s} state:?" % (self.descChannelStateCommand, chanName))
        return commandList


class CmdControllerChanPresetChoice(cmd.base_OnItemFeatureCommand):
    """ Displays a popover with a choice of channel state presets to apply to controller.

    Attributes
    ----------
    descControllerClass : Controller
        A class inheriting from controller item feature base class that implements
        the controller item feature.
    
    descFormIdentifier : str
        Identifier of a form that should pop up.
        The form should include a list of all channel preset choices for this controller type.
    """
    
    # -------- Attributes
    
    descControllerClass = None
    descFormIdentifier = ''

    @property
    def descIFClassOrIdentifier(self):
        """ Make sure descIFClassOrIdentifier is set to the same class as descControllerClass
        """
        return self.descControllerClass

    ARG_TYPE = 'type'

    def arguments(self):
        superArgs = cmd.base_OnItemFeatureCommand.arguments(self)
                
        argType = cmd.Argument(self.ARG_TYPE, 'string')
        argType.defaultValue = Controller.ControlledChannels.TRANSFORM

        return [argType] + superArgs

    def enable(self, msg):
        ctrl = self.itemFeatureToQuery
        if ctrl is None:
            return False
        return ctrl.controlledChannels == self.getArgumentValue(self.ARG_TYPE)

    def execute(self, msg, flags):
        lx.eval('attr.formPopover form:{%s}' % self.descFormIdentifier)


class CmdControllerChannelsPreset(cmd.base_OnItemFeatureCommand):
    """ This command sets one of the channel sets presets on a given controller.
    
    Attributes
    ----------
    descControllerClass : Controller
        A class inheriting from controller item feature base class that implements
        the controller item feature.
    
    descXfrmChannelsStates : dict
        Dictionary that defines which channel state value is assigned to True and False
        in a channel preset (True is channel included in preset, False is channel not
        present in a preset).
        An example:
        {True : s.ANIMATED,
         False : s.LOCKED}
    
    descUserChannelsStates : dict
        User channel presets toggle all user channels at once to a given state.
        This dictionary needs to list list the states that user can apply.
        
    descUserPresetsLabels : dict
        Same as above but dictionary values are labels for preset buttons.

    """

    # -------- Attributes
    
    descControllerClass = None
    descXfrmChannelsStates = {}
    descUserChannelsStates = {}
    descUserPresetsLabels = {}

    @property
    def descIFClassOrIdentifier(self):
        """ Make sure descIFClassOrIdentifier is set to the same class as descControllerClass
        """
        return self.descControllerClass

    # -------- Constants
    
    xfrmPresets = {
    'pos': Controller.POS_CHANNELS,
    'rot': Controller.ROT_CHANNELS,
    'scl': Controller.SCALE_CHANNELS,
    'posrot': Controller.POS_CHANNELS + Controller.ROT_CHANNELS,
    'all': Controller.POS_CHANNELS + Controller.ROT_CHANNELS + Controller.SCALE_CHANNELS,
    'px': ['pos.X'],
    'py': ['pos.Y'],
    'pz': ['pos.Z'],
    'rx': ['rot.X'],
    'ry': ['rot.Y'],
    'rz': ['rot.Z']
    }

    xfrmLabels = {
    'pos': 'Position',
    'rot': 'Rotation',
    'scl': 'Scale',
    'posrot': 'Position & Rotation',
    'all': 'All Transforms',
    'px': 'Position X',
    'py': 'Position Y',
    'pz': 'Position Z',
    'rx': 'Rotation X',
    'ry': 'Rotation Y',
    'rz': 'Rotation Z'
    }

    ARG_TYPE = 'type'
    ARG_PRESET = 'preset'

    def arguments(self):
        superArgs = cmd.base_OnItemFeatureCommand.arguments(self)
                
        argType = cmd.Argument(self.ARG_TYPE, 'string')
        
        argPreset = cmd.Argument(self.ARG_PRESET, 'string')
        argPreset.defaultValue = 'posrot'

        return [argType, argPreset] + superArgs

    def enable(self, msg):
        ctrl = self.itemFeatureToQuery
        if ctrl is None:
            return False
        return ctrl.controlledChannels == self.getArgumentValue(self.ARG_TYPE)

    def setupMode(self):
        return True

    def basic_ButtonName(self):
        chansType = self.getArgumentValue(self.ARG_TYPE)
        preset = self.getArgumentValue(self.ARG_PRESET)
        if chansType == Controller.ControlledChannels.TRANSFORM:
            try:
                return self.xfrmLabels[preset]
            except KeyError:
                pass
        elif chansType == Controller.ControlledChannels.USER:
            try:
                return self.descUserPresetsLabels[preset]
            except KeyError:
                pass

        return modox.Message.getMessageTextFromTable(c.MessageTable.GENERIC, 'unknown')

    def execute(self, msg, flags):
        chansType = self.getArgumentValue(self.ARG_TYPE)
        preset = self.getArgumentValue(self.ARG_PRESET)

        controllers = self.itemFeaturesToEdit
        if not controllers:
            return
        
        # Transform channels
        if chansType == Controller.ControlledChannels.TRANSFORM:
            try:
                animChannels = self.xfrmPresets[preset]
            except KeyError:
                return
            
            xfrmChannels = Controller.POS_CHANNELS + Controller.ROT_CHANNELS + Controller.SCALE_CHANNELS
            
            for ctrl in controllers:
                ctrl.batchEdit = True
                for chanName in xfrmChannels:
                    if chanName in animChannels:
                        ctrl.setChannelState(chanName, self.descXfrmChannelsStates[True])
                    else:
                        ctrl.setChannelState(chanName, self.descXfrmChannelsStates[False])
                ctrl.batchEdit = False

        # User channels
        elif chansType == Controller.ControlledChannels.USER:
            try:
                userState = self.descUserChannelsStates[preset]
            except KeyError:
                return
            
            for ctrl in controllers:
                ctrl.batchEdit = True
                
                item = modox.Item(ctrl.modoItem.internalItem)
                channels = item.getUserChannels(sort=False)
                #chanNames = []
                chanUtils = modox.ChannelUtils
                for chan in channels:
                    if chanUtils.isNumericChannel(chan):
                        ctrl.setChannelState(chan.name, userState)
                ctrl.batchEdit = False

        self._notify()

    def notifiers(self):
        notifiers = []
        notifiers.append(('select.event', 'item element+t'))
        notifiers.append((c.Notifier.CONTROLLER, ''))
        return notifiers

    # -------- Private methods

    def _notify(self):
        service.notify(c.Notifier.CONTROLLER, c.Notify.DATATYPE)

