

import lx
import lxu
import modo
import modox

import rs


class CmdActionMirror(rs.RigCommand):

    def applyEditActionPre(self):
        return True

    def applyEditActionPost(self):
        return True

    def setupMode(self):
        return False

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        action = rs.Action(rig)
        action.mirror()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_LABEL)
        return notifiers

    # -------- Private methods

rs.cmd.bless(CmdActionMirror, "rs.action.mirror")