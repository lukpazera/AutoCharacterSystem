

import lx
import lxu
import modo

import rs


class CmdSetSchematicView(rs.RigCommand):
    """ Sets schematic view to choosen rig content.

    """

    ARG_CONTENT = 'content'

    CONTENT_HINTS = ((0, 'module'),
                     (1, 'modGuide'),
                     (2, 'modRig'))

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        contentArg = rs.command.Argument(self.ARG_CONTENT, 'integer')
        contentArg.defaultValue = 0
        contentArg.hints = self.CONTENT_HINTS

        return [contentArg] + superArgs

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        if not rig:
            return

        content = self.getArgumentValue(self.ARG_CONTENT)
        contentItem = None

        module = rig.modules.editModule
        if not module:
            return

        if content == 0: # module
            contentItem = module.assemblyModoItem
        elif content == 1: # module guide
            try:
                contentItem = rs.ModuleGuide(module).guideAssemblies[0].modoItem
            except IndexError:
                pass
        elif content == 2:  # rig submodule
             contentItem = module.getFirstSubassemblyOfItemType(rs.c.RigItemType.MODULE_RIG_ASSM).modoItem

        if contentItem is not None:
            rs.run('!viewport.hide true tag LayoutMODOXXCentreLowerPanelVPTag down LayoutMODOXXCentreLowerTabVPKey LayoutMODOXXCentreLowerTabFVPTag')
            rs.run('schematic.setView mode:assembly group:{%s}' % contentItem.id)

rs.cmd.bless(CmdSetSchematicView, 'rs.schematic.setView')