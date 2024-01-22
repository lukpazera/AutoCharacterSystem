

import lx
import lxu
import modo

import rs


class CmdItemAddGenericProperties (rs.Command):
    """ Adds generic rig properties to an item.
    """

    def arguments(self):
        return []

    def execute(self, msg, flags):
        scene = modo.Scene()

        for item in scene.selected:
            name = item.name
            basename = rs.acs2.Name.getBasename(name)
            if basename != name:
                name = basename
            rs.GenericItem.newFromExistingItem(modoItem=item, name=name)

rs.cmd.bless(CmdItemAddGenericProperties, "rs.item.addRigProperties")