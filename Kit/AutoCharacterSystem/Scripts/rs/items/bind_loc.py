
import lx
import modo
import modox
from modox import ItemUtils
from modox import LocatorUtils
from modox import Effector
from modox import GeneralInfluence

from ..item import Item
from ..items.plug import PlugItem
from ..items.socket import SocketItem
from .. import const as c
from ..log import log
from ..util import run
from ..core import service


class BindLocatorItem(Item):

    PLUG_GRAPH_NAME = 'rs.bindLocPlug'
    SOCKET_GRAPH_NAME = 'rs.bindLocSocket'
    RELATED_CONTROLLERS_GRAPH_NAME = 'rs.bindLocCtrls'
    RELATED_REGION_GRAPH_NAME = 'rs.bindLocCmdRegion'
    _GRAPH_BAKED_PARENT = 'rs.bindLocBakedParent'

    _CHAN_EXPORT_NAME = 'rsblExportName'
    _CHAN_ORIENT_OFFSET_X = 'rsblOrientOffset.X'
    _CHAN_ORIENT_OFFSET_Y = 'rsblOrientOffset.Y'
    _CHAN_ORIENT_OFFSET_Z = 'rsblOrientOffset.Z'

    _SETTING_BIND_MAP_WEIGHTS = 'bindwght'

    descType = c.RigItemType.BIND_LOCATOR
    descUsername = 'Bind Locator'
    descModoItemType = 'locator'
    descDefaultName = 'BindLocator'
    descPackages = ['rs.pkg.generic', 'rs.pkg.bindLocator']
    descDropScriptSource = c.DropScript.ITEM_ON_ITEM_SOURCE
    descDropScriptDestination = c.DropScript.ITEM_ON_ITEM_DESTINATION
    descItemCommand = c.ItemCommand.GENERIC
    
    def onAdd(self, subtype):
        modoItem = self.modoItem
        ident = modoItem.id

        #ItemUtils.autoPlaceInChain(modoItem, modo.Vector3(0.0, 0.0, 0.2))

        if not modoItem.internalItem.PackageTest("glItemShape"):
            modoItem.PackageAdd("glItemShape")

        if not modoItem.internalItem.PackageTest("glLinkShape"):
            modoItem.PackageAdd("glLinkShape")

        # Set shape
        run('!channel.value custom channel:{%s:drawShape}' % ident)
        run('!channel.value circle channel:{%s:isShape}' % ident)
        run('!channel.value true channel:{%s:isAlign}' % ident)
        run('!channel.value 0.005 channel:{%s:isRadius}' % ident)

        # Set link shape
        run('!channel.value custom channel:{%s:link}' % ident)
        run('!channel.value box channel:{%s:lsShape}' % ident)
        run('!channel.value true channel:{%s:lsSolid}' % ident)
        run('!channel.value true channel:{%s:lsAuto}' % ident)
            
        # Set item color.
        run('!rs.item.color bindJoint autoAdd:true item:{%s}' % ident)
        run('select.item {%s} set' % ident)
        run('item.editorColor lightgreen')

    def onDroppedOnItem(self, modoItem, context):
        """
        Performs an action when bind locator is dropped onto another item.

        We want to check if bind locator has a related plug set.
        If it has we try to perform drop action on that plug to make bind locator
        behave as a plug when dropped on a socket in assembly context.
        """
        relatedPlug = self.relatedPlug
        if relatedPlug is None:
            return

        relatedPlug = Item.getFromModoItem(relatedPlug)
        try:
            relatedPlug.onDroppedOnItem(modoItem, context)
        except AttributeError:
            pass

    def onItemDropped(self, modoItem, context):
        """ Called when another item is dropped onto this one.
        
        There are multiple actions depending on the context we're in.
        """
        if context == c.Context.MESHES:
            self._attachDroppedMeshDropAction(modoItem, context.subcontext)
        
        elif context == c.Context.ASSEMBLY:
            # Dropping bind locator on bind locator from another module
            # will try to connect plug related to dropped bind locator
            # to the socket related to the bind locator the first one was dropped onto.
            self._connectToSocketDropAction(modoItem)

    def onStandardise(self):
        """ Clear all graph links by clearing settings that use graphs.
        """
        self.relatedPlug = None
        self.relatedSocket = None
        self.relatedControllers = None

    @property
    def exportName(self):
        """
        Gets bind locator export name - name applied during baking for export.

        Returns
        -------
        str
        """
        return self.getChannelProperty(self._CHAN_EXPORT_NAME)

    @exportName.setter
    def exportName(self, name):
        """
        Sets new export name. The name will be applied during baking for export.

        Parameters
        ----------
        name : str
        """
        self.setChannelProperty(self._CHAN_EXPORT_NAME, name)

    @property
    def bakeSettingsChannels(self):
        """
        Gets channel in which export name is stored.

        Returns
        -------
        [modo.Channel]
        """
        chans = [self.modoItem.channel(self._CHAN_EXPORT_NAME),
                 self.modoItem.channel(self._CHAN_ORIENT_OFFSET_X),
                 self.modoItem.channel(self._CHAN_ORIENT_OFFSET_Y),
                 self.modoItem.channel(self._CHAN_ORIENT_OFFSET_Z)]
        return chans

    @property
    def bakedParent(self):
        """
        Gets parent item for baked version of the bind locator.

        When bind skeleton is baked it gets parented to this item.

        Returns
        -------
        modo.Item, None
        """
        return self._getLinkedConnector(self._GRAPH_BAKED_PARENT)

    @bakedParent.setter
    def bakedParent(self, parentItem=None):
        """
        Sets baked parent item.

        When bind skeleton is baked it gets parented to this item.

        Parameters
        ----------
        parentItem : modo.Item, None
            Pass None to clear any connections.
        """
        self._setLinkedConnector(parentItem, self._GRAPH_BAKED_PARENT)

    @property
    def orientationOffset(self):
        """
        Gets orientation offset as a list.

        Returns
        -------
        [float, float, float]
        """
        x = self.getChannelProperty(self._CHAN_ORIENT_OFFSET_X)
        y = self.getChannelProperty(self._CHAN_ORIENT_OFFSET_Y)
        z = self.getChannelProperty(self._CHAN_ORIENT_OFFSET_Z)
        return modo.Vector3(x, y, z)

    @property
    def relatedPlug(self):
        """ Gets hierarchy connector for this bind locator.
        
        Returns
        -------
        modo.Item, None
        """
        return self._getLinkedConnector(self.PLUG_GRAPH_NAME)
    
    @relatedPlug.setter
    def relatedPlug(self, plugModoItem):
        """ Sets hierarchy connector.
        
        Parameters
        ----------
        plugModoItem : modo.Item, None
            Pass None to clear any connections.
        """
        self._setLinkedConnector(plugModoItem, self.PLUG_GRAPH_NAME)

    @property
    def relatedSocket(self):
        """ Gets hierarchy connector for this bind locator.
        
        Returns
        -------
        modo.Item, None
        """
        return self._getLinkedConnector(self.SOCKET_GRAPH_NAME)
    
    @relatedSocket.setter
    def relatedSocket(self, socketModoItem):
        """ Sets hierarchy connector.
        
        Parameters
        ----------
        socketModoItem : modo.Item, None
            Pass None to clear any connections.
        """
        self._setLinkedConnector(socketModoItem, self.SOCKET_GRAPH_NAME)

    def applyOrientationOffset(self):
        """
        Applies orientation offset from bind locator's properties to the constraint
        that is driving locator's world rotation.

        If rotation constraint is not an input to bind locator's world rotation
        the offset is ignored.

        Returns
        -------
        modo.Item
        """
        worldRotChannel = modox.LocatorUtils.getItemWorldRotationMatrixChannel(self.modoItem)
        drivingItem = modox.ChannelUtils.getChannelInputItem(worldRotChannel)

        if drivingItem is None:
            return

        try:
            constraintItem = modox.CMTransformConstraint(drivingItem)
        except TypeError:
            return

        if not constraintItem.isRotationConstraint:
            return

        offsetVec = self.orientationOffset
        constraintItem.offset = offsetVec

    def getParentBindLocator(self):
        """ Gets a parent for this bind locator.
        
        This is not simply returning bind locator modo item parent.
        This returns a parent as if bind skeleton was continuous hierarchy.
        This means that it can return bind locator from another module if
        proper connection was set up in bind locator properties.
        
        Returns
        -------
        BindLocator or None, bool
            Parent bind locator or none if no parent bind locator was found.
            2nd returned value tells whether parent bind locator is direct parent
            or external one, obtained via reaching out to plug->socket connection.
            False is returned for direct parent, True for external one.
        """
        # Get regular parent first.
        # We look for connectors only when locator does not have a bind locator parent.
        parent = self.modoItem.parent
        
        if parent:
            try:
                return BindLocatorItem(parent), False
            except TypeError:
                pass

        # No regular parent, check if this bind locator is linked with a plug.
        connected = modox.ItemUtils.getForwardGraphConnections(self.modoItem, "rs.plugBindLoc")
        if not connected:
            return None, False
        
        # Connector has to be plug.
        try:
            plug = PlugItem(connected[0])
        except TypeError:
            return None, False
        
        # Get socket from a plug.
        socket = plug.socket
        if socket is None:
            return None, False

        # Follow link from socket to bind locator.
        bindlocModoItem = socket.linkedBindLocatorModoItem
        if bindlocModoItem is None:
            return None, False

        try:
            return BindLocatorItem(bindlocModoItem), True
        except TypeError:
            return None, False

    @property
    def nonHiddenParentBindLocator(self):
        """
        Gets first parent bind locator that is not a hidden bind locator.

        All hidden parents are skipped and not considered parents.

        Returns
        -------
        BindLocatorItem or None, bool
            Bind locator item is returned or None if there is no parent.
            Bool is True when returned parent comes from another module
            and is not direct parent in hierarchy.
        """
        parent, external = self.getParentBindLocator()

        while parent is not None and parent.hidden:
            parent, nextExternal = parent.getParentBindLocator()
            # once we reach first external parent every another parent
            # is considered external
            external = external or nextExternal

        return parent, external

    @property
    def relatedControllers(self):
        return ItemUtils.getForwardGraphConnections(self.modoItem, self.RELATED_CONTROLLERS_GRAPH_NAME)

    @relatedControllers.setter
    def relatedControllers(self, items):
        """ Sets controllers that are related to bind locator.
        
        New list completely replaces any connections that were already there!
        
        Related controllers are ones that can be selected or edited in some other
        way by either selecting bind locator or some other item attached
        to the bind locator. For example selecting bind mesh proxy can redirect
        selection to a controller via bind locator the proxy is attached to.
        
        Parameters
        ----------
        items : list of modo.Item, None
            Pass None to clear any connections.
        
        Returns
        -------
        modo.Item
        """

        ItemUtils.clearForwardGraphConnections(self.modoItem, self.RELATED_CONTROLLERS_GRAPH_NAME)
        
        if items is None:
            return

        if type(items) not in (list, tuple):
            items = [items]
        ItemUtils.addForwardGraphConnections(self.modoItem, items, self.RELATED_CONTROLLERS_GRAPH_NAME)

    @property
    def relatedCommandRegion(self):
        """
        Gets a command region that is related to this bind locator.

        Returns
        -------
        modo.Item, None
        """
        return ItemUtils.getFirstForwardGraphConnection(self.modoItem, self.RELATED_REGION_GRAPH_NAME)

    @relatedCommandRegion.setter
    def relatedCommandRegion(self, item):
        """ Sets a command region that is related to bind locator.

        Region has to be within the same module the bind locator is.

        Parameters
        ----------
        item : modo.Item, None
            Pass None to clear a connection.
        """
        ItemUtils.clearForwardGraphConnections(self.modoItem, self.RELATED_REGION_GRAPH_NAME)

        if item is None:
            return

        ItemUtils.addForwardGraphConnections(self.modoItem, item, self.RELATED_REGION_GRAPH_NAME)

    @property
    def regionColorRGB(self):
        """ Gets command region color for this bind locator as RGB vector.
        
        Returns
        -------
        tuple of 3 floats
        """
        return self.getChannelProperty('rsblRegionColor')
        
    @property
    def isLeaf(self):
        """ Tests whether this bind locator is a leaf.
        
        Leaf is a locator that does not have any children and
        is parented to another bind locator directly.
        It also cannot have related socket set in its properties.
        """
        parent = self.modoItem.parent
        if parent is None:
            return False
        try:
            BindLocatorItem(parent)
        except TypeError:
            return False

        if self.relatedSocket is not None:
            return False
        
        return self.modoItem.childCount() == 0

    @property
    def centerPoint(self):
        """ Gets bind locator's center point.
        
        If bind locator has a child the center is a midpoint between
        this bind locator and its first child.
        If bind locator has no children it's center point is the position
        of the bind locator itself.
        Returned position is in world space.
        
        Returns
        -------
        modo.Vector3
        """
        bindLocWPos = modo.Vector3(LocatorUtils.getItemWorldPosition(self.modoItem))
        
        if self.modoItem.childCount() == 0:
            return bindLocWPos
        else:
            child = self.modoItem.childAtIndex(0)
            childWPos = LocatorUtils.getItemWorldPosition(child)
            return bindLocWPos.lerp(modo.Vector3(childWPos), 0.5)

    @property
    def weightMapName(self):
        """ Gets first weight map name from the first deformer this bind locator drivers.

        This can be either weight container or a weight map set directly in deformer properties.
        
        Returns
        -------
        str, None
        """
        eff = Effector(self.modoItem)
        deformers = eff.deformers
        if not deformers:
            return None
        wmapNames = modox.Deformer(deformers[0]).weightMapNames
        if len(wmapNames) == 0:
            return None
        return wmapNames[0]

    @property
    def normalizedGeneralInfluence(self):
        """ Gets first general influence the effector is plugged to.
        
        Returns
        -------
        modox.GeneralInfluence
        """
        eff = Effector(self.modoItem)
        geninfs = eff.generalInfluences
        if not geninfs:
            return None
        return GeneralInfluence(geninfs[0])

    @property
    def isEffector(self):
        """ Tests whether this bind locator is an effector.
        
        Being effector means driving one or more deformers.
        """
        return modox.Effector(self.modoItem).isEffector
        
    # -------- Private Methods

    def _attachDroppedMeshDropAction(self, modoItem, subcontext):
        """ Performs an action when a mesh was dropped onto bind locator.
        
        The action will be different depending on which meshes subcontext we're in.
        """
        if modoItem.type not in ['mesh', 'meshInst']:
            return

        if subcontext == c.MeshesSubcontexts.RIGID_MESHES:
            try:
                lx.eval('rs.attach.add type:{%s} mesh:{%s} item:{%s}' % (c.ComponentType.RIGID_MESHES, modoItem.id, self.modoItem.id))
            except RuntimeError:
                pass
        elif subcontext == c.MeshesSubcontexts.BIND_PROXIES:
            try:
                lx.eval('rs.attach.add type:{%s} mesh:{%s} item:{%s}' % (c.ComponentType.BIND_PROXIES, modoItem.id, self.modoItem.id))
            except RuntimeError:
                pass
        elif subcontext == c.MeshesSubcontexts.BIND_MESHES:
            try:
                lx.eval('rs.bind.mesh action:assign mesh:{%s}' % (modoItem.id))
            except RuntimeError:
                pass

    def _connectToSocketDropAction(self, modoItem):
        """ Performs an action when item was dropped onto this bind locator in assembly context.
        
        This is complementary to drop action handled by plug itself.
        Here we handle following scenarios:
        - plug dropped onto bind locator that has related socket
        - bind locator with related plug dropped onto bind locator that has related socket.
        - ignore either plug or bind locator if it comes from the same module as target item.
        """
        try:
            sourceItem = self.getFromModoItem(modoItem)
        except TypeError:
            return

        # If this bind locator doesn't have a related socket
        # we can't do anything.
        if not self.relatedSocket:
            return

        # Ignore item that comes from the same module.
        if sourceItem.moduleRootItem == self.moduleRootItem:
            return

        # Acceptable item is either plug or bind locator.
        if sourceItem.type == c.RigItemType.PLUG:
            plug = sourceItem
        elif sourceItem.type == c.RigItemType.BIND_LOCATOR:
            plug = sourceItem.relatedPlug # This returns modo.Item
            if plug is not None:
                plug = PlugItem(plug)

        if plug is None:
            return

        try:
            socketItem = SocketItem(self.relatedSocket)
        except TypeError:
            return

        # Connect plug to socket.
        plug.connectToSocket(socketItem)

    def _getLinkedConnector(self, graphName):
        graph = self.modoItem.itemGraph(graphName)
        try:
            return graph.forward(0)
        except LookupError:
            return None
        
    def _setLinkedConnector(self, modoItem, graphName):
        ItemUtils.clearForwardGraphConnections(self.modoItem, graphName)
        
        if modoItem is None:
            return

        bindlocGraph = self.modoItem.itemGraph(graphName)
        connectorGraph = modoItem.itemGraph(graphName)
        bindlocGraph >> connectorGraph