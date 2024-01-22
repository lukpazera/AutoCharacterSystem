

import lx
import lxu
import modo

import rs


class CmdItemStandardize(rs.Command):
    """ Clears all rig properties from an item.
    """

    def arguments(self):
        return []

    def execute(self, msg, flags):
        scene = modo.Scene()
        for item in scene.selected:
            try:
                rigItem = rs.Item.getFromModoItem(item)
            except TypeError:
                continue
            # Note that this code is duplicated in Rig when standardising entire rig.
            # TODO: Figure out a way to make it a separate function somewhere so this
            # code is written only once.
            featureOp = rs.ItemFeatures(rigItem)
            featureOp.removeAllFeatures(silent=True)
            rigItem.standardise()

rs.cmd.bless(CmdItemStandardize, "rs.item.clearRigProperties")