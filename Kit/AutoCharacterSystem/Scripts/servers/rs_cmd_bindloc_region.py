
import lx
import lxu
import modo

import rs


class CmdBindLocatorRegionPopup(rs.Command):
    """ Sets or queries region related to bind locator item.

    The region item is set via a popup so this command is suitable
    for putting it into UI but not for using it from scripts.
    """

    ARG_INDEX = 'popupIndex'

    def arguments(self):
        index = rs.cmd.Argument(self.ARG_INDEX, 'integer')
        index.flags = 'query'
        index.valuesList = self._buildPopup
        index.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        return [index]

    def execute(self, msg, flags):
        index = self.getArgumentValue(self.ARG_INDEX)

        bindLoc = self._bindLocatorToQuery
        if bindLoc is None:
            return

        if index == 0:
            relatedRegion = None
        else:
            regionsList = self._getModuleRegions(bindLoc)
            relatedRegion = regionsList[index - 1].modoItem

        bindLoc.relatedCommandRegion = relatedRegion

    def query(self, argument):
        if argument == self.ARG_INDEX:
            bindLoc = self._bindLocatorToQuery
            if bindLoc is None:
                return 0
            relatedRegionModoItem = bindLoc.relatedCommandRegion
            if relatedRegionModoItem is None:
                return 0

            relatedRegion = rs.Item.getFromModoItem(relatedRegionModoItem)
            regionsList = self._getModuleRegions(bindLoc)

            index = -1
            for n, rigItem in enumerate(regionsList):
                if relatedRegion == rigItem:
                    index = n
                    break

            if index >= 0:
                return index + 1  # account for the (none) option

            return 0

    # -------- Private methods

    def _getModuleRegions(self, bindLoc):
        module = rs.Module(bindLoc.moduleRootItem)
        rigClayOp = rs.RigClayModuleOperator(module)
        regionsList = rigClayOp.polygonRegions
        return rs.ItemUtils.sortRigItemsByName(regionsList)

    @property
    def _bindLocatorToQuery(self):
        """ Gets bind locator that will be used for querying a list of controllers.

        Returns
        -------
        BindLocatorItem or None
        """
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
        bindLoc = self._bindLocatorToQuery
        if bindLoc is not None:
            regionsList = self._getModuleRegions(bindLoc)
            for rigItem in regionsList:
                entries.append((rigItem.modoItem.id, rigItem.name))
        return entries

rs.cmd.bless(CmdBindLocatorRegionPopup, 'rs.bindloc.setRegionPopup')