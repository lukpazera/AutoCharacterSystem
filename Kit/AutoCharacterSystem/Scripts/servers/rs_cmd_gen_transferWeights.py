
import lx
import lxu
import modo
import modox

import rs


class CmdTransferWeights(modox.Command):
    """
    Transfers all or selected weight maps between one source and multiple target meshes.

    This command does not need the rig to be present in the scene, it's a generic
    command that can work stand-alone.
    """

    ARG_METHOD = 'method'
    ARG_SKIP_EMPTY = 'skipEmpty'

    METHOD_HINTS = ((0, 'distance'),
                    (1, 'raycast'))

    METHOD_INT_TO_STRING_CONSTANT = {0: rs.Bind.TransferMethod.DISTANCE,
                                     1: rs.Bind.TransferMethod.RAYCAST}

    def arguments(self):
        argMethod = modox.Argument(self.ARG_METHOD, 'integer')
        argMethod.defaultValue = 0
        argMethod.hints = self.METHOD_HINTS

        argSkipEmpty = modox.Argument(self.ARG_SKIP_EMPTY, 'boolean')
        argSkipEmpty.defaultValue = True
        argSkipEmpty.flags = 'optional'

        return [argMethod, argSkipEmpty]

    def enable(self, msg):
        try:
            self._getMeshes()
        except LookupError:
            msg.set(rs.c.MessageTable.DISABLE, "transWeightsMesh")
            return False
        if not self._getWeightMaps():
            msg.set(rs.c.MessageTable.DISABLE, "transWeightsMap")
            return False
        return True

    def setupMode(self):
        return True

    def execute(self, msg, flags):
        meshFrom, meshesTo = self._getMeshes()

        transferMethodInt = self.getArgumentValue(self.ARG_METHOD)
        transferMethod = self.METHOD_INT_TO_STRING_CONSTANT[transferMethodInt]
        skipEmptyMaps = self.getArgumentValue(self.ARG_SKIP_EMPTY)

        wmaps =self._getWeightMaps()

        ticks = 500 * len(meshesTo)
        monitor = modox.Monitor(ticks, "Transfer Weight Maps")

        for meshTo in meshesTo:
            modox.VertexMapUtils.transferWeights(meshFrom,
                                                 meshTo,
                                                 wmaps,
                                                 transferMethod,
                                                 skipEmptyMaps,
                                                 monitor,
                                                 ticks)

        monitor.release()

        modox.VertexMapSelection().setByCommand(wmaps,
                                                lx.symbol.i_VMAP_WEIGHT,
                                                modox.SelectionMode.REPLACE,
                                                clearAll=True)

    def notifiers(self):
        notifiers = []
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        notifiers.append(modox.c.Notifier.SELECT_VMAP_DISABLE)
        return notifiers

    # -------- Private methods

    def _getMeshes(self):
        """ Gets meshes for the transfer.

        Meshes are picked up from current selection.
        First selected mesh is source mesh, the rest are target meshes.

        Returns
        -------
        modo.Item, [modo.Item]
            Source mesh, target meshes (as list).
        """
        selectedMeshes = modo.Scene().selectedByType('mesh')
        if not selectedMeshes or len(selectedMeshes) < 2:
            raise LookupError

        return selectedMeshes[0], selectedMeshes[1:]

    def _getWeightMaps(self):
        vmapSelection = modox.VertexMapSelection()
        return vmapSelection.get(lx.symbol.i_VMAP_WEIGHT)

rs.cmd.bless(CmdTransferWeights, 'rs.weights.transfer')