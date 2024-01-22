

import lx
import lxu
import modo
import modox

import rs


class CmdSyncIKFK(rs.Command):

    ARG_RANGE = 'range'

    RANGE_HINTS = ((0, 'current'),
                   (1, 'explicit'),
                   (2, 'envelope'))

    def arguments(self):
        argRange = rs.command.Argument(self.ARG_RANGE, 'integer')
        argRange.hints = self.RANGE_HINTS
        argRange.defaultValue = 0
        argRange.flags = 'optional'

        return [argRange]

    def setupMode(self):
        return False

    def icon(self):
        range = self.getArgumentValue(self.ARG_RANGE)
        if range == 2: # envelope range
            return 'rs.ikfk.syncEnv'
        return 'rs.ikfk.syncCurrent'

    def basic_ButtonName(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)

    def cmd_Tooltip(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDTOOLTIP, key)

    def execute(self, msg, flags):
        switchers = self._getSwitchers()
        if not switchers:
            return

        range = self.getArgumentValue(self.ARG_RANGE)

        for switcher in switchers:
            switcher.sync(range, time=0.0)

    # -------- Private methods

    def _getMsgKey(self):
        range = self.getArgumentValue(self.ARG_RANGE)
        token = 'Env'
        if range == 0:  # current frame
            token = 'Frame'

        return 'ikfksync' + token

    def _getSwitchers(self):
        """
        Gets a list of IK/FK switcher features that will have matching performed on.

        We sync all chains for either rigs which items are selection or all selected rigs
        if no items are selected.
        """
        switchers = []
        rigs = {}

        # If no selection don't return anything
        selected = modox.ItemSelection().getRaw()

        # If we have selection, grab all rigs selected items belong to.
        for lxitem in selected:
            try:
                rigItem = rs.Item.getFromOther(lxitem)
            except TypeError:
                continue

            rigRoot =rigItem.rigRootItem
            rig = rs.Rig(rigRoot)
            if rig.sceneIdentifier in rigs:
                continue
            rigs[rig.sceneIdentifier] = rig

        # IF there are still no rigs, grab all selected rigs
        if rigs:
            rigs = list(rigs.values())
        else:
            rigs = rs.Scene().selectedRigs

        modules = []
        for rig in rigs:
            modules.extend(rig.modules.allModules)

        for module in modules:
            switchers.extend(module.getItemFeaturesByIdentifier(rs.c.ItemFeatureType.IKFK_SWITCHER))

        return switchers

rs.cmd.bless(CmdSyncIKFK, "rs.ikfk.sync")