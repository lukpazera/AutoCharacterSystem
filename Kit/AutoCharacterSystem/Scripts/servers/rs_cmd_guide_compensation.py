
import lx
import lxu
import modo
import modox

x = modox.TransformToolsUtils()

import rs


class CmdGuideCompensation(rs.Command):
    """ Toggles child compensation mode on/off for transform tools.
    """

    ARG_STATE = 'state'
    
    def arguments(self):
        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = 'query'

        return [state]
    
    def enable(self, msg):
        if x.moveItem or x.rotateItem or x.transformItem:
            return True
        return False
    
    def applyEditActionPre(self):
        return True

    def execute(self, msg, flags):
        state = int(self.getArgumentValue(self.ARG_STATE))
        modox.TransformToolsUtils().childCompensation = state
    
    def query(self, argument):
        if argument == self.ARG_STATE:
            try:
                state = modox.TransformToolsUtils().childCompensation
            except RuntimeError:
                state = False
            return state
            
    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('notifier.tool.set', 'TransformMove'))
        notifiers.append(('notifier.tool.set', 'TransformRotate'))
        notifiers.append(('notifier.tool.set', 'TransformScale'))
        notifiers.append(('notifier.tool.set', 'Transform'))
        return notifiers

rs.cmd.bless(CmdGuideCompensation, 'rs.guide.compensation')