
import lx
import lxu
import modo
import modox

import rs


class CmdRetargetRigFilter (lxu.command.BasicCommand):

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

    def basic_Enable(self, msg):
        editRoot = rs.Scene.getEditRigRootItemFast()
        if editRoot is None:
            return False

        if editRoot.identifier == rs.Retargeting.RetargetRigIdentifier:
            return True
        return False

lx.bless(CmdRetargetRigFilter, 'rs.filter.bipedRetarget')