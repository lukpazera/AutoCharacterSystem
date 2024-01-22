

import lx
import lxu
import modo
import modox

import rs


def testItem(rawItem):
    """
    """
    try:
        bloc = rs.BindLocatorItem(rawItem)
    except TypeError:
        return False
    return True


class ItemsListContent(rs.cmd.ArgumentItemsContent):
    def __init__(self):
        self.noneOption = True
        self.testOnRawItems = True
        self.itemTestFunction = testItem


class RSCmdSocketBindLocator(rs.base_OnItemCommand):

    descItemClassOrIdentifier = rs.SocketItem
    
    ARG_BIND_LOC_ITEM = 'blocItem'
    
    def arguments(self):
        superArgs = rs.base_OnItemCommand.arguments(self)
                
        blocItemArg = rs.cmd.Argument(self.ARG_BIND_LOC_ITEM, '&item')
        blocItemArg.flags = 'query'
        blocItemArg.valuesListUIType = rs.cmd.ArgumentValuesListType.ITEM_POPUP
        blocItemArg.valuesList = ItemsListContent()
        
        return [blocItemArg] + superArgs

    def execute(self, msg, flags): 
        # itemid will be empty string if none option was chosen.
        itemid = self.getArgumentValue(self.ARG_BIND_LOC_ITEM)
        blocModoItem = None
            
        if itemid:
            try:
                blocModoItem = modo.Item(modox.SceneUtils.findItemFast(itemid))
            except LookupError:
                pass
                
        for socket in self.itemsToEdit:
            socket.linkedBindLocatorModoItem = blocModoItem

    def query(self, argument):
        if argument == self.ARG_BIND_LOC_ITEM:
            socket = self.itemToQuery
            if socket is None:
                return
            
            return socket.linkedBindLocatorModoItem
            
rs.cmd.bless(RSCmdSocketBindLocator, 'rs.socket.bindLocator')