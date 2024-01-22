

import lx
import lxu
import modo

import rs


class CmdBindLocatorControllerPopup(rs.Command):
    """ Sets or queries controller related to bind locator item.
    
    The controller is set via a popup so this command is suitable
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
            relatedController = None
        else:
            availableControllers = self._getAvailableControllers(bindLoc)
            relatedController = availableControllers[index - 1]

        bindLoc.relatedControllers = relatedController.modoItem

    def query(self, argument):
        if argument == self.ARG_INDEX:
            bindLoc = self._bindLocatorToQuery
            if bindLoc is None:
                return 0
            relatedControllers = bindLoc.relatedControllers
            if not relatedControllers or len(relatedControllers) < 1:
                return 0
            
            relatedController = rs.Controller(relatedControllers[0])

            index = -1
            for n, ctrl in enumerate(self._getAvailableControllers(bindLoc)):
                if relatedController == ctrl:
                    index = n
                    break
            
            if index >= 0:
                return index + 1 # account for the (none) option
            
            return 0

    # -------- Private methods

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
    
    def _getAvailableControllers(self, rigItem):
        """
        
        Parameters
        ----------
        rigItem : Item
        
        Returns
        -------
        list of Controller
        """
        rigRoot = rigItem.rigRootItem
        moduleRoot = rigItem.moduleRootItem
        ctrlsSet = rs.ControllersElementSet(rigRoot)
        
        controllers = []
        
        for ctrlModoItem in ctrlsSet.elements:
            try:
                ctrl = rs.Controller(ctrlModoItem)
            except TypeError:
                continue
            if ctrl.item.moduleRootItem == moduleRoot:
                controllers.append(ctrl)
        
        return controllers
    
    def _buildPopup(self):
        """ Builds a popup that the command will present in UI.
        """
        entries = [('none', '(none)')]
        bindLoc = self._bindLocatorToQuery
        if bindLoc is not None:
            controllers = self._getAvailableControllers(bindLoc)
            for ctrl in controllers:
                entries.append((ctrl.modoItem.id, ctrl.item.nameAndSide))
        return entries

rs.cmd.bless(CmdBindLocatorControllerPopup, 'rs.bindloc.setControllerPopup')