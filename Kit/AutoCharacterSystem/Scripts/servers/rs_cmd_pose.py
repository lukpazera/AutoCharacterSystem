

import lx
import lxu
import modo
import modox

import rs


class CmdPoseCopy(rs.RigCommand):

    def icon(self):
        rig = rs.Scene().firstSelectedRig
        if rig:
            pose = rs.Pose(rig)
            if pose.currentScopeIsSelection:
                return 'rs.pose.copySelected'
        return 'rs.pose.copy'

    def execute(self, msg, flags):
        rig = rs.Scene().firstSelectedRig
        pose = rs.Pose(rig)
        pose.copy()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_LABEL)
        return notifiers

rs.cmd.bless(CmdPoseCopy, "rs.pose.copy")


class CmdPosePaste(rs.RigCommand):

    def execute(self, msg, flags):
        rigs = rs.Scene().selectedRigs
        buffer = None
        for rig in rigs:
            pose = rs.Pose(rig)
            buffer = pose.paste(buffer=buffer)

rs.cmd.bless(CmdPosePaste, "rs.pose.paste")


class CmdPoseMirror(rs.RigCommand):

    def icon(self):
        rig = rs.Scene().firstSelectedRig
        if rig:
            pose = rs.Pose(rig)
            if pose.currentScopeIsSelection:
                return 'rs.pose.mirrorSelected'
        return 'rs.pose.mirror'

    def execute(self, msg, flags):
        for rig in rs.Scene().selectedRigs:
            pose = rs.Pose(rig)
            pose.mirror()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_LABEL)
        return notifiers

rs.cmd.bless(CmdPoseMirror, "rs.pose.mirror")


class CmdPoseMirrorOneWay(rs.RigCommand):

    ARG_MODE = 'mode'

    MODE_HINTS = ((0, 'push'),
                  (1, 'pull'))

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        mode = rs.cmd.Argument(self.ARG_MODE, 'integer')
        mode.defaultValue = 0
        mode.hints = self.MODE_HINTS

        return [mode] + superArgs

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        if modox.ItemSelection().size == 0:
            msg.set(rs.c.MessageTable.DISABLE, "mirrorOneWay")
            return False

        return True

    def icon(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        if mode == 0:  # push
            return 'rs.pose.mirrorPush'
        return 'rs.pose.mirrorPull'

    def basic_ButtonName(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)

    def cmd_Tooltip(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDTOOLTIP, key)

    def execute(self, msg, flags):
        mode = self.getArgumentValue(self.ARG_MODE)
        for rig in rs.Scene().selectedRigs:
            pose = rs.Pose(rig)
            if mode == 0:  # push
                pose.mirrorPush()
            elif mode == 1:  # pull
                pose.mirrorPull()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_LABEL)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getMsgKey(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        token = 'Push'
        if mode == 1:  # pull
            token = 'Pull'

        return 'mirror' + token

rs.cmd.bless(CmdPoseMirrorOneWay, "rs.pose.mirrorOneWay")