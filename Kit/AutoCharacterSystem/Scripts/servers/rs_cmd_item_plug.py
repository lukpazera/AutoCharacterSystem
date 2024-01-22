
import lx
import lxu
import modo
import modox

import rs


class CmdConnectPlug(rs.RigCommand):
    """ Connects one or more plugs to given socket.
    """

    ARG_PLUG = 'plug'
    ARG_SOCKET = 'socket'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        plugArg = rs.cmd.Argument(self.ARG_PLUG, '&item')
        plugArg.flags = ['optional', 'hidden']

        socketArg = rs.cmd.Argument(self.ARG_SOCKET, '&item')
        socketArg.flags = ['optional', 'hidden']

        return [plugArg, socketArg] + superArgs

    def setupMode(self):
        return True

    def enable(self, msg):
        return self._testItems()

    def execute(self, msg, flags):
        plugs, socket = self._getItems()
        if not plugs or socket is None:
            return

        for plug in plugs:
            plug.connectToSocket(socket, drawConnection=True)

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _testItems(self):
        """
        Tests whether two viable items are selected.
        1. a plug and socket.
        2. bind locator with related plug/socket that is not None.
        """
        if self.isArgumentSet(self.ARG_PLUG) and self.isArgumentSet(self.ARG_SOCKET):
            return True

        isplug = False
        issocket = False

        selected = modox.ItemSelection().getRaw()
        for item in selected:
            modoItem = modo.Item(item)
            if not rs.Item.isRigItem(modoItem):
                continue

            if rs.PlugItem.isRigItem(modoItem):
                isplug = True
            elif rs.SocketItem.isRigItem(modoItem):
                issocket = True
            elif rs.BindLocatorItem.isRigItem(modoItem):
                bindLoc = rs.BindLocatorItem(modoItem)
                if bindLoc.relatedSocket is not None:
                    issocket = True

            if isplug and issocket:
                return True
        return False

    def _getItems(self):
        """
        Gets items for command to work on.

        Returns
        -------
        PlugItem, SocketItem
        """
        if self.isArgumentSet(self.ARG_PLUG) and self.isArgumentSet(self.ARG_SOCKET):
            plugID = self.getArgumentValue(self.ARG_PLUG)
            socketID = self.getArgumentValue(self.ARG_SOCKET)
            rawPlug = modox.SceneUtils.findItemFast(plugID)
            rawSocket = modox.SceneUtils.findItemFast(socketID)
            return [rs.PlugItem(rawPlug)], rs.SocketItem(rawSocket)

        plugs = []
        socket = None
        selected = modox.ItemSelection().getRaw()
        for item in selected:
            try:
                rigItem = rs.Item.getFromOther(item)
            except TypeError:
                continue

            if rigItem.type == rs.c.RigItemType.PLUG:
                plugs.append(rigItem)
            elif rigItem.type == rs.c.RigItemType.SOCKET:
                socket = rigItem
            elif rigItem.type == rs.c.RigItemType.BIND_LOCATOR:
                if rigItem.relatedSocket is not None:
                    socket = rigItem.relatedSocket

        return plugs, socket

rs.cmd.bless(CmdConnectPlug, 'rs.item.connectPlug')


class CmdDisconnectPlug(rs.base_OnItemCommand):
    """ Disconnects plug from its socket.
    """

    descItemClassOrIdentifier = rs.PlugItem

    def enable(self, msg):
        if not rs.Scene.anyRigsInSceneFast():
            return False

        return self.itemToQuery is not None

    def setupMode(self):
        return True

    def execute(self, msg, flags):
        for rigItem in self.itemsToEdit:
            rigItem.disconnectFromSocket()

    def notifiers(self):
        notifiers = rs.base_OnItemCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

rs.cmd.bless(CmdDisconnectPlug, 'rs.item.disconnectPlug')