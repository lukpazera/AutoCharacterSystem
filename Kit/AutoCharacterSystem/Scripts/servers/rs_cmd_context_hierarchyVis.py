

import lx
import modo
import rs


class CmdAssemblyContextHierarchyVisibility(rs.Command):

    ARG_STATE = 'state'
    
    def arguments(self):
        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = ['query']
        state.defaultValue = True

        return [state]

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def execute(self, msg, flags):
        state = self.getArgumentValue(self.ARG_STATE)   
        context = rs.ContextAssembly()
        context.storeHierarchyVisibility(state)
        rs.Scene().contexts.refreshCurrent()
        
    def query(self, argument):
        if argument == self.ARG_STATE:
            context = rs.ContextAssembly()
            return context.readHierarchyVisibility()
            
rs.cmd.bless(CmdAssemblyContextHierarchyVisibility, 'rs.context.assemblyHierarchyVis')