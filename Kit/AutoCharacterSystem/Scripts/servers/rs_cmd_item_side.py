

import copy

import lx
import lxu
import modo
import modox

import rs


class CmdItemSide(rs.base_OnItemCommand):
    """ Query or set item side.
    
    This command presents a popup with side choices.
    Therefore the argument is an integer (in range from 0 to n)
    and then it has popup as a hint that is using internal and user strings.
    """

    ARG_SIDE = 'side'

    POPUP_INDEX_TO_SIDE = {1: rs.c.Side.CENTER,
                           2: rs.c.Side.LEFT,
                           3: rs.c.Side.RIGHT}
    SIDE_TO_POPUP_INDEX = {rs.c.Side.CENTER: 1,
                           rs.c.Side.LEFT: 2,
                           rs.c.Side.RIGHT: 3}
    SIDE_TO_STRING = {rs.c.Side.CENTER: 'Center',
                      rs.c.Side.LEFT: 'Left',
                      rs.c.Side.RIGHT: 'Right'}
    POPUP_ITEMS = [['inherit', '(Inherited From Module)'],
                   ['center', 'Center'],
                   ['left', 'Left'],
                   ['right', 'Right']]

    def arguments(self):
        superArgs = rs.base_OnItemCommand.arguments(self)
        
        arg = rs.cmd.Argument(self.ARG_SIDE, 'integer')
        arg.flags = 'query'
        arg.valuesList = self._buildPopup
        arg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        return [arg] + superArgs
        
    def execute(self, msg, flags):
        itemSide = self.getArgumentValue(self.ARG_SIDE)

        if itemSide == 0:
            # Switch to inherit from module
            for rawItem in modox.ItemSelection().getRaw():
                try:
                    rigItem = rs.Item.getFromOther(rawItem)
                    rigItem.sideSameAsModule = True
                except TypeError:
                    continue
            return

        try:
            itemSide = self.POPUP_INDEX_TO_SIDE[itemSide]
        except KeyError:
            return

        for rawItem in modox.ItemSelection().getRaw():
            try:
                rigItem = rs.Item.getFromOther(rawItem)
                rigItem.sideSameAsModule = False
            except TypeError:
                continue
            
            previousSide = rigItem.side
            if previousSide == itemSide:
                return
            rigItem.itemSide = itemSide

    def query(self, argument):
        if argument == self.ARG_SIDE:
            rigItem = self.itemToQuery
            if rigItem is None:
                return None
            try:
                if rigItem.sideSameAsModule:
                    return 0
            except TypeError:
                pass
            
            name = rigItem.side
            if name:
                return self.SIDE_TO_POPUP_INDEX[name]
        return None

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers

    # -------- Private methods

    def _buildPopup(self):
        """ Builds popup to present in UI.
        
        Popup is fixed except for the username for the inherited side setting.
        This gets updated with current module's side.
        """
        popup = copy.deepcopy(self.POPUP_ITEMS)
        rigItem = self.itemToQuery
        if rigItem is not None:
            modRoot = rigItem.moduleRootItem
            if modRoot is not None:
                mod = rs.Module(modRoot)
                popup[0][1] = self.SIDE_TO_STRING[mod.side] + ' ' + popup[0][1]
        return popup
        
rs.cmd.bless(CmdItemSide, 'rs.item.side')