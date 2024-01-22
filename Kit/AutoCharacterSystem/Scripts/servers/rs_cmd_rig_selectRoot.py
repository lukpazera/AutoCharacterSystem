

import lx
import lxu
import modo
import modox

import rs


class CmdSelectRigRoot(rs.Command):
    """ Selects edit rig root item.
    """

    def execute(self, msg, flags):
        rsScene = rs.Scene()
        editRig = rsScene.editRig
        if editRig is None:
            return
        editRig.rootModoItem.select(replace=True)
        modox.Item(editRig.rootModoItem.internalItem).autoFocusInItemList()

rs.cmd.bless(CmdSelectRigRoot, 'rs.rig.selectRoot')