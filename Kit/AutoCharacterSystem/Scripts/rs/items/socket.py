
import lx
import modox

from ..item import Item
from ..util import run
from .. import const as c


class SocketItem(Item):

    _GRAPH_LINKED_BIND_LOC = "rs.socketBindLoc"
    
    descType = 'socket'
    descUsername = 'Socket'
    descModoItemType = 'locator'
    descDefaultName = 'Socket'
    descPackages = ['rs.pkg.socket', 'rs.pkg.generic']
    descItemCommand = c.ItemCommand.GENERIC
    descDropScriptSource = c.DropScript.ITEM_ON_ITEM_SOURCE
    descDropScriptDestination = c.DropScript.ITEM_ON_ITEM_DESTINATION

    def onAdd(self, subtype):
        modoItem = self.modoItem

        if not modoItem.internalItem.PackageTest("glItemShape"):
            modoItem.PackageAdd("glItemShape")

        run('!channel.value custom channel:{%s:drawShape}' % modoItem.id)
        run('!channel.value circle channel:{%s:isShape}' % modoItem.id)
        run('!channel.value true channel:{%s:isAlign}' % modoItem.id)
        run('!channel.value 0.0 channel:{%s:isRadius}' % modoItem.id) # We don't really want to see any shape
        run('!channel.value false channel:{%s:isSolid}' % modoItem.id)

        run('select.item {%s} set' % modoItem.id)
        run('item.editorColor blue')

        run('!rs.item.color socket autoAdd:true item:{%s}' % self.modoItem.id)

    @property
    def linkedBindLocatorModoItem(self):
        connected = modox.ItemUtils.getReverseGraphConnections(self.modoItem, self._GRAPH_LINKED_BIND_LOC)
        if not connected:
            return None
        return connected[0]

    @linkedBindLocatorModoItem.setter
    def linkedBindLocatorModoItem(self, bindloc):
        """ Gets/sets bind locator that will be linked with this socket.
        
        The idea is that when shadow bind skeleton is built the bind locator
        linked with this socket will be a parent to a bind locator that is linked
        with a plug which is connected to this socket.
        
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
