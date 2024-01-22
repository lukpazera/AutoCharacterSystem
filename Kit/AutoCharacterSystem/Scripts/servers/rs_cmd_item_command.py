

import modo
import modox
import rs


class CmdItemCommand(rs.Command):
    """ General item command.
    """

    def enable(self, msg):
        return True

    def execute(self, msg, flags):
        itemSel = modox.ItemSelection()
        itemToTest = itemSel.getLastModo()
        if itemToTest is None:
            return
            
        try:
            rigItem = rs.ItemUtils.getItemFromModoItem(itemToTest)
        except TypeError:
            return
        
        # Try to call onSelected() on the item.
        try:
            rigItem.onSelected()
        except AttributeError:
            pass

        # Try to call onSelected() on all item features.
        featureop = rs.ItemFeatures(rigItem.modoItem)
        for feature in featureop.allFeatures:
            try:
                feature.onSelected()
            except AttributeError:
                pass
        
        rs.service.events.send(rs.c.EventTypes.RIG_ITEM_SELECTED, item=rigItem)

rs.cmd.bless(CmdItemCommand, 'rs.item.command')