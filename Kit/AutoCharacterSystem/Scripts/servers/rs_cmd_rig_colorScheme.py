

import lx
import lxu
import modo

import rs


class CmdRigColorScheme(rs.RigCommand):
    """ Sets and queries color scheme for a rig.
    """

    ARG_LIST = 'list'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        listArg = rs.cmd.Argument(self.ARG_LIST, 'integer')
        listArg.flags = 'query'
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        return [listArg] + superArgs

    def query(self, argument):
        if argument == self.ARG_LIST:
            rigToQuery = self.rigToQuery
            if rigToQuery is None:
                return 0

            editRigColorScheme = rigToQuery.colorScheme
            if editRigColorScheme is None:
                return 0
            
            index = -1
            for n, colorScheme in enumerate(self._colorSchemes):
                if colorScheme == editRigColorScheme:
                    index = n
                    break

            if index < 0:
                rs.log.out("Bad color scheme reference.", messageType=rs.log.MSG_ERROR)
                return 0

            return index

    def execute(self, msg, flags):
        nameSchemeIndex = self.getArgumentValue(self.ARG_LIST)

        try:
            colorSchemeToSet = self._colorSchemes[nameSchemeIndex]
        except IndexError:
            rs.log.out("Bad color scheme index when setting color scheme", messageType=rs.log.MSG_ERROR)
            return

        rigs = self.rigsToEdit
        for rig in rigs:        
            rig.colorScheme = colorSchemeToSet
    
    def restoreItemSelection(self):
        return True

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)

        # For the popup to refresh command needs to react to
        # datatype change when new rig root item is added or removed
        notifiers.append(('item.event', 'add[%s] +t' % rs.c.RigItemType.ROOT_ITEM))
        notifiers.append(('item.event', 'remove[%s] +t' % rs.c.RigItemType.ROOT_ITEM))
        
        # React to changes to current Rig graph as well
        # this changes current selection.
        notifiers.append(('graphs.event', '%s +t' % rs.c.RigGraph.EDIT_RIG))

        return notifiers

    # -------- Private methods
    
    def _buildPopup(self):
        content = rs.cmd.ArgumentPopupContent()
        content.iconWidth = rs.base_ColorScheme.Icon.SCHEME_WIDTH
        content.iconHeight = rs.base_ColorScheme.Icon.SCHEME_HEIGHT
        
        for scheme in self._colorSchemes:
            entry = rs.cmd.ArgumentPopupEntry(scheme.descIdentifier, scheme.descUsername)
            entry.iconImage = scheme.iconImage
            content.addEntry(entry)
        return content

    @property
    def _colorSchemes(self):
        return rs.service.systemComponent.getOfType(rs.c.SystemComponentType.COLOR_SCHEME)

rs.cmd.bless(CmdRigColorScheme, 'rs.rig.colorScheme')