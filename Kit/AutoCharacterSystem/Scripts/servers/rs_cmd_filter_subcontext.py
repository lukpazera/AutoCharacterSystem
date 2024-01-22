

import lx
import lxu
import modo

import rs


class CmdSubcontextFilter(rs.Command):

    ARG_CONTEXT = 'context'
    ARG_SUBCONTEXT = 'sub'

    def arguments(self):
        context = rs.cmd.Argument(self.ARG_CONTEXT, 'string')
        
        subcontext = rs.cmd.Argument(self.ARG_SUBCONTEXT, 'string')

        return [context, subcontext]
    
    def basic_Enable (self, msg):
        context = self.getArgumentValue(self.ARG_CONTEXT)
        sub = self.getArgumentValue(self.ARG_SUBCONTEXT)

        return rs.Scene().contexts.getSubcontext(context) == sub

lx.bless(CmdSubcontextFilter, 'rs.filter.subcontext')