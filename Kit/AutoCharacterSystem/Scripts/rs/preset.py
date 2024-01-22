import sys
import time

import lx
import lxu
import modo
import modox

from . import sys_component
from . import const as c
from . import preset_thumb
from .log import log
from .debug import debug
from .util import run
from .util import getTime
from .core import service
from .item_settings import ItemSettings
from .item import Item
from .module import Module


class PresetValuesType(object):
    STATIC = 'static'
    ENVELOPE = 'env'


class DestinationRig(object):
    EDIT = 1
    SELECTED = 2


class ContentItem(object):

    @property
    def channels(self):
        """
        Gets a list of channels stored in the content item.

        Returns
        -------
        [modo.Channel]
        """
        if self._cachedChannels is not None:
            return self._cachedChannels
        xContentItem = modox.Item(self._modoItem.internalItem)
        self._cachedChannels = xContentItem.getUserChannels(sort=False)
        return self._cachedChannels

    @property
    def channelsByIdentifiers(self):
        """
        Gets channels keyed by their identifiers.

        Use this to easily look a channel up.

        Returns
        -------
        {str: modo.Channel}
        """
        if self._channelsByIdentifiers is not None:
            return self._channelsByIdentifiers

        self._channelsByIdentifiers = {}
        for chan in self.channels:
            self._channelsByIdentifiers[modox.ChannelUtils.getChannelUsername(chan)] = chan

        return self._channelsByIdentifiers

    def getItemChannels(self, itemIdentifier):
        """
        Gets all channels stored in preset for a given item.

        itemIdentifier : str
            String identifier of an item in a format in which it's stored within preset channel name.
        """
        itemChannels = []
        for channel in self.channels:
            if channel.name.startswith(itemIdentifier):
                itemChannels.append(channel)
        return itemChannels

    def getChannelValue(self, channelIdentifier):
        """
        Gets value of a given channel from preset.

        If channel has an envelope you'll just get current value at current time.

        Returns
        -------
        float, int
        """
        try:
            presetChannel = self.channelsByIdentifiers[channelIdentifier]
        except KeyError:
            raise LookupError

        return modox.ChannelUtils.getRawChannelValue(presetChannel, None, lx.symbol.s_ACTIONLAYER_EDIT)

    def setChannelValue(self, channelIdentifier, value):
        """
        Sets new value for preset channel.

        Note that this doesn't check what's already there in a channel (if it has envelope for example)
        so it's your responsibility to write proper stuff into the channel.

        Parameters
        ----------
        channelIdentifier : str
            Identifier of channel as stored in a preset.

        value : float, int
            A value to store, make sure it's of correct type yourself!
        """
        try:
            presetChannel = self.channelsByIdentifiers[channelIdentifier]
        except KeyError:
            raise LookupError

        presetChannel.set(value, time=None, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

    def mirror(self):
        """
        Mirrors channels from one side to another.

        Both channel sides and values are mirrored.
        Values are mirrored in the same way as mirroring poses go.
        """
        channels = self.channels
        self._mirrorChannelSides(channels)
        self._mirrorChannelValues(channels)

    # -------- Private methods

    def _mirrorChannelValues(self, channels):
        posXChannelName = modox.c.TransformChannels.PositionX
        # Keep in mind that when checking for channels we need to
        # use channel names as stored in the preset.
        # This is why we remove the dot here because the name
        # will be 'rotX', 'rotY'.
        rotYZChannelNames = [modox.c.TransformChannels.RotationY.replace('.', ''),
                             modox.c.TransformChannels.RotationZ.replace('.', '')]

        for channel in channels:
            mirrorValue = False
            name = channel.name
            if name.startswith('C'):
                # Flip channel value on center channel only if it's rotation Y or Z.
                # Again, we compare last 4 characters only (rotY, rotZ).
                if name[-4:] in rotYZChannelNames:
                    mirrorValue = True

            # Always flip channel value if it's position X.
            if modox.ChannelUtils.getChannelUsername(channel).endswith(posXChannelName):
                mirrorValue = True

            if mirrorValue:
                modox.ChannelUtils.mirrorChannel(channel)

    def _mirrorChannelSides(self, channels):

        for channel in channels:
            username = modox.ChannelUtils.getChannelUsername(channel)
            if username.startswith('C..'):
                continue

            newUsername = ''
            if username.startswith('R..'):
                newUsername = 'L' + username[1:]
            elif username.startswith('L..'):
                newUsername = 'R' + username[1:]

            # Since loading from preset is using channel usernames only
            # we only care about mirroring usernames.
            modox.ChannelUtils.setChannelUsername(channel, newUsername)

    def __init__(self, modoItem):
        self._cachedChannels = None  # this is meant to be list
        self._channelsByIdentifiers = None  # this is meant to be dictionary
        self._modoItem = modoItem


class Preset(sys_component.SystemComponent):
    """ Base class for implementing channel presets.
    
    Channel presets can save a set of channels as lxp preset and load them back onto the rig.
    
    Attributes
    ----------
    descIdentifier : str
        Unique identifier of the preset type: pose, guide, action, etc.
    
    descUsername : str
        User friendly name to display in UI.

    descDestinationRig : int
        One of DestinationRig constants. Defines on which rigs the preset should be applied on drop.
        It can be either edit rig or selected rigs currently (setup vs animation preset really).

    descSupportsDestinationItem : bool
        When preset supports destination item it will be applied to a rig from which the targeted item
        in viewport is. If there's no destination item set by users while dropping then we're falling back
        on the descDestinationRig attribute.

    descValuesType : str
        One of PresetValueType constants. Defines whether the preset is going to store
        a static value or an entire envelope.
    
    descSourceAction : str
        Source action to copy values from. It only really matters for static values.
        For envelopes it is edit action always. Static values are copied from edit action
        by default.
    
    descTargetAction : str
        Target action to paste values to when the preset is loaded.
        Again, for envelopes it is edit action always so this setting concerns static values only.
        Edit action is the default.
    
    descKeyStaticValue : bool
        When set to True static value set by loading preset will create a keyframe.
        Does not have an effect if setup is the target action.
        
    descPresetDescription : str
        Description of the preset that will be shown at the bottom of the thumbnail
        when preset is displayed in PB view.
        
    descThumbnailClass : PresetThumbnail
        Class of the thumbnail that preset is going to use for generating its thumbnails.

    descDefaultThumbnailFilename : str
        Name of the default thumbnail filename. File has to be within registered thumbnails path.
        This attribute is used only when thumbnail class is not provided.

    descContext : str, None
        Identifier of the context the preset should switch the state to.
        When None, current context will not be changed.

    descDefaultButtonName : str
        Default name for the button if no dynamic button name is provided.
        This should really resolve to message table.

    descDefaultIcon : str
        Default icon name. This is used if no dynamic icon name is provided.
    """
    
    DROP_SCRIPT = 'rs_drop_preset'
    TAG_PRESET_IDENTIFIER = 'RSPI'
    TAG_PRESET_IDENTIFIER_INT = lxu.lxID4(TAG_PRESET_IDENTIFIER)
    _SETTINGS_GROUP = 'pst'

    ValuesType = PresetValuesType
    DestinationRig = DestinationRig

    descIdentifier = ''
    descUsername = ''
    descDestinationRig = DestinationRig.EDIT
    descSupportsDestinationItem = False
    descValuesType = ValuesType.STATIC
    descKeyStaticValue = True
    descSourceAction = lx.symbol.s_ACTIONLAYER_EDIT
    descTargetAction = lx.symbol.s_ACTIONLAYER_EDIT
    descPresetDescription = ''
    descThumbnailClass = None
    descDefaultThumbnailFilename = ''
    descContext = None
    descSelectionSensitive = False
    descDefaultButtonName = ''
    descDefaultIcon = ''

    @property
    def descSettings(self):
        """
        Return any extra settings that need to be stored in the preset.

        Returns
        -------
        {str : value}
            Settings need to be returned as dictionary. Key is the name of the setting.
            Value is any kind of value that can be stored via ItemSettings interface.
        """
        return {}

    # -------- System component attributes, do not touch.

    @classmethod
    def sysType(cls):
        return c.SystemComponentType.PRESET
    
    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
   
    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Preset'
    
    @classmethod
    def sysSingleton(cls):
        return False

    # -------- Class methods
    
    @classmethod
    def getPresetClassFromContentItem(cls, contentItem):
        try:
            identifier = contentItem.readTag(cls.TAG_PRESET_IDENTIFIER)
        except LookupError:
            return None

        try:
            return service.systemComponent.get(c.SystemComponentType.PRESET, identifier)
        except LookupError:
            return None

    @classmethod
    def cleanUp(self, contentItem):
        """ Cleans up preset existing in a scene manually.

        Parameters
        ----------
        contentItem : modo.Item
            The item under which all preset content is stored.
        """
        self._cleanUp(contentItem)

    # -------- Virtual methods
    
    def init(self):
        """ Called at the very beginning, before anything else is done.
        """
        return True
    
    def preSave(self):
        """ Called before preset saving happens.
        """
        pass
    
    def postSave(self):
        """ Called after preset file is saved.
        
        Use this method to perform any custom clean up.
        """
        pass
    
    def preLoad(self, settings={}):
        """ Called right before preset is loaded and applied to a rig.

        Parameters
        ----------
        settings: {str : value}
            If preset saves settings the will be available as dictionary here.
        """
        pass
    
    def postLoad(self, settings={}):
        """ Called after the preset has been fully loaded and applied.
        
        Use this method to perform any custom clean up.

        Parameters
        ----------
        settings: {str : value}
            If preset saves settings the will be available as dictionary here.
        """
        pass

    @property
    def channels(self):
        """ Needs to return all channels that should be contained within the preset.
        """
        return []

    @property
    def loadChannels(self):
        """
        Load channels can be a different set than save channels.
        If that's the case - implement this property.
        By default load channels set is the same as save one.
        """
        return self.channels

    @property
    def icon(self):
        """
        Returns name of the icon file to use.
        This is useful in case the icon needs to be dynamic (dependent on selection for example).

        Returns
        -------
        str
        """
        return ''

    @property
    def buttonName(self):
        """
        Returns text to display on the button in case it needs to be dynamic.

        Returns
        -------
        str
        """
        return ''

    # -------- Public interface

    @property
    def destinationItem(self):
        """
        Gets preset's destination item (if any).

        Applies to loading presets only.

        Returns
        -------
        Item
        """
        return self._destinationItem

    @destinationItem.setter
    def destinationItem(self, rigItem):
        """
        Sets preset destination item.

        Note that this shouldn't really be set manually, the system sets it itself
        prior to loading a preset.
        """
        self._destinationItem = rigItem

    @property
    def name(self):
        """
        Gets name of the preset.

        Name is the filename without extension.
        This applies to loading a preset only.

        Returns
        -------
        str
        """
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def contentItem(self):
        return self._contentItem

    def save(self, filename, captureThumb=False):
        """ Saves preset as .lxp.
        
        Parameters
        ----------
        filename : str
            Full filename (including path and file extension) of the preset.
        
        captureThumb : bool
            Whether to grab a custom thumbnail for a preset or use default one.

        Returns
        -------
        bool
            True when preset was saved, False otherwise.
        """
        startTime = getTime()
            
        if not self.init():
            return False
        
        modox.TransformUtils.applyEdit()
        
        thumbCaptured = False
        if captureThumb and self.descThumbnailClass is not None:
            thumb = self.descThumbnailClass()
            thumb.capture()
            thumbCaptured = True

        contentItem = self._spawnPresetAssembly()
        self._storeSettings(contentItem)
        self.preSave()
        self._save(contentItem, filename)
        self.postSave()
        self._cleanUp(contentItem)
        
        if thumbCaptured:
            thumb.setOnPreset(filename)
        elif self.descDefaultThumbnailFilename:
            try:
                thumbFilename = service.path.getFullPathToFile(c.Path.THUMBNAILS, self.descDefaultThumbnailFilename)
            except LookupError:
                pass
            else:
                preset_thumb.PresetThumbnail.setThumbnailImageOnPreset(filename, thumbFilename)

        endTime = getTime()
        if debug.output:
            log.out('Preset saved in: %f' % (endTime - startTime))
    
    def load(self, contentItem, cleanUp=True):
        """ Load preset from a content item.
        
        Parameters
        ----------
        contentItem : modo.Item
            Preset content item.
        """
        start = getTime()

        settings = ItemSettings(contentItem).getGroup(self._SETTINGS_GROUP)
        self._contentItem = ContentItem(contentItem)

        self.preLoad(settings)

        sourceChannels = self._contentItem.channels
        targetChannels = self._storeChannelsByPresetIdent(self.loadChannels)

        if debug.output:
            log.out('Target Channels')
            log.startChildEntries()
            for chanid in list(targetChannels.keys()):
                log.out('%s' % chanid)
            log.stopChildEntries()

        for channel in sourceChannels:
            channelUsername = modox.ChannelUtils.getChannelUsername(channel)
            try:
                targetChannel = targetChannels[channelUsername]
            except KeyError:
                if debug.output:
                    log.out('No matching target channel!')
                continue
            self._applyValues(channel, targetChannel)
            if debug.output:
                log.out('apply channel %s' % channel.name)

        if debug.output:
            log.out('channels in preset: %d' % len(sourceChannels))

        self.postLoad(settings)

        if cleanUp:
            self._cleanUp(contentItem)
        
        end = getTime()
        if debug.output:
            log.out('Preset applied in: %f' % (end - start))

    def renderItemIdentifier(self, rigItem):
        """
        Renders item identifier as used within preset channel username.

        Parameters
        ----------
        rigItem : Item
        """
        return self._renderItemIdentifierString(rigItem)

    def mirrorItemIdentifier(self, identifier):
        """
        Mirrors given item identifier.

        Right gets mirrored to left, left to right and center is left untouched.
        """
        if identifier.startswith('R'):
            return 'L' + identifier[1:]
        elif identifier.startswith('L'):
            return 'R' + identifier[1:]
        return identifier

    def renderChannelIdentifier(self, rigItem, channel):
        """
        Renders channel identifier under which the channel will be stored in preset.

        Parameters
        ----------
        rigItem : Item, str
            This is the item that will be used for creating identifier.
            It's not always the same item as the one from channel!
            Transform channels are stored under their locator item identifier!
            So to store transform channel pass its locator item and transform channel.
            You can also pass string if you have item identifier already.

        channel : modoItem, str, unicode
            Channel to take name from. Or pass string name directly (or unicode).
        """
        # Python 3 doesn't have unicode as all strings are unicode by default.
        # We need to test against unicode in python 2, don't remember why exactly
        # but I think some other function is returning its result as unicode and
        # this function gets called with that.
        typesToTest = [str]
        if self._pyVersion < 3:
            typesToTest = [str, unicode]

        if type(rigItem) in typesToTest:
            itemIdString = rigItem
        else:
            itemIdString = self._renderItemIdentifierString(rigItem)

        if isinstance(channel, str):
            chanName = channel
        else:
            chanName = channel.name
        return itemIdString+ '..' + chanName

    @property
    def rig(self):
        return self._rig

    # -------- Private methods
    
    def _spawnPresetAssembly(self):
        """ Spawns new preset to save.

        Returns
        -------
        modo.Item
        """
        scene = modo.Scene()
        contentItem = scene.addItem('groupLocator', 'RSPresetRoot')
        xContentItem = modox.Item(contentItem.internalItem)
        xContentItem.setTag(self.TAG_PRESET_IDENTIFIER, self.descIdentifier)

        run('!assembly.createScript {%s} item:{%s}' % (self.DROP_SCRIPT, contentItem.id))
            
        channelsToSave = self.channels
        #chanSelection = modox.ChannelSelection()
        channelsDict = self._storeChannelsByPresetIdent(channelsToSave)
        for key in list(channelsDict.keys()):
            channel = channelsDict[key]
            username = key
            name = key.replace('.', '')
            name = name.replace(' ', '')

            userChan = xContentItem.addUserChannel(name, channel.storageType, username)
            # Output channels that could not be stored in a preset.
            if userChan is None:
                if debug.output:
                    log.out('User channel %s was not created, it will not be stored in a preset.' % key, log.MSG_ERROR)
                continue
            self._storeValues(channel, userChan, self.descValuesType)
            
        #modox.TransformUtils.applyEdit()
        return contentItem

    def _storeValues(self, sourceChannel, destChannel, valueType):
        """ Stores values into the preset.
        """
        if valueType == self.ValuesType.ENVELOPE:
            run('select.channel {%s:%s} mode:set' % (sourceChannel.item.id, sourceChannel.name))
            run('channel.copy')
            run('select.channel {%s:%s} mode:set' % (destChannel.item.id, destChannel.name))
            run('channel.paste')
        elif valueType == self.ValuesType.STATIC:
            value = modox.ChannelUtils.getRawChannelValue(sourceChannel, None, self.descSourceAction)  # eval action.
            destChannel.set(value, time=None, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

    def _storeSettings(self, contentItem):
        settings = self.descSettings
        if not settings:
            return
        iset = ItemSettings(contentItem)
        iset.setGroup(self._SETTINGS_GROUP, settings)

    def _applyValues(self, sourceChannel, destChannel):
        """ Applies values from preset to the scene.
        """
        if sourceChannel.isAnimated:
            # Copy envelope
            run('select.channel {%s:%s} mode:set' % (sourceChannel.item.id, sourceChannel.name))
            run('channel.copy')
            run('select.channel {%s:%s} mode:set' % (destChannel.item.id, destChannel.name))
            run('channel.paste')
        else:
            # Copy static value.
            # We copy from edit action, that'll be good because we're copying from preset.
            # We store on the designated target action setting the key only if target action
            # is not setup and the relevant attribute is set to True.
            value = modox.ChannelUtils.getRawChannelValue(sourceChannel, None, lx.symbol.s_ACTIONLAYER_EDIT)
            setKey = self.descKeyStaticValue
            if self.descTargetAction == lx.symbol.s_ACTIONLAYER_SETUP:
                setKey = False
            destChannel.set(value, time=None, key=setKey, action=self.descTargetAction)

    def _save(self, contentItem, filename):
        """ Performs the actual save.
        """
        contentItem.select(replace=True)
        cmd = '!item.selPresetSave type:locator filename:{%s} desc:{%s}' % (filename, self.descPresetDescription)
        run(cmd)

    def _storeChannelsByPresetIdent(self, channels):
        """ Stores a list of channels in dictionary keyed by special id.
        
        Every channel receives unique id based on its side, module ,ident, etc.
        This id is used as channel name when saving preset and when loading the id
        is used to match channels from preset with ones in the scene.
        """
        chansDict = {}
        for channel in channels:
            # To generate channel preset idents I need main item
            # and not its transform. So I need to get main item from transform one first.
            if modox.ItemUtils.isTransformItem(channel.item):
                sourceItem = modox.ItemUtils.getTransformItemHost(channel.item)
            else:
                sourceItem = channel.item

            try:
                rigItem = Item.getFromModoItem(sourceItem)
            except TypeError:
                continue

            try:
                renderedName = self.renderChannelIdentifier(rigItem, channel)
            except TypeError:
                continue

            chansDict[renderedName] = channel
        return chansDict

    def _renderItemIdentifierString(self, rigItem):
        side = rigItem.side
        module = Module(rigItem.moduleRootItem)
        moduleName = module.name.replace(' ', '_') # module name can have spaces
        itemName = rigItem.name.replace(' ', '_') # rig item name can have spaces and these are forbidden in channel names.

        itemType = rigItem.type.replace(' ', '_') # just in case

        sideTrans = {c.Side.RIGHT: 'R', c.Side.LEFT: 'L', c.Side.CENTER: 'C'}
        sideString = sideTrans[side]

        return sideString + '..' + moduleName + '..' + itemType + '..' + itemName

    @classmethod
    def _cleanUp(self, contentItem):
        """ Cleans up preset items from the scene.
        
        This is just single content item on save and content item plus assembly on load.
        """
        connectedGroups = contentItem.connectedGroups
        run('!item.delete item:{%s}' % contentItem.id)
        if connectedGroups is not None: # Will be none and not empty list if there are no connected groups
            for group in connectedGroups:
                run('!item.delete child:1 item:{%s}' % group.id)

    def __init__(self, rig):
        self._rig = rig
        self._scene = modo.Scene()
        self._destinationItem = None
        self._contentItem = None
        self._name = ''
        self._pyVersion = sys.version_info[0]