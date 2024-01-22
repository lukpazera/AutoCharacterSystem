
import lx
import modo

import rs
from rs import controller_dyna_space_op


class CmdControllerAnimationSpace(rs.base_OnItemFeatureCommand):
    """ Sets or queries actor content type: items or channels.
    """

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.Controller
    
    ARG_SPACE = 'space'

    SPACE_HINT = (
        (0, rs.Controller.AnimationSpace.FIXED),
        (1, rs.Controller.AnimationSpace.DYNAMIC),
    )

    SPACE_TO_INT = {rs.Controller.AnimationSpace.FIXED: 0,
                      rs.Controller.AnimationSpace.DYNAMIC: 1}

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
                
        content = rs.cmd.Argument(self.ARG_SPACE, 'integer')
        content.flags = 'query'
        content.defaultValue = rs.Controller.AnimationSpace.FIXED
        content.hints = self.SPACE_HINT

        return [content] + superArgs

    def restoreItemSelection(self):
        return True

    def setupMode(self):
        return True

    def execute(self, msg, flags):
        space = self.getArgumentValue(self.ARG_SPACE)
        for ctrl in self.itemFeaturesToEdit:
            dynaSpaceOp = controller_dyna_space_op.ControllerDynamicSpaceOperator(ctrl)
            if space == rs.Controller.AnimationSpaceInt.DYNAMIC:
                dynaSpaceOp.setAnimationSpaceToDynamic()
            else:
                dynaSpaceOp.setAnimationSpaceToFixed()

    def query(self, argument):
        if argument == self.ARG_SPACE:
            try:
                ctrl = self.itemFeatureToQuery
            except IndexError:
                return

            return self.SPACE_TO_INT[ctrl.animationSpace]

rs.cmd.bless(CmdControllerAnimationSpace, 'rs.controller.animSpace')

