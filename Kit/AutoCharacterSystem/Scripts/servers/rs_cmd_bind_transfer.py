

import lx
import lxu
import modo
import modox

import rs


class CmdTransferBind(rs.RigCommand):

    ARG_METHOD = 'method'
    ARG_SKIP_UNUSED = 'skipUnused'
    
    METHOD_HINTS = ((0, 'distance'),
                    (1, 'raycast'))
    
    METHOD_INT_TO_STRING_CONSTANT = {0: rs.Bind.TransferMethod.DISTANCE,
                                     1: rs.Bind.TransferMethod.RAYCAST}
    
    
    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        argMethod = rs.command.Argument(self.ARG_METHOD, 'integer')
        argMethod.defaultValue = 0
        argMethod.hints = self.METHOD_HINTS

        argSkipUnused = rs.command.Argument(self.ARG_SKIP_UNUSED, 'boolean')
        argSkipUnused.defaultValue = True
        argSkipUnused.flags = 'optional'
        
        return [argMethod, argSkipUnused] + superArgs

    def enable(self, msg):
        try:
            self._getMeshes()
        except LookupError:
            msg.set(rs.c.MessageTable.DISABLE, "transferBind")
            return False
        return True

    def setupMode(self):
        return True

    def interact(self):
        editRig = self.firstRigToEdit
        if editRig is None:
            return False
        try:
            meshFrom, meshTo = self._getMeshes()
        except LookupError:
            return False
        if not isinstance(meshTo, rs.BindMeshItem):
            meshTo = self._autoAssignBindMesh(meshTo, editRig)
            if meshTo is None:
                return False
        return True

    def execute(self, msg, flags):
        meshFrom, meshTo = self._getMeshes()

        transferMethodInt = self.getArgumentValue(self.ARG_METHOD)
        transferMethod = self.METHOD_INT_TO_STRING_CONSTANT[transferMethodInt]
        skipUnusedDeformers = self.getArgumentValue(self.ARG_SKIP_UNUSED)
        
        ticks = 500
        monitor = modox.Monitor(ticks, "Transfer Bind")
            
        bind = rs.Bind(meshTo.rigRootItem)
        bind.transfer(meshFrom,
                      meshTo,
                      method=transferMethod,
                      skipUnusedDeformers=skipUnusedDeformers,
                      monitor=monitor,
                      ticks=ticks)

        monitor.release()
        rs.Scene().contexts.refreshCurrent()
        meshTo.modoItem.select(replace=True)

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

    def _getMeshes(self):
        """ Gets meshes for the transfer.
        
        Meshes are picked up from current selection.
        First bound and first unboud mesh are taken.
        
        Returns
        -------
        BindMeshItem or modo.Item, BindMeshItem
            meshFrom, meshTo
            meshFrom can be modo.Item if selected mesh is not bind mesh,
            just regular mesh item.
        """
        selectedMeshes = modo.Scene().selectedByType('mesh')
        if not selectedMeshes or len(selectedMeshes) < 2:
            raise LookupError
        
        bindMeshFrom = None
        bindMeshTo = None
        
        standardFromMesh = None
        
        for modoItem in selectedMeshes:
            try:
                bindMesh = rs.BindMeshItem(modoItem)
            except TypeError:
                standardFromMesh = modoItem
                continue
            
            if bindMesh.isBound:
                bindMeshFrom = bindMesh
            else:
                bindMeshTo = bindMesh

            if bindMeshFrom is not None and bindMeshTo is not None:
                break
        
        if bindMeshFrom is None:
            raise LookupError
        if bindMeshTo is None:
            bindMeshTo = standardFromMesh
            
        return bindMeshFrom, bindMeshTo

rs.cmd.bless(CmdTransferBind, 'rs.bind.transfer')