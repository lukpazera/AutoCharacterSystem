

import lx
import lxu
import modo

import rs


class CmdUIState(rs.Command):
    """ Queries or sets mesh editing mode.
    
    Mesh edit mode dictates what kind of meshes related to the rig
    can be edited at a given point: bind meshes, rigid meshes or bind proxies.
    """

    ARG_STATE_IDENT = 'stateId'
    ARG_STATE_VALUE = 'stateValue'
    ARG_ENABLE = 'enable'

    def arguments(self):
        ident = rs.cmd.Argument(self.ARG_STATE_IDENT, 'string')
        
        value = rs.cmd.Argument(self.ARG_STATE_VALUE, 'string')
        
        enable = rs.cmd.Argument(self.ARG_ENABLE, 'boolean')
        enable.flags = ['query', 'optional']
        enable.defaultValue = False
        
        return [ident, value, enable]

    def uiHints(self, argument, hints):
        if argument == self.ARG_ENABLE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)
        
    def execute(self, msg, flags):
        ident = self.getArgumentValue(self.ARG_STATE_IDENT)
        value = self.getArgumentValue(self.ARG_STATE_VALUE)
        enable = self.getArgumentValue(self.ARG_ENABLE)
        if enable:
            rs.service.ui.setState(ident, value)
            rs.service.notify(rs.c.Notifier.UI_GENERAL, rs.c.Notify.DATATYPE)

    def query(self, argument):
        if argument == self.ARG_ENABLE:
            ident = self.getArgumentValue(self.ARG_STATE_IDENT)
            currentMode = rs.service.ui.getState(ident)
            value = self.getArgumentValue(self.ARG_STATE_VALUE)
            if value == currentMode:
                return True
            return False

rs.cmd.bless(CmdUIState, "rs.ui.state")