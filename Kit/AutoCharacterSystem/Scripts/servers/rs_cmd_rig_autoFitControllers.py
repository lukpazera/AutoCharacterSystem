

import lx
import lxu
import modo

import rs
import rs.item_shape_fit


class CmdRigAutoFitControllers(rs.Command):
    """
    """

    def arguments(self):
        return []

    def execute(self, msg, flags):
        scene = modo.Scene()
        rsScene = rs.Scene()
        editRig = rsScene.editRig

        if not editRig:
            return None

        meshes = editRig.getElements(rs.c.ElementSetType.BIND_MESHES)
        ctrls = editRig.getElements(rs.c.ElementSetType.CONTROLLERS)
        itemShapeFitter = rs.item_shape_fit.ItemShapeFitter(meshes)
        
        for item in ctrls:
            try:
                rigItem = rs.ItemUtils.getItemFromModoItem(item)
            except TypeError:
                continue
            itemShapeFitter.autoFit(rigItem)

rs.cmd.bless(CmdRigAutoFitControllers, 'rs.rig.autoFitControllers')