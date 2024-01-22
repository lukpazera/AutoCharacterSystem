

import lx
import lxu
import modo

import rs


class CmdModuleSymmetricModulePopup(rs.base_OnModuleCommand):
    """ Sets or queries module that acts as symmetry reference for another module.
    """

    ARG_SYMMETRY_MODULE_INDEX = 'index'

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)
                
        argSymModule = rs.cmd.Argument(self.ARG_SYMMETRY_MODULE_INDEX, 'integer')
        argSymModule.flags = 'query'
        argSymModule.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        argSymModule.valuesList = self._buildPopup
        
        return [argSymModule] + superArgs

    def execute(self, msg, flags):
        index = self.getArgumentValue(self.ARG_SYMMETRY_MODULE_INDEX)

        if index == 0:
            symModule = None
        else:
            index -= 1
            symModulesList = self._availableSymmetryModules
            if index >= len(symModulesList):
                return
            symModule = symModulesList[index]

        for moduleToEdit in self.modulesToEdit:
            moduleOp = rs.ModuleOperator(moduleToEdit.rigRootItem)
            if symModule is None:
                moduleOp.clearSymmetry(moduleToEdit)
            else:
                moduleOp.setSymmetry(moduleToEdit, symModule)

        # If we are in guide context we need to refresh the context.
        rsScene = rs.Scene()
        if rsScene.contexts.current == rs.c.Context.GUIDE:
            rsScene.contexts.refreshCurrent()

    def query(self, argument):
        if argument == self.ARG_SYMMETRY_MODULE_INDEX:
            module = self.moduleToQuery
            if module is None:
                return

            currentSymModule = module.symmetricModule
            if currentSymModule is None:
                return 0

            index = -1
            for n, mod in enumerate(self._availableSymmetryModules):
                if mod == currentSymModule:
                    index = n
                    break
            
            if index >= 0:
                return index + 1 # account for the (none) option
            
            return 0

    # -------- Private methods

    @property
    def _availableSymmetryModules(self):
        """ Gets a list of modules that can be used as
        symmetry reference for a given module.
        
        Returns
        -------
        list of module
        """
        
        module = self.moduleToQuery
        if module is None:
            return []
        
        if module.side == rs.c.Side.CENTER:
            return []

        moduleRigRoot = module.rigRootItem
        if moduleRigRoot is None:
            return []
        
        rig = rs.Rig(moduleRigRoot)
        modules = rig.modules.allModules
                
        sideToQuery = rs.c.Side.RIGHT
        if module.side == rs.c.Side.RIGHT:
            sideToQuery = rs.c.Side.LEFT

        symList = []
        moduleIdentifier = module.identifier

        for m in modules:
            if m == module:
                continue
            if m.identifier != moduleIdentifier:
                continue

            if m.side == sideToQuery:
                symList.append(m)
        
        return symList

    def _buildPopup(self):
        """ Builds a popup that the command will present in UI.
        """
        entries = [('none', '(none)')]
        modules = self._availableSymmetryModules
        for module in modules:
            entries.append((module.sceneIdentifier, module.nameAndSide))
        return entries

rs.cmd.bless(CmdModuleSymmetricModulePopup, 'rs.module.symmetricModulePopup')