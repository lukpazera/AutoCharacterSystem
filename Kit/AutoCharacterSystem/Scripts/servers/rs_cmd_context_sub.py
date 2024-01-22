
import lx
import modo
import rs


class CmdSubcontext(rs.Command):

    ARG_CONTEXT = 'context'
    ARG_SUBCONTEXT = 'sub'
    ARG_STATE = 'state'
    
    def arguments(self):
        context = rs.cmd.Argument(self.ARG_CONTEXT, 'string')
        subcontext = rs.cmd.Argument(self.ARG_SUBCONTEXT, 'string')
        
        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = ['query', 'optional']
        state.defaultValue = False

        return [context, subcontext, state]

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def execute(self, msg, flags):

        contextid = self.getArgumentValue(self.ARG_CONTEXT)
        subcontext = self.getArgumentValue(self.ARG_SUBCONTEXT)
        state = self.getArgumentValue(self.ARG_STATE)
        
        if not state:
            return

        rs.Scene().contexts.setSubcontext(contextid, subcontext)
        rs.service.notify(rs.c.Notifier.UI_GENERAL, rs.c.Notify.DATATYPE)
        
    def query(self, argument):
        if argument == self.ARG_STATE:
            contextid = self.getArgumentValue(self.ARG_CONTEXT)
            subcontextid = self.getArgumentValue(self.ARG_SUBCONTEXT)
            
            sub = rs.Scene().contexts.getSubcontext(contextid)
            return sub == subcontextid
        
rs.cmd.bless(CmdSubcontext, 'rs.subcontext')