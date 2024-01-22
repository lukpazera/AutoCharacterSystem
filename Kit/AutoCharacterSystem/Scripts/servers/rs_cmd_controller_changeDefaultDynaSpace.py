import lx
import modo
import modox

import rs
from rs import controller_dyna_space_op


class CmdControllerChangeDefaultDynaSpace(rs.Command):
    """ Sets or queries actor content type: items or channels.
    """

    def setupMode(self):
        return True

    def applyEditActionPost(self):
        return True

    def enable(self, msg):
        ctrl, parent = self._getItems()
        if not ctrl or not parent:
            return False
        return ctrl.animationSpace == rs.Controller.AnimationSpace.DYNAMIC

    def execute(self, msg, flags):
        ctrl, parent = self._getItems()
        dynaSpaceOp = controller_dyna_space_op.ControllerDynamicSpaceOperator(ctrl)
        dynaSpaceOp.setDefaultSpace(parent)

    def notifiers(self):
        notifiers = []
        notifiers.append(('select.event', 'item element+d'))
        return notifiers

    # -------- Private methods

    def _getItems(self):
        controller = None
        parent = None
        for item in modo.Scene().selected:
            if controller is None:
                try:
                    controller = rs.Controller(item)
                except TypeError:
                    pass
                continue

            parent = item
            break

        return controller, parent

rs.cmd.bless(CmdControllerChangeDefaultDynaSpace, 'rs.controller.changeDefaultDynaSpace')

