

import lx
import lxu
import modo
import modox

import rs


class CmdItemDropItemSource(rs.Command):
    """ Command is fired when one item is dropped onto another.
    
    This is how item on item drop mechanism works in MODO:
    1. When there is source drop script on an item and you drop this item onto another -
       source drop script from source item is executed.
    2. When there is destination drop script on item and you drop another item on this item -
       destination drop script will be executed ONLY if there was no source script
       on the item that was dropped.

    In rigging system we try to perform destination script action on each target item.
    So if source item is dropped on an item with destination action we will execute source
    script action first and then destination action on target item too.
    """

    SOURCE_ITEM = 'srcItem'
    DESTINATION_ITEM = 'dstItem'
    MODE = 'mode'

    MODE_HINTS = ((0, 'src'),
                  (1, 'dst'))

    def arguments(self):
        sourceItem = rs.cmd.Argument(self.SOURCE_ITEM, '&item')
        sourceItem.defaultValue = None
        
        destItem = rs.cmd.Argument(self.DESTINATION_ITEM, '&item')
        destItem.defaultValue = None

        mode = rs.cmd.Argument(self.MODE, 'integer')
        mode.hints = self.MODE_HINTS
        mode.flags = 'optional'
        mode.defaultValue = 0 # src mode by default

        return [sourceItem, destItem, mode]

    def enable(self, msg):
        return True

    def applyEditActionPre(self):
        return True

    def applyEditActionPost(self):
        return True

    def execute(self, msg, flags):
        # We do not perform drop action if one of standard
        # drop actions are set up in MODO UI.
        dropAction = lx.eval('item.dropAction type:global action:?')
        if dropAction != 'none':  # return value comes out as a string
            return

        srcItemIdent = self.getArgumentValue(self.SOURCE_ITEM)
        dstItemIdent = self.getArgumentValue(self.DESTINATION_ITEM)
        
        if srcItemIdent is None or dstItemIdent is None:
            return

        scene = modo.Scene()
        
        try:
            srcItem = scene.item(srcItemIdent)
        except LookupError:
            return
        
        try:
            dstItem = scene.item(dstItemIdent)
        except LookupError:
            return

        mode = self.getArgumentValue(self.MODE)

        context = rs.Scene.getCurrentContextFast()

        if mode == 0:
            # With source drop script we execute both onDroppedOnItem on the source item
            # as well as OnItemDropped on destination item.
            # This is because MODO will not execute destination script on an item
            # if an item with source drop script was dropped on it.
            sourceDropAction = True
            destinationDropAction = True
        elif mode == 1:
            sourceDropAction = False
            destinationDropAction = True
        else:
            sourceDropAction = False
            destinationDropAction = False

        # Source drop script
        if sourceDropAction:
            try:
                srcRigItem = rs.Item.getFromModoItem(srcItem)
            except TypeError:
                srcRigItem = None

            if srcRigItem is not None:
                try:
                    srcRigItem.onDroppedOnItem(dstItem, context)
                except AttributeError:
                    pass

        # Destination drop script
        if destinationDropAction:
            try:
                dstRigItem = rs.Item.getFromModoItem(dstItem)
            except TypeError:
                dstRigItem = None

            if dstRigItem is not None:
                try:
                    dstRigItem.onItemDropped(srcItem, context)
                except AttributeError:
                    pass

    def notifiers(self):
        return []

rs.cmd.bless(CmdItemDropItemSource, 'rs.item.dropOnItem')