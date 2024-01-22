

import lx
import lxu
import modo
import modox

import rs


class CmdBindProxyAutoSetup(rs.Command):

    ARG_NAME = 'name'
    ARG_SUBDIVIDE = 'subdivide'
    ARG_DOUBLE_SIDED = 'doubleSided'
    ARG_RESTORE_REGIONS = 'restoreRegions'

    def arguments(self):
        nameArg = rs.cmd.Argument(self.ARG_NAME, 'string')
        nameArg.defaultValue = 'Proxy'
        
        subdivideArg = rs.cmd.Argument(self.ARG_SUBDIVIDE, 'boolean')
        subdivideArg.flags = 'optional'
        subdivideArg.defaultValue = False

        doubleSidedArg = rs.cmd.Argument(self.ARG_DOUBLE_SIDED, 'boolean')
        doubleSidedArg.flags = 'optional'
        doubleSidedArg.defaultValue = True

        regionsArg = rs.cmd.Argument(self.ARG_RESTORE_REGIONS, 'boolean')
        regionsArg.flags = 'optional'
        regionsArg.defaultValue = True

        return [nameArg, subdivideArg, doubleSidedArg, regionsArg]

    def uiHints(self, argument, hints):
        if argument == self.ARG_SUBDIVIDE or argument == self.ARG_DOUBLE_SIDED or argument == self.ARG_RESTORE_REGIONS:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def execute(self, msg, flags):
        """ Main command execution code.
        
        Note that I'm using commands for setting and clearing vertex map selection.
        This is because using vertex map selection class from modox is somehow
        getting MODO in a bad state and eventually causing crash.
        """
        scene = modo.Scene()
        resolutionName = self.getArgumentValue(self.ARG_NAME)

        rscene = rs.Scene()
        editRig = rscene.editRig
        if editRig is None:
            return

        meshes = editRig[rs.c.ElementSetType.RESOLUTION_BIND_MESHES].elements
        if not meshes:
            return

        subdivide = self.getArgumentValue(self.ARG_SUBDIVIDE)
        doubleSided = self.getArgumentValue(self.ARG_DOUBLE_SIDED)
        
        attachments = rs.Attachments(editRig)
        resolutions = rs.Resolutions(editRig.rootItem)
        resolutions.addResolution(resolutionName)
        bindSkeleton = rs.BindSkeleton(editRig)

        bindlocsByMap = {}

        for bindloc in bindSkeleton.items:
            mapName = bindloc.weightMapName
            if mapName is not None:
                bindlocsByMap[mapName] = bindloc

        # Monitor
        perMeshMonitorTicks = 1000
        proxyCommandTicks = 500
        restoreRegionsTicks = 200
        totalMonitorTicks = len(meshes) * perMeshMonitorTicks + restoreRegionsTicks
        monitor = modox.Monitor(totalMonitorTicks, 'Bind Proxies Automatic Setup')
        countMeshes = 0

        for mesh in meshes:
            scene.select(mesh, add=False)

            # Selected weight map first.
            # We have to select weights for each mesh separately.
            # This is because we do not want to select maps that are not on a given mesh.
            # If map does not exist on a mesh the command will throw RuntimeError.
            lx.eval('!select.vertexMap {} wght remove')
            for mapName in bindlocsByMap:
                try:
                    lx.eval('!select.vertexMap {%s} wght add' % mapName)
                except RuntimeError:
                    pass

            rs.run('!rs.mesh.partitionByWeights item:%s subdivide:%d doubleSided:%d' % (mesh.id, int(subdivide), int(doubleSided)))

            proxyItems = scene.selected

            # If mesh is empty there will be no proxy items created.
            if len(proxyItems) == 0:
                monitor.tick(perMeshMonitorTicks)
                continue

            # Make sure to set proxies to 1 level for subdiv display
            rs.run('mesh.patchSubdiv 1')
            rs.run('mesh.psubSubdiv 1')

            monitor.tick(proxyCommandTicks)
            perProxyMeshTick = float(perMeshMonitorTicks - proxyCommandTicks) / float(len(proxyItems))

            for proxyMesh in proxyItems:
                monitor.tick(perProxyMeshTick)

                # Proxy items will have name created from 3 parts separated by '-':
                # meshName-weightmapName-proxySuffix
                # We need to extract weight map name out of that and also reassemble the name.
                # This could potentially use naming scheme?
                nameParts = proxyMesh.name.split('-')
                key = nameParts[1] # this is weight map name
                proxyMesh.name = mesh.name + ' ' + nameParts[1] + ' (Proxy)' # rerender the name
                try:
                    bindloc = bindlocsByMap[key]
                except KeyError:
                    continue
                proxyRigItem = attachments.attachItem(proxyMesh, bindloc.modoItem, rs.c.ComponentType.BIND_PROXIES)
                proxyRigItem.addToResolution(resolutionName)

            # Make sure monitor reaches required progress state.
            countMeshes += 1
            monitor.progress = countMeshes * perMeshMonitorTicks

        rs.run('!select.vertexMap {} wght remove')
        scene.deselect(None)
        rs.run('!select.type item')

        # Restore command regions from selection sets if user requested it.
        # At this point selection is dropped so the command should automatically apply
        # to all meshes in the Proxy resolution.
        if self.getArgumentValue(self.ARG_RESTORE_REGIONS):
            rs.run('rs.rig.clayAutoSetup method:selsets addSelectionSets:0')
        monitor.tick(restoreRegionsTicks)

        rscene.contexts.refreshCurrent()
        
        monitor.release()

    @property
    def _mesh(self):
        for mesh in modo.Scene().selectedByType('mesh'):
            return mesh
        return None

rs.cmd.bless(CmdBindProxyAutoSetup, 'rs.bind.proxyAutoSetup')
