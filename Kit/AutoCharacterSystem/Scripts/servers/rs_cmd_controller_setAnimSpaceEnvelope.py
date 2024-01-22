
import lx
import modo
import modox

import rs
from rs import controller_dyna_space_op


class CmdControllerSetAnimationSpaceEnvelope(rs.Command):
    """ Sets or queries actor content type: items or channels.
    """

    ARG_ENVELOPE = 'envelope'

    def arguments(self):
        envelopeArg = rs.cmd.Argument(self.ARG_ENVELOPE, 'boolean')
        envelopeArg.flags = 'query'
        envelopeArg.defaultValue = False

        return [envelopeArg]

    def applyEditActionPost(self):
        return True

    def restoreItemSelection(self):
        return True

    def enable(self, msg):
        try:
            ctrl = self._getDynamicOrSwitcherControllers(first=True)[0]
        except IndexError:
            msg.set(rs.c.MessageTable.DISABLE, "dynaSpaceEnable")
            return False
        return True
        
    def execute(self, msg, flags):
        env = self.getArgumentValue(self.ARG_ENVELOPE)
        ctrls = self._getDynamicOrSwitcherControllers()
        for ctrl in ctrls:
            dynaSpaceOp = controller_dyna_space_op.ControllerDynamicSpaceOperator(ctrl)
            dynaSpaceOp.animatedDynamicSpace = env

    def query(self, argument):
        if argument == self.ARG_ENVELOPE:
            try:
                ctrl = self._getDynamicOrSwitcherControllers(first=True)[0]
            except IndexError:
                return

            dynaSpaceOp = controller_dyna_space_op.ControllerDynamicSpaceOperator(ctrl)
            return dynaSpaceOp.animatedDynamicSpace

    def notifiers(self):
        notifiers = []
        notifiers.append(('select.event', 'item element+d'))
        return notifiers
    
    # -------- Private methods

    def _getDynamicOrSwitcherControllers(self, first=False):
        """ Gets controllers items to display data for.
        
        Parameters
        ----------
        first : bool
            When true only first found controller will be returned
    
        Returns
        -------
        list of Controllers or empty list
        """
        controllers = []
        for item in modox.ItemSelection().getRaw():
            try:
                ctrl = rs.Controller(item)
            except TypeError:
                continue

            # Either switcher or needs to have dynamic space.
            if (ctrl.item.type == rs.c.RigItemType.SPACE_SWITCHER or
                    ctrl.animationSpace == rs.Controller.AnimationSpace.DYNAMIC):

                if first:
                    return [ctrl]
                controllers.append(ctrl)
        return controllers

rs.cmd.bless(CmdControllerSetAnimationSpaceEnvelope, 'rs.controller.animSpaceEnv')

