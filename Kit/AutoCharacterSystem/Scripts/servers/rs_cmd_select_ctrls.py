

import lx
import modo
import modox

import rs


class CmdSelectControllers(rs.RigCommand):

    ARG_SET = 'set'

    SET_HINTS = ((0, 'all'),
                 (1, 'pose'),
                 (2, 'keyed'),
                 (3, 'translate'))

    ICON = {0: 'rs.select.ctrls.all',
            1: 'rs.select.ctrls.pose',
            2: 'rs.select.ctrls.keyed',
            3: 'rs.select.ctrls.translate'}

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argSet = rs.cmd.Argument(self.ARG_SET, 'integer')
        argSet.hints = self.SET_HINTS
        argSet.defaultValue = 0

        return [argSet] + superArgs

    def icon(self):
        setToSelect = self.getArgumentValue(self.ARG_SET)
        return self.ICON[setToSelect]
    
    def execute(self, msg, flags):
        setToSelect = self.getArgumentValue(self.ARG_SET)
        itemSelection = modox.ItemSelection()
        ctrlsToSelect = self._getControllersToSelect(setToSelect)
        itemSelection.set(ctrlsToSelect, modox.SelectionMode.REPLACE, batch=True)

    # -------- Private methods

    def _getControllersToSelect(self, setToSelect):
        controllers = []
        for rig in rs.Scene().selectedRigs:
            if setToSelect == 0:  # all
                controllers.extend(rig[rs.c.ElementSetType.CONTROLLERS].elements)
            elif setToSelect == 1:  # posing
                ctrlIFs = rs.Pose(rig).allControllers
                ctrls = [ctrl.modoItem for ctrl in ctrlIFs]
                controllers.extend(ctrls)
            elif setToSelect == 2:  # Keyframed at current time.
                ctrlIFs = rs.Pose(rig).getKeyframedControllers()
                ctrls = [ctrl.modoItem for ctrl in ctrlIFs]
                controllers.extend(ctrls)
        return controllers

rs.cmd.bless(CmdSelectControllers, "rs.select.controllers")
