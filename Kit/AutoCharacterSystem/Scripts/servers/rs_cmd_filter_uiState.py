

import lx
import lxu
import modo

import rs


class CmdUIStateFilter(rs.Command):
    """ This command is used as a filter command for a form.
    When this command's enable state returns true the form 
    will be visible. It'll be hidden otherwise.
    
    More information here:
    http://modo.sdk.thefoundry.co.uk/wiki/Form_Filtering
    """

    ARG_STATE_ID = 'stateid'
    ARG_STATE_VALUE = 'value'

    def arguments(self):
        argStateId = rs.cmd.Argument(self.ARG_STATE_ID, 'string')
        
        argStateValue = rs.cmd.Argument(self.ARG_STATE_VALUE, 'string')

        return [argStateId, argStateValue]
    
    def basic_Enable (self, msg):
        stateId = self.getArgumentValue(self.ARG_STATE_ID)
        value = self.getArgumentValue(self.ARG_STATE_VALUE)

        return rs.service.ui.getState(stateId) == value

lx.bless(CmdUIStateFilter, 'rs.filter.uiState')