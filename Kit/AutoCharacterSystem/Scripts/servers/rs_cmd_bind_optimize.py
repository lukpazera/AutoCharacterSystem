
import time

import lx
import lxu
import modo
import modox

import rs


class CmdOptimizeDeformers(rs.RigCommand):
    """ Disconnects deformers that have no influence over the mesh(es).
    """

    ARG_MESH = 'mesh'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argMesh = rs.cmd.Argument(self.ARG_MESH, '&item')
        argMesh.flags = ['optional', 'hidden']
        argMesh.defaultValue = None

        return [argMesh] + superArgs

    def setupMode(self):
        return True

    def enable(self, msg):
        if len(self._getMeshes()) > 0:
            return True
        msg.set(rs.c.MessageTable.DISABLE, "unbind")
        return False

    def execute(self, msg, flags):
        meshesToOptimize = self._getMeshes()

        disconnectedCount = 0
        for bmesh in meshesToOptimize:
            disconnectedCount += rs.Bind(bmesh.rigRootItem).disconnectDeformersWithNoInfluence(bmesh)

        if disconnectedCount > 1:
            modo.dialogs.alert("Optimize Bind", "%d deformers were disconnected." % disconnectedCount, 'info')
        elif disconnectedCount == 1:
            modo.dialogs.alert("Optimize Bind", "1 deformer was disconnected.", 'info')
        else:
            modo.dialogs.alert("Optimize Bind", "No deformers were disconnected.", 'info')

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getMeshes(self):
        """ Gets meshes to optimize.

        Returns
        -------
        list of BindMeshItem
            Empty list is returned if not meshes to unbind.
        """
        # Check argument first
        meshes = []

        if self.isArgumentSet(self.ARG_MESH):
            meshIdent = self.getArgumentValue(self.ARG_MESH)
            try:
                meshes = [modox.SceneUtils.findItemFast(meshIdent)]
            except LookupError:
                return []

        # Try selection
        if not meshes:
            meshes = modo.Scene().selectedByType('mesh')

        if not meshes:
            return []

        unbindMeshes = []

        for meshModoItem in meshes:
            try:
                bindMesh = rs.BindMeshItem(meshModoItem)
            except TypeError:
                continue
            if bindMesh.isBound:
                unbindMeshes.append(bindMesh)

        return unbindMeshes

rs.cmd.bless(CmdOptimizeDeformers, 'rs.bind.optimize')