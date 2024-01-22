

import lx
import lxu
import modo
import modox

import rs


class CmdOpenBindMap(rs.RigCommand):
    """ Opens UI for setting bind from existing weights in the mesh.
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
        if not rs.RigCommand.enable(self, msg):
            return False
        
        if self._getMesh() is not None:
            return True
        
        msg.set(rs.c.MessageTable.DISABLE, "newBindFromMap")
        return False

    def interact(self):
        editRig = self.firstRigToEdit
        if editRig is None:
            return False
        mesh = self._getMesh()
        if not mesh:
            return False
        if not isinstance(mesh, rs.BindMeshItem):
            mesh = self._autoAssignBindMesh(mesh, editRig)
            if mesh is None:
                return False
        return True

    def execute(self, msg, flags):
        layoutName = "rs_BindMap"
        cmd = 'layout.createOrClose {rsBindMap} {%s} true {Bind Map} width:960 height:640 style:palette'
        lx.eval(cmd % (layoutName))

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers
    
    # -------- Private methods

    def _autoAssignBindMesh(self, mesh, rig):
        autoAssign = False
        if not autoAssign:
            title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, "assignBeforeBindTitle")
            args = [mesh.name]
            msgText = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, "assignBeforeBind", args)
            result = modo.dialogs.okCancel(title, msgText)
            if result == "cancel":
                return None

        rs.run("!rs.bind.assignMesh mesh:{%s} autoFreeze:1 rootItem:{%s}" % (mesh.id, rig.sceneIdentifier))
        return rs.BindMeshItem(mesh)

    def _getMesh(self):
        """ Gets a mesh that should be edited.
        
        If mesh is not set explicitly we grab selection.
        
        Returns
        -------
        modo.Item. None
            None is returned if no mesh can be found.
        """
        if self.isArgumentSet(self.ARG_MESH):
            meshIdent = self.getArgumentValue(self.ARG_MESH)
            if meshIdent is not None:
                try:
                    return modox.SceneUtils.findItemFast(meshIdent)
                except LookupError:
                    return None
            
        # Try selection
        selected = modo.Scene().selectedByType('mesh')

        standardMesh = None
        
        for meshModoItem in selected:
            try:
                bindMesh = rs.BindMeshItem(meshModoItem)
            except TypeError:
                standardMesh = meshModoItem
                continue
            if not bindMesh.isBound:
                return bindMesh
        
        return standardMesh
    
rs.cmd.bless(CmdOpenBindMap, "rs.bind.openMapUI")