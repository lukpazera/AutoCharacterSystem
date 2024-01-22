

import lx
import lxu
import modo

import rs


class CmdModuleName(rs.base_OnModuleCommand):
    """ Queries or sets module name.
    """

    ARG_NAME = 'name'

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)
        
        name = rs.cmd.Argument(self.ARG_NAME, 'string')
        name.flags = 'query'
        name.defaultValue = ''

        return [name] + superArgs

    def execute(self, msg, flags):
        moduleName = self.getArgumentValue(self.ARG_NAME)
        if not moduleName:
            return

        modules = self.modulesToEdit
        
        addNumberSuffix = False
        if len(modules) > 1:
            addNumberSuffix = True
        
        i = 1
        for mod in modules:
            if addNumberSuffix:
                mod.name = moduleName + str(i)
                i += 1
            else:
                mod.name = moduleName

    def query(self, argument):
        if argument == self.ARG_NAME:
            module = self.moduleToQuery
            if module is None:
                return ""
            return module.name

    def notifiers(self):
        notifiers = rs.base_OnModuleCommand.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers

rs.cmd.bless(CmdModuleName, 'rs.module.name')