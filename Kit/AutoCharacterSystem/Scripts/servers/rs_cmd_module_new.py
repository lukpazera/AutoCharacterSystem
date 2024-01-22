

import lx
import lxu
import modo
import modox

import rs


class CmdNewModule(rs.Command):
    """
    """

    ARG_NAME = 'name'
    ARG_FROM_ASSEMBLY = 'fromAssm'
    ARG_ASSEMBLY = 'assm'
    
    def arguments(self):
        name = rs.cmd.Argument(self.ARG_NAME, 'string')
        name.flags = ['optional']
        name.defaultValue = None

        fromAssm = rs.cmd.Argument(self.ARG_FROM_ASSEMBLY, 'boolean')
        fromAssm.flags = ['optional']
        fromAssm.defaultValue = False
        
        assm = rs.cmd.Argument(self.ARG_ASSEMBLY, '&item')
        assm.flags = ['optional']
        
        return [name, fromAssm, assm]
    
    def execute(self, msg, flags):
        moduleName = self.getArgumentValue(self.ARG_NAME)

        editRig = rs.Scene().editRig
        if editRig is None:
            return
        
        assemblyItem = self._assembly

        if assemblyItem is not None:
            newModule = editRig.modules.newModuleFromAssembly(assemblyItem)
        else:
            newModule = editRig.modules.newModule(name=moduleName)

        modox.Item(newModule.rootModoItem.internalItem).autoFocusInItemList()
        rs.run('rs.subcontext assembly dev 1')

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append((rs.c.Notifier.ACCESS_LEVEL, '+d'))
        return notifiers

    # -------- Private methods
    
    @property
    def _assembly(self):
        if not self.getArgumentValue(self.ARG_FROM_ASSEMBLY):
            return None

        scene = modo.Scene()

        if self.isArgumentSet(self.ARG_ASSEMBLY):
            assmid = self.getArgumentValue(self.ARG_ASSEMBLY)
            try:
                return scene.item(assmid)
            except LookupError:
                return None
        else:
            for item in scene.selected:
                if item.type == 'assembly':
                    return item
        return None

rs.cmd.bless(CmdNewModule, 'rs.module.new')