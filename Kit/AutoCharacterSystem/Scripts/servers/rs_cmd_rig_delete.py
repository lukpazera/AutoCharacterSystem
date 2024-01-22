

import lx
import lxu
import modo

import rs


class CmdDeleteRig(rs.RigCommand):
    """ Deletes rig from a scene.

    Arguments
    ---------
    rootItem : str, optional
        Rig root item scene ident.
        Edit rig will deleted if this argument is not set.
    """

    def execute(self, msg, flags):
        rigs = self.rigsToEdit
        scene = rs.Scene()
        scene.deleteRig(rigs)

rs.cmd.bless(CmdDeleteRig, 'rs.rig.delete')