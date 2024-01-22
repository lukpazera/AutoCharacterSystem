

import lx
import lxu
import modo
import modox

import rs


class CmdSelectModuleRoot(rs.Command):
    """ Selects edit module root item.
    """

    def execute(self, msg, flags):
        rsScene = rs.Scene()
        editRig = rsScene.editRig
        if editRig is None:
            return
        mod = editRig.modules.editModule
        if mod is None:
            return
        mod.rootModoItem.select(replace=True)
        modox.Item(mod.rootModoItem.internalItem).autoFocusInItemList()

rs.cmd.bless(CmdSelectModuleRoot, 'rs.module.selectRoot')