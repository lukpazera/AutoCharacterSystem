
import lx
import lxu
import modo
import modox

import rs


class CmdSelectWeightMapInfluence(rs.RigCommand):
    """ Selects all vertices affected by currently selected weight map.
    """

    def restoreItemSelection(self):
        return True

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        if self._getBindLocator():
            return True
        vmapSelection = modox.VertexMapSelection()
        return len(vmapSelection.get(lx.symbol.i_VMAP_WEIGHT)) > 0

    def execute(self, msg, flags):
        bindLocator = self._getBindLocator()

        if bindLocator:
            self._selectInfluencedVerticesFromBindLocator(bindLocator)
        else:
            self._selectInfluencedVerticesFromWeightMaps()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        notifiers.append(modox.c.Notifier.SELECT_VMAP_DISABLE)
        return notifiers

    # -------- Private methods

    def _selectInfluencedVerticesFromBindLocator(self, bindLocator):
        deformers = modox.Effector(bindLocator.modoItem).deformers
        if deformers:
            rs.run('select.deformerMap deformer:{%s} mode:set' % deformers[0].id)
        if len(deformers) > 0:
            for x in range(1, len(deformers)):
                rs.run('select.deformerMap deformer:{%s} mode:add' % deformers[x].id)

    def _selectInfluencedVerticesFromWeightMaps(self):
        vmapSelection = modox.VertexMapSelection()
        selectedWeightMaps = vmapSelection.get(lx.symbol.i_VMAP_WEIGHT)

        rig = self.firstRigToEdit
        bindSkel = rs.BindSkeleton(rig)

        for bloc in bindSkel.items:
            blocmap = bloc.weightMapName
            if blocmap in selectedWeightMaps:
                self._selectInfluencedVerticesFromBindLocator(bloc)
                break

    def _getBindLocator(self):
        """
        Gets first bind locator from selected items.

        Returns
        -------
        BindLocatorItem
        """
        bindLocs = modox.ItemSelection().getRaw()
        for rawItem in bindLocs:
            try:
                return rs.BindLocatorItem(rawItem)
            except TypeError:
                continue
        return None

rs.cmd.bless(CmdSelectWeightMapInfluence, 'rs.bind.selectWMapInfluence')