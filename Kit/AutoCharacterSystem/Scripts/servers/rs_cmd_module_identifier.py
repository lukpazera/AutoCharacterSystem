

import lx
import lxu
import modo

import rs


class CmdModuleIdentifier(rs.base_OnModuleCommand):

    ARG_IDENTIFIER = 'identifier'

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)
                
        argIdent = rs.cmd.Argument(self.ARG_IDENTIFIER, 'string')
        argIdent.flags = 'query'
        
        return [argIdent] + superArgs

    def execute(self, msg, flags):
        ident = self.getArgumentValue(self.ARG_IDENTIFIER)
        module = self.moduleToQuery
        if module is not None:
            module.identifier = ident

    def query(self, argument):        
        if argument == self.ARG_IDENTIFIER:
            module = self.moduleToQuery
            if module is None:
                return None

            return module.identifier
        return None

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        notifiers.append((rs.c.Notifier.MODULE_PROPERTIES, '+d'))
        return notifiers

rs.cmd.bless(CmdModuleIdentifier, 'rs.module.identifier')
