

import lx
import lxu
import modo
import modox

import rs


class CmdIsolateEditModule(rs.Command):

    ARG_STATE = 'state'

    def arguments(self):
        argState = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        argState.flags = 'query'
        argState.defaultValue = False
        return [argState]

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)
            
    def execute(self, msg, flags):
        state = self.getArgumentValue(self.ARG_STATE)
        scene = rs.Scene()
        scene.contexts.isolateEditModule = state
        if scene.contexts.current.edit:
            scene.refreshContext()

    def query(self, argument):
        if argument == self.ARG_STATE:
            scene = rs.Scene()
            return scene.contexts.isolateEditModule
        
rs.cmd.bless(CmdIsolateEditModule, 'rs.module.isolateEdit')