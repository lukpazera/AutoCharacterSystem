
import os.path

import lx
import modo
import modox

import rs


class CmdRigSnapshot(rs.RigCommand):
    """ Takes a snaphot of the rig in current resolution at current frame.
    """

    def setupMode(self):
        return False

    def execute(self, msg, flags):
        scene = rs.Scene()

        snapshotMesh = None
        for rig in scene.selectedRigs:
            snapshotMesh = self._takeSnapshot(rig)

        rs.run('!select.type item')
        if snapshotMesh:
            modox.ItemSelection().set(snapshotMesh, modox.SelectionMode.REPLACE)
            rs.run('mesh.patchSubdiv 1')
            rs.run('mesh.psubSubdiv 1')

    # -------- Private methods

    def _takeSnapshot(self, rig):
        meshes = []
        meshes.extend(rig[rs.c.ElementSetType.RESOLUTION_BIND_MESHES].elements)
        meshes.extend(rig[rs.c.ElementSetType.RESOLUTION_BIND_PROXIES].elements)
        meshes.extend(rig[rs.c.ElementSetType.RESOLUTION_RIGID_MESHES].elements)

        snapshotMesh = self._createSnapshotMesh(rig)

        itemSelection = modox.ItemSelection()

        for mesh in meshes:
            itemSelection.set(mesh, modox.SelectionMode.REPLACE)

            # Copy / Paste geo
            rs.run('select.type polygon')
            rs.run('select.drop polygon')
            rs.run('copy')

            itemSelection.set(snapshotMesh, modox.SelectionMode.REPLACE)
            rs.run('select.type polygon')
            rs.run('paste')
            rs.run('select.drop polygon')

        return snapshotMesh

    def _createSnapshotMesh(self, rig):
        actor = rig.actor
        currentAction = actor.currentAction
        if currentAction is not None:
            actionName = currentAction.name
            actionName = '_' + actionName.replace(' ', '_') + '_'
        else:
            actionName = '_'

        selectionService = lx.service.Selection()
        valueService = lx.service.Value()
        startFrame, endFrame = modox.TimeUtils.getSceneFrameRange(modox.TimeUtils.FrameRange.SCENE)
        digits = len(str(int(endFrame)))

        frameNumber = int(valueService.TimeToFrame(selectionService.GetTime()))
        frameNString = str(frameNumber).zfill(digits)
        meshName = '%s%s%s' % (rig.name, actionName, frameNString)

        meshItem = modo.Scene().addMesh(meshName)
        return meshItem

rs.cmd.bless(CmdRigSnapshot, 'rs.rig.snapshot')