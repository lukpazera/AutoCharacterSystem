

import time

import lx
import lxu
import modo
import modox

import rs


class CmdUnbind(rs.RigCommand):
    """ Unbinds the mesh from the rig.
    """
    
    ARG_BACKUP_WEIGHTS = 'bkpWeights'
    ARG_BINDMAP = 'bindMap'
    ARG_MESH = 'mesh'
    
    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
    
        argBkpWeights = rs.cmd.Argument(self.ARG_BACKUP_WEIGHTS, 'boolean')
        argBkpWeights.defaultValue = True

        argBindMap = rs.cmd.Argument(self.ARG_BINDMAP, 'boolean')
        argBindMap.defaultValue = True
        
        argMesh = rs.cmd.Argument(self.ARG_MESH, '&item')
        argMesh.flags = ['optional', 'hidden']
        argMesh.defaultValue = None

        return [argBkpWeights, argBindMap, argMesh] + superArgs

    def setupMode(self):
        return True

    def enable(self, msg):
        if len(self._getMeshes()) > 0:
            return True
        msg.set(rs.c.MessageTable.DISABLE, "unbind")
        return False

    def execute(self, msg, flags):
        backupWeights = self.getArgumentValue(self.ARG_BACKUP_WEIGHTS)
        embedBindMap = self.getArgumentValue(self.ARG_BINDMAP)
        meshesToUnbind = self._getMeshes()

        for bmesh in meshesToUnbind:
            if not embedBindMap:
                bmesh.bindMap.clear()
            rig = rs.Rig(bmesh.rigRootItem)
            bind = rs.Bind(rig)
            bind.unbind(bmesh, backupWeights=backupWeights)

        rs.Scene().contexts.refreshCurrent()
        
    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getMeshes(self):
        """ Gets meshes to unbind.

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

rs.cmd.bless(CmdUnbind, 'rs.unbind')