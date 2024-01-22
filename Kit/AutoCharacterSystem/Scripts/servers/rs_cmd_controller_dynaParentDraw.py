
import lx
import modo

import rs


class CmdControllerDynaParentDraw(rs.Command):
    """ Toggles drawing of dynamic parent link for a controller.
    """

    ARG_DRAW = 'draw'

    def arguments(self):
        drawArg = rs.cmd.Argument(self.ARG_DRAW, 'boolean')
        drawArg.flags = 'query'
        drawArg.defaultValue = False

        return [drawArg]

    def setupMode(self):
        return False

    def enable(self, msg):
        try:
            ctrl = self._getControllers(first=True)[0]
        except IndexError:
            msg.set(rs.c.MessageTable.DISABLE, "dynaParentLink")
            return False
        
        result = (ctrl.animationSpace == rs.Controller.AnimationSpace.DYNAMIC and
                  ctrl.dynamicSpace.isAnimated)
        if not result:
            msg.set(rs.c.MessageTable.DISABLE, "dynaParentLink")
        return result
        
    def execute(self, msg, flags):
        draw = self.getArgumentValue(self.ARG_DRAW)
        ctrls = self._getControllers()
        for ctrl in ctrls:
            ctrl.dynamicSpace.draw = draw

    def query(self, argument):
        if argument == self.ARG_DRAW:
            try:
                ctrl = self._getControllers(first=True)[0]
            except IndexError:
                return False

            return ctrl.dynamicSpace.draw

    def notifiers(self):
        notifiers = []
        notifiers.append(('select.event', 'item element+d'))
        return notifiers
    
    # -------- Private methods

    def _getControllers(self, first=False):
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
        for item in modo.Scene().selected:
            try:
                ctrl = rs.Controller(item)
            except TypeError:
                continue
            if first:
                return [ctrl]
            controllers.append(ctrl)
        return controllers

rs.cmd.bless(CmdControllerDynaParentDraw, 'rs.controller.dynaParentDraw')

