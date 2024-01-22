

import lx
import lxu
import modo

import rs


class CmdRigFromDroppedPreset(rs.Command):
    """ Initialises new rig in scene from dropped rig preset.
    """

    ARG_ROOT_ITEM = 'rootItem'

    def arguments(self):
        itemArg = rs.command.Argument(self.ARG_ROOT_ITEM, '&item')
        itemArg.defaultValue = ''
        
        return [itemArg]

    def notifiers(self):
        """ New rig command is always enabled and doesn't need any notifiers.

        By returning empty list we clear any default notifiers.
        """
        return []

    def enable(self, msg):
        """ This command is always enabled.
        By returning True we override any default enable state behaviour.
        """
        return True

    def execute(self, msg, flags):
        rootItemIdent = self.getArgumentValue(self.ARG_ROOT_ITEM)
        scene = modo.Scene()
        try:
            rootModoItem = scene.item(rootItemIdent)
        except LookupError:
            return
        newRig = rs.Rig.fromSetupInScene(rootModoItem)
        rsScene = rs.Scene()
        rsScene.editRig = newRig
        rsScene.refreshContext()


rs.command.bless(CmdRigFromDroppedPreset, 'rs.rig.fromDroppedPreset')