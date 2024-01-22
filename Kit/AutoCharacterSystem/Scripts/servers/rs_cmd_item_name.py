

import lx
import lxu
import modo

import rs


class CmdItemName(rs.base_OnItemCommand):
    """ Queries or sets rig item name.
    """

    ARG_NAME = 'name'

    def arguments(self):
        superArgs = rs.base_OnItemCommand.arguments(self)
        
        nameArg = rs.cmd.Argument(self.ARG_NAME, 'string')
        nameArg.flags = 'query'
        nameArg.defaultValue = ''

        return [nameArg] + superArgs

    def execute(self, msg, flags):
        itemName = self.getArgumentValue(self.ARG_NAME)
        if not itemName:
            return
        
        for rigItem in self.itemsToEdit:
            rigItem.name = itemName
            rigItem.renderAndSetName()

    def query(self, argument):
        if argument == self.ARG_NAME:
            item = self.itemToQuery
            if item is not None:
                return item.name

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers

rs.cmd.bless(CmdItemName, 'rs.item.name')