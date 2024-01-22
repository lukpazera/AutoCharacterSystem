

import lx
import lxu
import modo
import modox


import rs


class CmdNewItem (rs.Command):
    """ Adds new rig item to the scene.
    """

    ARG_TYPE = 'type'
    ARG_SUBTYPE = 'subtype'
    ARG_NAME = 'name'
    ARG_SCHEMA = 'schema'

    def arguments(self):
        typeArg = rs.cmd.Argument(self.ARG_TYPE, 'string')
        
        subtypeArg = rs.cmd.Argument(self.ARG_SUBTYPE, 'string')
        subtypeArg.flags = 'optional'
        subtypeArg.defaultValue = None
    
        nameArg = rs.cmd.Argument(self.ARG_NAME, 'string')
        nameArg.flags = 'optional'
        nameArg.defaultValue = ''

        schemaArg = rs.cmd.Argument(self.ARG_SCHEMA, 'boolean')
        schemaArg.flags = 'optional'
        schemaArg.defaultValue = False

        return [typeArg, subtypeArg, nameArg, schemaArg]

    def setupMode(self):
        return True

    def basic_ButtonName(self):
        itemType = self.getArgumentValue(self.ARG_TYPE)
        itemClass = rs.service.systemComponent.get(rs.c.SystemComponentType.ITEM, itemType)
        itemTypeUsername = itemClass.descUsername

        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, 'itemNew', [itemTypeUsername])

    def execute(self, msg, flags):
        itemType = self.getArgumentValue(self.ARG_TYPE)
        if not itemType:
            return
        
        subtype = self.getArgumentValue(self.ARG_SUBTYPE)
        name = self.getArgumentValue(self.ARG_NAME)
        if not name:
            name = None
        schema = self.getArgumentValue(self.ARG_SCHEMA)

        rsScene = rs.Scene()
        editRig = rsScene.editRig
        if editRig is None:
            return

        if schema:
            newItem = self._addToSchematic(itemType, subtype)
        else:
            # Add item to edit rig, to current module
            try:
                newItem = editRig.newItem(itemType, subtype, name)
            except TypeError:
                return
        rsScene.contexts.refreshCurrent()
        modox.Item(newItem.modoItem.internalItem).autoFocusInItemList()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+t'))
        return notifiers

    # -------- Private methods

    def _addToSchematic(self, itemType, subtype=None):
        """ Adds item to current assembly in schematic.
        """
        itemClass = rs.service.systemComponent.get(rs.c.SystemComponentType.ITEM, itemType)
        modoItemType = itemClass.descModoItemType
        if modoItemType is None:
            modoItemType = 'locator'
        newModoItem = modo.Scene().addItem(modoItemType, itemClass.descDefaultName)
        rs.run('schematic.addItem item:{%s} mods:false' % newModoItem.id)

        try:
            parentGroup = newModoItem.connectedGroups[0]
        except IndexError:
            pass
        else:
            parentGroup.removeItems(newModoItem)

        newItem = itemClass.newFromExistingItem(newModoItem,
                                                subtype,
                                                name=itemClass.descDefaultName,
                                                componentSetup=parentGroup)
        return newItem

rs.cmd.bless(CmdNewItem, "rs.item.new")