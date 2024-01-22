
""" This module implements transmitter items.

    Transmitter items serve the same purpose as assembly inputs and outputs
    but are separate items.
"""


import modo
import modox

from . import const as c
from .item import Item
from .util import run


class TransmitDirection(object):
    INPUT = 'i'
    OUTPUT = 'o'


class TransmitterItem(Item):
    
    descType = c.RigItemType.TRANSMITTER
    descUsername = 'Transmitter'
    descModoItemType = 'groupLocator'
    descDefaultName = 'Transmitter'
    descPackages = ['rs.pkg.generic']
    descItemCommand = None

    Direction = TransmitDirection
    
    _SETTING_GROUP = 'trans'
    _SETTING_DIRECTION = 'dir'
    
    @property
    def direction(self):
        return self.settings.getFromGroup(self._SETTING_GROUP, self._SETTING_DIRECTION, self.Direction.INPUT)
    
    @direction.setter
    def direction(self, direction):
        if direction not in (self.Direction.INPUT, self.Direction.OUTPUT):
            return
        self.settings.setInGroup(self._SETTING_GROUP, self._SETTING_DIRECTION, direction)
    
    @property
    def inputs(self):
        if self.direction is not self.Direction.INPUT:
            return []
        return self._getAllChannels()
    
    @property
    def outputs(self):
        if self.direction is not self.Direction.OUTPUT:
            return []
        return self._getAllChannels()

    def onAdd(self, subtype):
        run('select.item {%s} set' % self.modoItem.id)
        run('item.editorColor green')
    
    # -------- Private methods
    
    def _getAllChannels(self):
        pass


class ConnectionsCache(object):
    """ This class is used to cache and then restore input/output channels connections on rig item.
    
    The rig item needs to expose interface with following properties:
    
    inputChannels
    outputChannels
    
    These properties need to return list of modo.Channel for inputs and outputs respectively.
    
    All input/output connections are stored as item settings in a connections cache settings group.
    Upon restore the cache is read back and connections restored.
    
    Channel link items are referenced by identifier and this one doesn't exist
    a string combining rig item name and type is used instead.
    While the second option works it's a fallback really and it's better to give
    identifiers to all items which channels are linked with the rig item that is cached.
    
    Parameters
    ----------
    rigItem : Item
        Rig item which has the input/output connections to be cached/restored.
    """
    def cacheConnections(self):
        inputCache = {}
        outputCache = {}
        
        for chan in self._item.inputChannels:
            connections = []
            for linkchan in chan.revLinked:
                try:
                    rigItem = Item.getFromModoItem(linkchan.item)
                except TypeError:
                    continue
                ident = rigItem.identifierOrNameType
                if ident:
                    connections.append(ident + ':' + linkchan.name)
            inputCache[chan.name] = connections

        self._item.settings.setInGroup('chancnnct', 'in', inputCache)
        
        for chan in self._item.outputChannels:
            connections = []
            for linkchan in chan.fwdLinked:
                try:
                    rigItem = Item.getFromModoItem(linkchan.item)
                except TypeError:
                    continue
                ident = rigItem.identifierOrNameType
                if ident:
                    connections.append(ident + ':' + linkchan.name)
            outputCache[chan.name] = connections

        self._item.settings.setInGroup('chancnnct', 'out', outputCache)
        
    def restoreConnections(self, componentSetup):
        """ Restore connections using given component setup.
        
        Parameters
        ----------
        componentSetup : componentSetup
            A component setup to which the item with cached connections will belong.
            Only items from this component setup will be searched when matching
            item references in cache to actual scene items.
        """
        # Make a list of all item identifiers in the cache.
        itemIdents = {}
        inCache = self._item.settings.getFromGroup('chancnnct', 'in', None)
        if inCache:
            self._initItemIdentsDictFromCache(itemIdents, inCache)
        outCache = self._item.settings.getFromGroup('chancnnct', 'out', None)
        if outCache:
            self._initItemIdentsDictFromCache(itemIdents, outCache)
            
        # Then iterate through component setup and match items to idents.
        self._itemIdents = itemIdents
        componentSetup.iterateOverItems(self._matchComponentItemToIdent)
        
        # Then restore in connections.
        for chanName in list(inCache.keys()):
            chan = self._item.modoItem.channel(chanName)
            if not chan:
                continue
            
            linkChans = self._getLinkChannels(inCache[chanName])
            for linkChan in linkChans:
                linkChan >> chan
        
        # And out connections
        for chanName in list(outCache.keys()):
            chan = self._item.modoItem.channel(chanName)
            if not chan:
                continue
            
            linkChans = self._getLinkChannels(outCache[chanName])
            for linkChan in linkChans:
                chan >> linkChan
    
    def clearCache(self):
        self._item.settings.deleteGroup('chancnnct')

    # -------- Private methods

    def _getLinkChannels(self, chanLinkSet):
        chans = []
        for chanLinkRef in chanLinkSet:
            itemIdent, linkChanName = chanLinkRef.split(':')
            try:
                linkItem = self._itemIdents[itemIdent]
            except KeyError:
                continue
            if linkItem is None:
                continue
            
            linkChan = linkItem.modoItem.channel(linkChanName)
            if linkChan is None:
                continue
            chans.append(linkChan)
        return chans

    def _matchComponentItemToIdent(self, modoItem):
        try:
            rigItem = Item.getFromModoItem(modoItem)
        except TypeError:
            return
        
        ident = rigItem.identifierOrNameType
        if not ident:
            return
        
        if ident in self._itemIdents:
            self._itemIdents[ident] = rigItem
            
    def _initItemIdentsDictFromCache(self, itemIdents, channelCache):
        """
        
        Parameters
        ----------
        itemIdents : dict
        """
        for chanName in list(channelCache.keys()):
            for chanLinkRef in channelCache[chanName]:
                itemIdent, linkChanName = chanLinkRef.split(':')
            
                if itemIdent in itemIdents:
                    continue
                itemIdents[itemIdent] = None
        return itemIdents
    
    def __init__(self, rigItem):
        self._item = rigItem
    