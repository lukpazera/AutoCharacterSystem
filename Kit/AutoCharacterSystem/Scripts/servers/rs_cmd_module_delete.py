

import lx
import lxu
import modo
import modox

import rs


class CmdDeleteModule(rs.base_OnModuleCommand):
    """ Deletes module.

    Deletes module with given root item or current edit module
    if the argument is not set.
    
    By default all child modules are deleted as well.
    """

    def execute(self, msg, flags):
        modules = self.modulesToEdit

        modsToDelete = []

        for module in modules:
            # Delete each module hierarchy separately.
            rig = rs.Rig(module.rigRootItem)
            
            modsToDelete.append(module)

            deleteHierarchy = False
            modulesMap = rig.modules.modulesMap
            if deleteHierarchy:
                modsToDelete.extend(modulesMap.getDependentModules(module, recursive=True))
                modsToDelete.reverse()
            else:
                # When not deleting hierarchy I first have to disconnect children modules from the module
                # That is about to be deleted. We do not want any leftover links.
                modulesToDisconnect = modulesMap.getDependentModules(module, recursive=False)
                for disModule in modulesToDisconnect:
                    disModule.disconnectFromModule(module)

            # Add submodules but make sure that we're not adding submodules
            # that were selected by user directly and are on the list to delete already.
            submodules = module.submodules
            for submod in submodules:
                if submod in modsToDelete:
                    continue
                modsToDelete.append(submod)

        # Add any symmetrical modules to the list
        # We only want to add symmetrical modules if we are processing
        # symmetry reference module. This way when we delete module that has
        # symmetry reference it doesn't delete the source but when
        # symmetry reference module is deleted it takes a module that's linked to it via
        # its symmetry property.
        symLinkedModules = []
        for module in modsToDelete:
            symMods = module.getSymmetryLinkedModules(reference=False, driven=True)
            for symMod in symMods:
                if symMod not in modsToDelete and symMod not in symLinkedModules:
                    symLinkedModules.append(symMod)
        modsToDelete.extend(symLinkedModules)

        for module in modsToDelete:
            module.selfDelete()

        modox.ItemSelection().clear()

    def notifiers(self):
        notifiers = rs.base_OnModuleCommand.notifiers(self)

        # For the popup to refresh command needs to react to
        # datatype change when new rig root item is added or removed
        notifiers.append(('item.event', "add[%s] +t" % rs.c.RigItemType.MODULE_ROOT))
        notifiers.append(('item.event', "remove[%s] +t" % rs.c.RigItemType.MODULE_ROOT))

        # React to changes to current Rig graph as well
        # this changes current selection.
        notifiers.append(('graphs.event', '%s +t' % rs.module_op.ModuleOperator.GRAPH_EDIT_MODULE))
        notifiers.append(('graphs.event', '%s +t' % rs.Scene.GRAPH_EDIT_RIG))

        return notifiers

rs.cmd.bless(CmdDeleteModule, 'rs.module.delete')