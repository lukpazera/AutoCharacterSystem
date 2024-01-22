

import lx
import lxu
import modo

import rs


class CmdBindLocatorConnectorPopup(rs.Command):
    """ Sets or queries the connector for bind locator item.

    This command is suitable for using from UI, not from scripts.
    """

    ARG_INDEX = 'popupIndex'
    ARG_TYPE = 'type'

    TYPE_HINTS = ((0, 'plug'),
                  (1, 'socket'),
                  (2, 'bparent'))

    def arguments(self):
        argIndex = rs.cmd.Argument(self.ARG_INDEX, 'integer')
        argIndex.flags = 'query'
        argIndex.valuesList = self._buildPopup
        argIndex.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        argType = rs.cmd.Argument(self.ARG_TYPE, 'string')
        argType.hints = self.TYPE_HINTS

        return [argIndex, argType]

    def execute(self, msg, flags):
        index = self.getArgumentValue(self.ARG_INDEX)
        connectorType = self.getArgumentValue(self.ARG_TYPE)
        bindloc = self._bindLocatorToQuery
        
        if index == 0:
            connector = None
        else:
            connectors = self._availableConnectorsList(bindloc)
            connector = connectors[index - 1]

        if connectorType == 'plug':
            bindloc.relatedPlug = connector
        elif connectorType == 'socket':
            bindloc.relatedSocket = connector
        elif connectorType == 'bparent':
            bindloc.bakedParent = connector

    def query(self, argument):
        if argument == self.ARG_INDEX:
            bindloc = self._bindLocatorToQuery
            if bindloc is None:
                return 0
            linkType = self.getArgumentValue(self.ARG_TYPE)
            if linkType == 'plug':
                connectorToFind = bindloc.relatedPlug
            elif linkType == 'socket':
                connectorToFind = bindloc.relatedSocket
            elif linkType == 'bparent':
                connectorToFind = bindloc.bakedParent
            else:
                connectorToFind = None

            if connectorToFind is None:
                return 0
            
            connectorsList = self._availableConnectorsList(bindloc)
            index = -1
            for n, connector in enumerate(connectorsList):
                if connector == connectorToFind:
                    index = n
                    break
            
            if index >= 0:
                return index + 1 # account for the (none) option
            
            return 0

    @property
    def _bindLocatorToQuery(self):
        for item in modo.Scene().selected:
            try:
                return rs.BindLocatorItem(item)
            except TypeError:
                continue
        return None

    def _buildPopup(self):
        """ Builds a popup that the command will present in UI.
        """
        entries = [('none', '(none)')]
        bindloc = self._bindLocatorToQuery
        if bindloc is not None:
            module = rs.Module(bindloc.moduleRootItem)
            elementSetType = self._getElementSetType()
            items = module[elementSetType]
            for item in items:
                rigItem = rs.Item.getFromModoItem(item)
                entries.append((item.id, rigItem.nameAndSide))
        return entries

    def _availableConnectorsList(self, bindloc):
        module = rs.Module(bindloc.moduleRootItem)
        elementSetType = self._getElementSetType()
        if elementSetType is not None:
            return module[elementSetType]
        return []

    def _getElementSetType(self):
        connectorType = self.getArgumentValue(self.ARG_TYPE)
        if connectorType == 'plug':
            return rs.c.ElementSetType.PLUGS
        elif connectorType == 'socket':
            return rs.c.ElementSetType.SOCKETS
        elif connectorType == 'bparent':
            return rs.c.ElementSetType.BIND_SKELETON
        return None

rs.cmd.bless(CmdBindLocatorConnectorPopup, 'rs.bindloc.setConnectorPopup')