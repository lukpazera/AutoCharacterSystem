
""" ACS2 module contains tools that concern converting to/from ACS2 assets.
"""


import modo
import modox
from . import const as c
from .log import log as log
from .items.generic import GenericItem
from .items.guide import GuideItem
from .items.bind_loc import BindLocatorItem
from .item_feature_op import ItemFeatureOperator
from .item_features.controller import ControllerChannelState
from .item_features.controller_guide import ControllerChannelState as GuideControllerChannelState
from .controller_if import Controller
from .controller_if import CtrlControlledChannels as ControlledChannels
from .util import run


class ItemType(object):
    
    CTRL = 1
    EDIT_GUIDE = 2
    GUIDE = 3
    BIND_LOCATOR = 4
    RETARGET_LOCATOR = 5
    PLUG = 6
    SOCKET = 7
    INTRANSMITTER = 8
    OUTTRANSMITTER = 9
    GUIDE_BUFFER = 10


class ItemTypeSuffix(object):
    
    EDITGUIDE = '(Edit)'
    CTRL = '(Ctrl)'
    SLIDERS = '(Sliders)'
    CHANNELCTRL = '(Channel)'
    GUIDE = '(Guide)'
    GUIDE_BUFFER = '(Guided)'
    BIND = '(Bind)'
    MIRROR = '(Mirror)'
    POSEINF = '(JointInf)'
    GENINF = '(Influence)'
    MORPHDFRM = '(MorphDeform)'
    WCONTAINER = '(Container)'
    SEGMENT = '(Segment)'
    RETARGET = '(Retarget)'
    PLUG = '(Plug)'
    SOCKET = '(Socket)'
    INTRANSMITTER = '(InTrans)'
    OUTTRANSMITTER = '(OutTrans)'

    
class Name(object):
    
    PREFIX_SEPARATOR = '__'
    SUFFIX_SEPARATOR = ' '
    SUFFIX_ASSEMBLY = '_Assm'
    PREFIX_RIGHT_SIDE = 'R.'
    PREFIX_LEFT_SIDE = 'L.'

    @classmethod
    def removePrefix(self, name):
        """ Removes rig name prefix from given name.
        """
        p = name.partition(self.PREFIX_SEPARATOR)
        if p[2]:
            return p[2]
        return name

    @classmethod
    def removeSuffix(self, name):
        """ Removes suffix such as (Ctrl), etc.
        """
        # If right partitioning works the name before the suffix 
        # separator will be in p[0]. If it fails p[0]
        # is empty and whole name as it was is in p[2]
        p = name.rpartition(self.SUFFIX_SEPARATOR)
        if p[0]:
            return p[0]
        else:
            return name

    @classmethod
    def removeAssemblySuffix(self, name):
        """ Removes suffix of an ACS2 assembly item.
        """
        if name.endswith(self.SUFFIX_ASSEMBLY):
            index = len(name) - len(self.SUFFIX_ASSEMBLY)
            return name[:index]
        return name
    
    @classmethod
    def removeSide(self, name):
        """ Cuts side prefix out of the given name.
        
        For example:
        Rig__R.Arm -> Rig__Arm
        """
        sideIndex = name.find(self.PREFIX_RIGHT_SIDE)
        preIndex = 0
        postIndex = len(name)

        if sideIndex > -1:
            preIndex = sideIndex - 1
            postIndex = sideIndex + 2
        else:
            sideIndex = name.find(self.PREFIX_LEFT_SIDE)
            if sideIndex > -1:
                preIndex = sideIndex - 1
                postIndex = sideIndex + 2
        
        nameWithNoSide = ''
        if preIndex > 0:
            nameWithNoSide = name[:preIndex]
        if postIndex < len(name):
            nameWithNoSide += name[postIndex:]
        
        if nameWithNoSide:
            return nameWithNoSide
        else:
            return name

    @classmethod
    def getBasename(self, name):
        """ Extracts basename from full ACS2 name.
        """
        basename = self.getBasenameAndSide(name)
        basename = self.removeSide(basename)
        return basename

    @classmethod
    def getBasenameAndSide(self, name):
        """ Extracts basename with side prefix from ACS2 name.
        """
        basename = self.removePrefix(name)
        basename = self.removeSuffix(basename)
        return basename
    
    @classmethod
    def getSideFromName(self, name):
        """ Gets ACS3 side from ACS2 item name.
        """
        if name.find(self.PREFIX_RIGHT_SIDE) > -1:
            return c.Side.RIGHT
        elif name.find(self.PREFIX_LEFT_SIDE) > -1:
            return c.Side.LEFT

        return c.Side.CENTER

    @classmethod
    def getTypeFromName(self, name):
        """ Gets rig item type from its name.
        
        Returns
        -------
        ItemType, None
        """
        if name.rfind(ItemTypeSuffix.CTRL) > -1:
            return ItemType.CTRL
        elif name.rfind(ItemTypeSuffix.EDITGUIDE) > -1:
            return ItemType.EDIT_GUIDE
        elif name.rfind(ItemTypeSuffix.GUIDE) > -1:
            return ItemType.GUIDE
        elif name.rfind(ItemTypeSuffix.GUIDE_BUFFER) > -1:
            return ItemType.GUIDE_BUFFER
        elif name.rfind(ItemTypeSuffix.BIND) > -1:
            return ItemType.BIND_LOCATOR
        elif name.rfind(ItemTypeSuffix.RETARGET) > -1:
            return ItemType.RETARGET_LOCATOR
        elif name.rfind(ItemTypeSuffix.PLUG) > -1:
            return ItemType.PLUG
        elif name.rfind(ItemTypeSuffix.SOCKET) > -1:
            return ItemType.SOCKET
        elif name.rfind(ItemTypeSuffix.INTRANSMITTER) > -1:
            return ItemType.INTRANSMITTER
        elif name.rfind(ItemTypeSuffix.OUTTRANSMITTER) > -1:
            return ItemType.OUTTRANSMITTER

        return None


class Item(object):
    
    @classmethod
    def isACS2Item(cls, modoItem):
        """ Tests whether an item is ACS2 item.
        
        Returns
        -------
        bool
        """
        try:
            v = modoItem.readTag('RGID')
        except LookupError:
            return False
        return True
        
    @classmethod
    def convertACS2ItemToRS(cls, modoItem):
        """ Converts ACS2 item to ACS3 one.
        """
        if not cls.isACS2Item(modoItem):
            return

        acsType = Name.getTypeFromName(modoItem.name)
        if acsType == ItemType.CTRL:
            cls._convertToController(modoItem)
        elif acsType == ItemType.EDIT_GUIDE:
            cls._convertToEditGuide(modoItem)
        elif acsType == ItemType.GUIDE:
            cls._convertToGuide(modoItem)
        elif acsType == ItemType.GUIDE_BUFFER:
            cls._convertToGuideBuffer(modoItem)
        elif acsType == ItemType.BIND_LOCATOR:
            cls._convertToBindLocator(modoItem)
        elif acsType == ItemType.RETARGET_LOCATOR:
            cls._convertToRetargetLocator(modoItem)
        elif acsType == ItemType.PLUG:
            pass
        elif acsType == ItemType.SOCKET:
            pass
        else:
            cls._convertToGeneric(modoItem)            
            
    # -------- Private methods
    
    @classmethod
    def _convertToGeneric(cls, modoItem):
        if not modox.Item(modoItem.internalItem).isOfXfrmCoreSuperType:
            return
        
        try:
            GenericItem.newFromExistingItem(modoItem, name=Name.getBasename(modoItem.name))
        except TypeError:
            log.out('Cannot convert %s ACS2 item to generic ACS3 item.' % modoItem.name, log.MSG_ERROR)

    @classmethod
    def _convertToController(cls, modoItem):
        try:
            ctrlItem = GenericItem.newFromExistingItem(modoItem, name=Name.getBasename(modoItem.name))
        except TypeError:
            return
        features = ItemFeatureOperator(ctrlItem)
        ctrlFeature = features.addFeature(c.ItemFeatureType.CONTROLLER)

        if modoItem.name.rfind(ItemTypeSuffix.CHANNELCTRL) > -1:
            ctrlFeature.batchEdit = True
            ctrlFeature.controlledChannels = ControlledChannels.USER

        stateMap = {Util.CHAN_ANIM: ControllerChannelState.ANIMATED,
                    Util.CHAN_STATIC: ControllerChannelState.STATIC,
                    Util.CHAN_LOCK: ControllerChannelState.LOCKED,
                    Util.CHAN_IGNORE: ControllerChannelState.IGNORE}
            
        channelStates = Util.parseChannelsTag(modoItem, stateMap)
        if channelStates:
            ctrlFeature.batchEdit = True
            for chanName in list(channelStates.keys()):
                ctrlFeature.setChannelState(chanName, channelStates[chanName])
        
        if ctrlFeature.batchEdit:
            ctrlFeature.batchEdit = False

    @classmethod
    def _convertToEditGuide(cls, modoItem):
        try:
            guideItem = GuideItem.newFromExistingItem(modoItem, name=Name.getBasename(modoItem.name))
        except TypeError:
            return

        features = ItemFeatureOperator(guideItem)
        ctrlFeature = features.addFeature(c.ItemFeatureType.CONTROLLER_GUIDE)
        
        stateMap = {Util.CHAN_ANIM: GuideControllerChannelState.EDIT,
                    Util.CHAN_LOCK: GuideControllerChannelState.LOCKED,
                    Util.CHAN_IGNORE: GuideControllerChannelState.IGNORE}

        channelStates = Util.parseChannelsTag(modoItem, stateMap)
        if channelStates:
            ctrlFeature.batchEdit = True
            for chanName in list(channelStates.keys()):
                ctrlFeature.setChannelState(chanName, channelStates[chanName])
            ctrlFeature.batchEdit = False

    @classmethod
    def _convertToGuide(cls, modoItem):
        try:
            guideItem = GuideItem.newFromExistingItem(modoItem, name=Name.getBasename(modoItem.name))
        except TypeError:
            return
        
        run('select.item {%s} set' % modoItem.id)
        run('item.editorColor purple')

    @classmethod
    def _convertToGuideBuffer(cls, modoItem):
        name = Name.getBasename(modoItem.name) + '_GuideBuffer'
        try:
            rigItem = GenericItem.newFromExistingItem(modoItem, name=name)
        except TypeError:
            return

        features = ItemFeatureOperator(rigItem)
        guideFeature = features.addFeature(c.ItemFeatureType.GUIDE)
        guideFeature.isBufferItem = True

        run('select.item {%s} set' % modoItem.id)
        run('item.editorColor grey')
        
    @classmethod
    def _convertToBindLocator(cls, modoItem):
        try:
            blocItem = BindLocatorItem.newFromExistingItem(modoItem, name=Name.getBasename(modoItem.name))
        except TypeError:
            return

    @classmethod
    def _convertToRetargetLocator(cls, modoItem):
        name = Name.getBasename(modoItem.name) + '_Retarget'
        try:
            rigItem = GenericItem.newFromExistingItem(modoItem, name=name)
        except TypeError:
            log.out('Cannot convert %s ACS2 item to retarget locator ACS3 item.' % modoItem.name, log.MSG_ERROR)


class Util(object):
    
    CHAN_ANIM = '#'
    CHAN_STATIC = '+'
    CHAN_LOCK = '='
    CHAN_IGNORE = '-'

    @classmethod
    def parseChannelsTag(cls, modoItem, stateMap):
        """ Returns channel states based on a channels tag of a given ACS2 item.
        
        Returns
        -------
        dict : (channelName: channelState)
        """
        try:
            chansTag = modoItem.readTag('RGCH')
        except LookupError:
            return None

        allChannels = {}

        chans = []
        for chunk in chansTag.split(' '):
            # Skip empty chunks, can happen when there are multiple spaces
            # separating chunks.
            if not chunk:
                continue

            if chunk[0] == 'p':
                chans = Controller.POS_CHANNELS
            elif chunk[0] == 'r':
                chans = Controller.ROT_CHANNELS
            elif chunk[0] == 's':
                chans = Controller.SCALE_CHANNELS
            elif chunk[0] == 'u':
                chans = modox.Item(modoItem.internalItem).getUserChannelsNames(sort=True)
                chansFiltered = []
                # Filter dividers out.
                # Dividers in ACS2 are channels that start with 'div'.
                for chan in chans:
                    if chan.startswith('div'):
                        continue
                    chansFiltered.append(chan)
                chans = chansFiltered
        
            chunk = chunk[1:]
            for x in range(len(chunk)):
                if x >= len(chans):
                    continue
                chanState = ControllerChannelState.IGNORE
                try:
                    chanState = stateMap[chunk[x]]
                except KeyError:
                    pass

                # Don't lock settings user channels.
                # They have lock state but we'll use ignore for now.
                if chunk[0] == 'u' and chanState == ControllerChannelState.LOCKED:
                    chanState = ControllerChannelState.IGNORE
    
                allChannels[chans[x]] = chanState

        return allChannels
    
