
import lx
import modo
import modox

from ..util import run
from ..item import Item
from ..item_utils import ItemUtils
from .. import const as c
from ..log import log
from ..xfrm_link import TransformLink
from .socket import SocketItem
from ..core import service
from ..item_features.item_link import ItemLinkFeature


class ConnectionType(object):
    STATIC = 'static'
    DYNAMIC = 'dynamic'

class PlugItem(Item):

    CHAN_CONNECTION = 'rsConnection'
    GRAPH_ITEM_LINK = 'rs.itemLink'
    _GRAPH_LINKED_BIND_LOC = "rs.plugBindLoc"
    _CHAN_SOCKET_WORLD_POS = 'rspgSocWPos'
    _CHAN_SOCKET_WORLD_ROT = 'rspgSocWRot'
    _CHAN_SOCKET_WORLD_SCL = 'rspgSocWScl'
    _CHAN_PARENT_POS_OFFSET_X = 'rspgPPosOffset.X'
    _CHAN_PARENT_POS_OFFSET_Y = 'rspgPPosOffset.Y'
    _CHAN_PARENT_POS_OFFSET_Z = 'rspgPPosOffset.Z'
    _CHAN_PARENT_ROT_OFFSET_X = 'rspgPRotOffset.X'
    _CHAN_PARENT_ROT_OFFSET_Y = 'rspgPRotOffset.Y'
    _CHAN_PARENT_ROT_OFFSET_Z = 'rspgPRotOffset.Z'

    Connection = ConnectionType

    # -------- Attributes
    
    descType = 'plug'
    descUsername = 'Plug'
    descModoItemType = 'locator'
    descDefaultName = 'Plug'
    descPackages = ['rs.pkg.plug', 'rs.pkg.generic']
    descDropScriptSource = c.DropScript.ITEM_ON_ITEM_SOURCE
    descDropScriptDestination = c.DropScript.ITEM_ON_ITEM_DESTINATION
    descItemCommand = c.ItemCommand.GENERIC
    
    # -------- Public methods
        
    def onAdd(self, subtype):
        modoItem = self.modoItem
        ident = modoItem.id
        
        if not modoItem.internalItem.PackageTest("glItemShape"):
            modoItem.PackageAdd("glItemShape")

        run('!channel.value custom channel:{%s:drawShape}' % ident)
        run('!channel.value sphere channel:{%s:isShape}' % ident)
        run('!channel.value true channel:{%s:isAlign}' % ident)
        run('!channel.value 0.025 channel:{%s:isRadius}' % ident)
        run('!channel.value false channel:{%s:isSolid}' % ident)
    
        run('select.item {%s} set' % ident)
        run('item.editorColor red')

        # Set color
        run('!rs.item.color plug autoAdd:true item:{%s}' % self.modoItem.id)
        
        # Add item link, disabled by default.
        run('!rs.item.feature itmlink true')
        run('!channel.value true channel:{%s:rsilEnable}' % ident)
        run('!channel.value 2 channel:{%s:rsilThickness}' % ident)
        run('!channel.value dashlong channel:{%s:rsilPattern}' % ident)

    def onDroppedOnItem(self, modoItem, context):
        """ Performs action when a plug is dropped onto an item.
        
        When plug is dropped onto socket we connect the plug to
        the socket. 
        When plug is dropped on some other item that belongs to the same module
        as the plug we diconnect the plug (if it was connected to socket already).
        """

        if context != c.Context.ASSEMBLY:
            return

        try:
            socketItem = SocketItem(modoItem)
        except TypeError:
            socketItem = None
        else:
            self.connectToSocket(socketItem)
            return

        try:
            rigItem = ItemUtils.getItemFromModoItem(modoItem)
        except TypeError:
            return

        if rigItem.moduleRootItem == self.moduleRootItem:
            self.disconnectFromSocket()
    
    def connectToSocket(self, socketItem, drawConnection=True):
        """ Connects plug to the socket.

        Socket has to be from different module.

        When a plug is already connected to another socket it will be
        automatically disconnected from that socket in a silent way -
        meaning there will be no plug disconnected event sent.
        
        Parameters
        ----------
        socketItem : SocketItem
            Socket item to connect to.
        """
        if not isinstance(socketItem, SocketItem):
            try:
                socketItem = SocketItem(socketItem)
            except TypeError:
                return

        if socketItem.moduleRootItem == self.moduleRootItem:
            return

        # Creating new link automatically removes any previous links
        # that might be there. This equals disconnecting from previous socket.
        xfrmLink = TransformLink.new(self.modoItem, socketItem.modoItem, c.TransformLinkType.DYNA_PARENT_NO_SCALE)
        # However, transforms may still be linked so clear them before setting new transform links.
        self._unlinkWorldTransforms()

        self._linkWorldTransforms(socketItem.modoItem)
        self._drawConnection(drawConnection, socketItem.modoItem)

        # Be sure to store up to date position offset from socket.
        self.cacheParentTransformOffset()

        # Send an event that the plug was connected
        service.events.send(c.EventTypes.PLUG_CONNECTED, plug=self, socket=socketItem)

    def disconnectFromSocket(self):
        """ Disconnects plug from socket if it was already connected.
        """
        try:
            xfrmLink = TransformLink(self.modoItem)
        except TypeError:
            # It may still be bad connection, get rid of it.
            TransformLink.clearFromItemIfNotValid(self.modoItem)
            return
        try:
            socketItem = SocketItem(xfrmLink.driverItem)
        except TypeError:
            log.out('Disconnecting a plug failed!', log.MSG_ERROR)
            return

        xfrmLink.remove()
        self._unlinkWorldTransforms()
        self._drawConnection(False)

        # Update position offset from socket after disconneting..
        self.cacheParentTransformOffset()

        # Send an event that the plug was disconnected
        service.events.send(c.EventTypes.PLUG_DISCONNECTED, plug=self, socket=socketItem)

    @property
    def isConnected(self):
        """ Tests whether plug is connected to a socket.
        
        Returns
        -------
        bool
        """
        return self.socket is None

    def cleanUpConnection(self):
        """
        Cleans up plug connections meaning connection will be removed if it's orphaned one
        and doesn't have socket at the other end.
        """
        try:
            xfrmLink = TransformLink(self.modoItem)
        except TypeError:
            return None
        if xfrmLink.drivenItem is None:
            xfrmLink.remove()
            
    @property
    def socket(self):
        """ Gets socket item to which this plug is connected.
        
        Returns
        -------
        SocketItem, None
        """
        try:
            xfrmLink = TransformLink(self.modoItem)
        except TypeError:
            return None
        
        driver = xfrmLink.driverItem
        if driver is None:
            return None
        
        try:
            return SocketItem(driver)
        except TypeError:
            return None

    @property
    def linkedBindLocatorModoItem(self):
        connected = modox.ItemUtils.getReverseGraphConnections(self.modoItem, self._GRAPH_LINKED_BIND_LOC)
        if not connected:
            return None
        return connected[0]

    @linkedBindLocatorModoItem.setter
    def linkedBindLocatorModoItem(self, bindloc):
        """ Gets/sets bind locator that will be linked with this plug.
        
        The idea is that when shadow bind skeleton is built the bind locator
        linked with this plug will be parented to a bind locator that is linked
        to a socket to which this plug is connected to.
        
        Parameters
        ----------
        bindLoc : modo.Item, None
            Pass None to clear linked root bind locator modo item.

        Returns
        -------
        BindLocator, None
        """
        modox.ItemUtils.clearReverseGraphConnections(self.modoItem, self._GRAPH_LINKED_BIND_LOC)
        if bindloc is None:
            return
        modox.ItemUtils.addForwardGraphConnections(bindloc, self.modoItem, self._GRAPH_LINKED_BIND_LOC)

    def cacheParentTransformOffset(self):
        """
        """
        modoItem = self.modoItem
        try:
            xfrmLink = TransformLink(modoItem)
        except TypeError:
            parentPosOffset = modo.Vector3()
            parentRotOffset = modo.Vector3()
        else:
            dynaParentModifier = modox.DynamicParentModifier(xfrmLink.setup.dynamicParentSetup.dynamicParentModifier)
            parentPosOffset, parentRotOffset = dynaParentModifier.offset

        self.setChannelProperty(self._CHAN_PARENT_POS_OFFSET_X, parentPosOffset.x)
        self.setChannelProperty(self._CHAN_PARENT_POS_OFFSET_Y, parentPosOffset.y)
        self.setChannelProperty(self._CHAN_PARENT_POS_OFFSET_Z, parentPosOffset.z)

        self.setChannelProperty(self._CHAN_PARENT_ROT_OFFSET_X, parentRotOffset.x)
        self.setChannelProperty(self._CHAN_PARENT_ROT_OFFSET_Y, parentRotOffset.y)
        self.setChannelProperty(self._CHAN_PARENT_ROT_OFFSET_Z, parentRotOffset.z)

    # -------- Private methods

    def _linkWorldTransforms(self, socket):
        """ Links socket world transforms with extra channels provided for that on the plug.
        """
        socwpos = modox.LocatorUtils.getItemWorldPositionMatrixChannel(socket)
        socwrot = modox.LocatorUtils.getItemWorldRotationMatrixChannel(socket)
        socwscl = modox.LocatorUtils.getItemWorldScaleMatrixChannel(socket)
        plugwpos = self.modoItem.channel(self._CHAN_SOCKET_WORLD_POS)
        plugwrot = self.modoItem.channel(self._CHAN_SOCKET_WORLD_ROT)
        plugwscl = self.modoItem.channel(self._CHAN_SOCKET_WORLD_SCL)
        socwpos >> plugwpos
        socwrot >> plugwrot
        socwscl >> plugwscl

    def _unlinkWorldTransforms(self):
        """ Unlinks socket world transform channels.
        Call it when disconnecting plug from socket.
        """
        plugwpos = self.modoItem.channel(self._CHAN_SOCKET_WORLD_POS)
        plugwrot = self.modoItem.channel(self._CHAN_SOCKET_WORLD_ROT)
        plugwscl = self.modoItem.channel(self._CHAN_SOCKET_WORLD_SCL)
        modox.ChannelUtils.removeAllReverseConnections([plugwpos, plugwrot, plugwscl])

    def _drawConnection(self, state, linkTargetItem=None):
        """ Enables/disables drawing connection to a given item.
        
        Parameters
        ----------
        state : bool
        
        linkTargetItem : modo.Item, None
        """
        if state:
            # Change connected plug drawing to solid circle and enable item link drawing.
            run('!channel.value circle channel:{%s:isShape}' % self.modoItem.id)
            run('!channel.value true channel:{%s:isSolid}' % self.modoItem.id)
            run('!channel.value true channel:{%s:rsilEnable}' % self.modoItem.id)
        else:
            # Change plug drawing back to wire sphere
            run('!channel.value sphere channel:{%s:isShape}' % self.modoItem.id)
            run('!channel.value false channel:{%s:isSolid}' % self.modoItem.id)
            run('!channel.value false channel:{%s:rsilEnable}' % self.modoItem.id)

        try:
            itemLink = ItemLinkFeature(self)
        except TypeError:
            pass
        else:
            itemLink.linkedItem = linkTargetItem
            itemLink.enable = state

    def _setItemLink(self, targetModoItem):
        self._removeItemLink()
        modox.ItemUtils.addForwardGraphConnections(self.modoItem, targetModoItem, self.GRAPH_ITEM_LINK)
    
    def _removeItemLink(self):
        modox.ItemUtils.clearForwardGraphConnections(self.modoItem, self.GRAPH_ITEM_LINK)

