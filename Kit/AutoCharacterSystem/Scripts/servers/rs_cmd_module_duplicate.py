

import lx
import lxu
import modo
import modox

import rs


class CmdDuplicateModule(rs.base_OnModuleCommand):
    """ Duplicates a module.
    
    This command does not work with multiselection.
    """

    ARG_OFFSET_X = 'offX'
    ARG_OFFSET_Y = 'offY'
    ARG_OFFSET_Z = 'offZ'

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)

        offX = rs.cmd.Argument(self.ARG_OFFSET_X, 'distance')
        offX.defaultValue = -0.1

        offY = rs.cmd.Argument(self.ARG_OFFSET_Y, 'distance')
        offY.defaultValue = 0.0

        offZ = rs.cmd.Argument(self.ARG_OFFSET_Z, 'distance')
        offZ.defaultValue = 0.1

        return [offX, offY, offZ] + superArgs

    def execute(self, msg, flags):
        module = self.moduleToQuery
        if module is None:
            return
        
        rigRoot = module.rigRootItem
        if rigRoot is None:
            return
        
        editRig = rs.Rig(rigRoot)
        dupModuleName = self._generateDuplicatedModuleName(module, editRig)

        dupModule = editRig.modules.duplicateModule(module)

        # We need to offset the module.
        offX = self.getArgumentValue(self.ARG_OFFSET_X)
        offY = self.getArgumentValue(self.ARG_OFFSET_Y)
        offZ = self.getArgumentValue(self.ARG_OFFSET_Z)

        modGuide = rs.ModuleGuide(dupModule)
        modGuide.offsetPosition(modo.Vector3(offX, offY, offZ))

        guide = rs.Guide(editRig)
        guide.apply([dupModule])

        dupModule.name = dupModuleName
        editRig.modules.editModule = dupModule
        rs.Scene().contexts.refreshCurrent()

    # -------- Private methods

    def _generateDuplicatedModuleName(self, dupModule, rig):
        names = [module.referenceName for module in rig.modules.allModules]
        x = names.count(dupModule.referenceName)
        return dupModule.name + str(x + 1)

rs.cmd.bless(CmdDuplicateModule, 'rs.module.duplicate')