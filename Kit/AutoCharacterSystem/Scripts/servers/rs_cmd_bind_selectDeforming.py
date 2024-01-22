

import lx
import lxu
import modo
import modox

import rs


class CmdSelectDeformingEffectors(rs.RigCommand):
    """ Selects bind locators(effectors) that deform given mesh.
    """
    
    ARG_MESH = 'mesh'
    
    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        argMesh = rs.cmd.Argument(self.ARG_MESH, '&item')
        argMesh.flags = ['optional', 'hidden']
        argMesh.defaultValue = None

        return [argMesh] + superArgs

    def enable(self, msg):
        if self._getMesh() is not None:
            return True
        msg.set(rs.c.MessageTable.DISABLE, "selEffectors")
        return False

    def execute(self, msg, flags):
        bindMesh = self._getMesh()
        if bindMesh is None:
            return
        
        effs = bindMesh.effectorsModoItems
        if not effs:
            return
        
        modo.Scene().select(effs)
        
    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getMesh(self):
        """ Gets mesh to select effectors for.
        
        The mesh has to be either set via argument or selected.
        
        Returns
        -------
        BindMeshItem, None
        """        
        if self.isArgumentSet(self.ARG_MESH):
            meshIdent = self.getArgumentValue(self.ARG_MESH)
            try:
                mesh = modox.SceneUtils.findItemFast(meshIdent)
            except LookupError:
                return None
            else:
                try:
                    bindMesh = rs.BindMeshItem(mesh)
                except TypeError:
                    return None
                if bindMesh.isBound:
                    return bindMesh
                else:
                    return None

        # Try selection
        selected = modo.Scene().selectedByType('mesh')
        for modoItem in selected:
            try:
                bindMesh = rs.BindMeshItem(modoItem)
            except TypeError:
                return None
            if bindMesh.isBound:
                return bindMesh
        
        return None

rs.cmd.bless(CmdSelectDeformingEffectors, 'rs.bind.selectDeforming')