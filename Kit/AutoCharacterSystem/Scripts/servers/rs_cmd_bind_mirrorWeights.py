

import lx
import lxu
import modo
import modox

import rs


class CmdBindMirrorWeights(rs.Command):
    """ Mirrors weights.

    Note that for mirroring to work properly symmetry mode has to be ON
    in MODO UI!!! This command handles that but the internal C++ command
    that is actually doing the mirroring is not!
    """

    ARG_FROM_SIDE = 'fromSide'
    ARG_SYMMETRY_TYPE = 'symType'

    SIDE_HINTS = (
        (0, 'right'),
        (1, 'left')
    )

    SYMMETRY_TYPE_HINTS = ((0, 'default'),
                           (1, 'topology'))

    def arguments(self):
        argFromSide = rs.cmd.Argument(self.ARG_FROM_SIDE, 'integer')
        argFromSide.defaultValue = 0
        argFromSide.hints = self.SIDE_HINTS

        argSymmetryType = rs.cmd.Argument(self.ARG_SYMMETRY_TYPE, 'integer')
        argSymmetryType.defaultValue = 0
        argSymmetryType.flags = 'optional'
        argSymmetryType.hints = self.SYMMETRY_TYPE_HINTS

        return [argFromSide, argSymmetryType]
    
    def enable(self, msg):
        if not rs.Command.enable(self, msg):
            return False

        result = (len(self._meshes) > 0)
        if not result:
            msg.set(rs.c.MessageTable.DISABLE, "mirrorWeights")
        return result

    def setupMode(self):
        return True

    def restoreSetupMode(self):
        return True

    def execute(self, msg, flags):
        meshes = self._meshes
        if not meshes:
            return

        bindLocs = self._bindLocators
        bindLocatorIds = [bloc.modoItem.id for bloc in bindLocs]

        if bindLocs:
            # When working with bind locators selection:
            # add symmetrical items if they're not in there yet.
            # Symmetry map will not work properly otherwise.
            symItems = []
            for bloc in bindLocs:
                symItem = rs.SymmetryUtils.getSymmetricalItem(bloc, rs.c.ElementSetType.BIND_SKELETON)
                if symItem is None:
                    continue
                # Test if symmetrical item is already on the list.
                if symItem.modoItem.id in bindLocatorIds:
                    continue
                symItems.append(symItem)
            bindLocs += symItems

        ticksPerMesh = 500
        allTicks = ticksPerMesh * len(meshes)
        monitor = modox.Monitor(allTicks, "Mirror Weights")

        self._enableSymmetry()

        for bindMeshItem in meshes:
            editRig = rs.Rig(bindMeshItem.rigRootItem)

            if not bindLocs:
                bindSkeleton = editRig[rs.c.ElementSetType.BIND_SKELETON].elements
            else:
                bindSkeleton = bindLocs

            symmap = rs.SymmetryUtils.buildSymmetryMap(bindSkeleton)

            cmd = '!rs.vertMap.mirror type:weight fromSide:%d mesh:{%s} sourceMap:{%s} targetMap:{%s}'

            sourceMaps = []
            targetMaps = []

            # Get from side argument
            # Arguments with hints come as integers!
            fromSide = self.getArgumentValue(self.ARG_FROM_SIDE)
            if fromSide == 0: # right
                sourceSide = rs.c.Side.RIGHT
                targetSide = rs.c.Side.LEFT
            else:
                sourceSide = rs.c.Side.LEFT
                targetSide = rs.c.Side.RIGHT

            for itemKey in list(symmap[sourceSide].keys()):
                rigItemFrom = symmap[sourceSide][itemKey]
                sourceMap = rigItemFrom.weightMapName
                rigItemTo = symmap[targetSide][itemKey]
                targetMap = rigItemTo.weightMapName

                if not sourceMap or not targetMap:
                    continue

                sourceMaps.append(sourceMap)
                targetMaps.append(targetMap)

            # Mirroring center maps
            for itemKey in list(symmap[rs.c.Side.CENTER].keys()):
                rigItemFrom = symmap[rs.c.Side.CENTER][itemKey]
                sourceMap = rigItemFrom.weightMapName

                if not sourceMap:
                    continue

                sourceMaps.append(sourceMap)

            # Convert maps lists into single string arguments.
            sourceMapArg = ''
            for m in sourceMaps:
                sourceMapArg += m
                sourceMapArg += ';'
            sourceMapArg = sourceMapArg[:-1]

            targetMapArg = ''
            for m in targetMaps:
                targetMapArg += m
                targetMapArg += ';'
            targetMapArg = targetMapArg[:-1]

            lx.eval(cmd % (fromSide, bindMeshItem.modoItem.id, sourceMapArg, targetMapArg))

            monitor.tick(ticksPerMesh)

        # Revert symmetry
        self._restoreSymmetry()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    @property
    def _meshes(self):
        meshes = []
        for mesh in modox.ItemSelection().getRaw():
            try:
                meshes.append(rs.BindMeshItem(mesh))
            except TypeError:
                continue
        return meshes

    @property
    def _bindLocators(self):
        blocs = []
        for item in modox.ItemSelection().getRaw():
            try:
                blocs.append(rs.BindLocatorItem(item))
            except TypeError:
                continue
        return blocs

    def _enableSymmetry(self):
        self._symmetryState = bool(rs.run('symmetry.state ?'))
        self._symmetryAxis = rs.run('symmetry.axis ?') # this will be 0,1,2
        self._symmetryTopo = bool(rs.run('symmetry.topology ?'))

        rs.run('symmetry.state 1')
        rs.run('symmetry.axis 0') # Fixed X axis mirroring

        symType = self.getArgumentValue(self.ARG_SYMMETRY_TYPE)
        if symType == 1: # Topo symmetry
            rs.run('symmetry.topology 1')
        else:
            rs.run('symmetry.topology 0')

    def _restoreSymmetry(self):
        rs.run('symmetry.topology %d' % int(self._symmetryTopo))
        rs.run('symmetry.axis %d' % self._symmetryAxis)
        rs.run('symmetry.state %d' % int(self._symmetryState))

rs.cmd.bless(CmdBindMirrorWeights, 'rs.bind.mirrorWeights')