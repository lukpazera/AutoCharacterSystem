

import os

import lx
import lxu
import modo
import modox

import rs


class CmdRigDeleteGuide(rs.RigCommand):
    """ Allows for deleting guide so the rig asset becomes a bit smaller.
    """

    def setupMode(self):
        return True

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        rootItem = rs.Scene.getEditRigRootItemFast()
        if rootItem:
            result = rs.Guide.isEditableFast(rootItem)  # type: bool
        else:
            result = False
        if not result:
            msg.set(rs.c.MessageTable.DISABLE, "delGuide")
        return result

    def interact(self):
        if rs.Scene().editRig is None:
            return False

        result = modo.dialogs.okCancel("Delete Guide", "You will not be able to adjust rig proportions after the Guide is removed.\nAre you sure you want to continue?")
        if result == 'cancel':
            return False
        return True

    def execute(self, msg, flags):
        rigsToEdit = self.rigsToEdit
        if not rigsToEdit:
            return

        for rig in rigsToEdit:
            guide = rs.Guide(rig)
            guide.selfDelete()

        rs.service.notify(rs.c.Notifier.UI_GENERAL, lx.symbol.fCMDNOTIFY_DISABLE)

rs.command.bless(CmdRigDeleteGuide, 'rs.rig.deleteGuide')