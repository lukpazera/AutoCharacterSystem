

import lx
import lxu
import modo

import rs


class CmdEditModulePopup(rs.Command):
    """ Sets or queries the edit module using popup list.
    """

    ARG_LIST = "list"

    def arguments(self):
        listArg = rs.cmd.Argument(self.ARG_LIST, 'integer')
        listArg.flags = 'query'
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        return [listArg]

    def query(self, argument):
        if argument == self.ARG_LIST:
            
            editRoot = rs.Scene.getEditRigRootItemFast()
            if editRoot is None:
                return 0

            modulesOp = rs.ModuleOperator(editRoot)
            modules = modulesOp.allModules
            modules = self._sortModules(modules)

            editModule = modulesOp.editModule
            if not editModule:
                return 0

            for n, module in enumerate(modules):
                if module == editModule:
                    return n

            return 0

    def execute(self, msg, flags):
        identIndex = self.getArgumentValue(self.ARG_LIST)
        if identIndex < 0:
            return
        scene = rs.Scene()
        editRig = scene.editRig
        
        if not editRig:
            return

        modules = editRig.modules.allModules
        modules = self._sortModules(modules)
        if identIndex < len(modules):
            moduleToSet = modules[identIndex]
            editRig.modules.editModule = moduleToSet
            if scene.contexts.current.edit and scene.contexts.isolateEditModule:
                scene.refreshContext()
            moduleToSet.rootModoItem.select(replace=True)
            
    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.extend(rs.NotifierSet.EDIT_MODULE_CHANGED)
        return notifiers

    def _buildPopup(self):
        entries = []
        rig = rs.Scene().editRig
        if rig is None or not rig:
            return entries
        modules = rig.modules.allModules
        modules = self._sortModules(modules)
        for mod in modules:
            entries.append((mod.sceneIdentifier, mod.nameAndSide))
        return entries

    def _sortModules(self, modules):
        d = {}
        for module in modules:
            d[module.referenceName] = module
        keys = list(d.keys())
        keys.sort()
        return [d[key] for key in keys]

rs.cmd.bless(CmdEditModulePopup, 'rs.module.editPopup')


class CmdEditModule(rs.base_OnModuleCommand):
    """ Sets edit module directly using module's root item ident.
    """

    def execute(self, msg, flags):
        ident = self.getArgumentValue(self.ARG_ROOT_ITEM)
        try:
            module = rs.Module(ident)
        except TypeError:
            return
        
        rigRoot = module.rigRootItem
        if rigRoot is None:
            return
        
        rig = rs.Rig(rigRoot)
        rig.modules.editModule = module
        
        # Changing to a edit module from different rig.
        # Change the edit rig then as well.
        rsScene = rs.Scene()
        if rsScene.editRig != rig:
            rs.run('rs.rig.edit {%s}' % rig.sceneIdentifier)

rs.cmd.bless(CmdEditModule, 'rs.module.edit')