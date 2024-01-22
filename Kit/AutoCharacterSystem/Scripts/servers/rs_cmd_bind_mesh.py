

import lx
import lxu
import modo
import modox

import rs


class CmdAssignBindMesh(rs.RigCommand):
    """ Assigns bind meshes to the rig.
    """

    ARG_MESH = 'mesh'
    ARG_AUTOFREEZE = 'autoFreeze'
    
    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        autoFreezeArg = rs.cmd.Argument(self.ARG_AUTOFREEZE, 'boolean')
        autoFreezeArg.flags = 'optional'
        autoFreezeArg.defaultValue = False

        meshArg = rs.cmd.Argument(self.ARG_MESH, '&item')
        meshArg.flags = ['optional', 'hidden']
        meshArg.defaultValue = None

        return [autoFreezeArg, meshArg] + superArgs

    def restoreItemSelection(self):
        return True

    def autoFocusItemListWhenDone(self):
        return True

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        if len(self._getMeshes()) > 0:
            return True

        rigName = self.firstRigToEdit.name
        msg.set(rs.c.MessageTable.DISABLE, "assignBind", [rigName])
        return False
    
    def execute(self, msg, flags):
        meshes = self._getMeshes()
        if not meshes:
            return

        editRig = self.firstRigToEdit
        if editRig is None:
            return
        
        if not self._freezeMeshesWithTransforms(meshes):
            return
        
        try:
            bindMeshes = rs.BindMeshes(editRig.rootModoItem)
        except TypeError:
            return

        bindMeshes.assign(meshes)

        # Notify UI.
        # TODO: This is excessive, need to optimise later.
        rs.service.notify(rs.c.Notifier.UI_GENERAL, rs.c.Notify.DATATYPE)

        # Reset the context
        rsScene = rs.Scene()
        rsScene.contexts.refreshCurrent()

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods
    
    def _freezeMeshesWithTransforms(self, meshes):
        meshesToFreeze = self._testWorldTransforms(meshes)
        if meshesToFreeze:
            if not self.getArgumentValue(self.ARG_AUTOFREEZE):
                if len(meshesToFreeze) > 1:
                    msgKey = "assignBindFreezeN" 
                    args = []
                else:
                    msgKey = "assignBindFreeze1"
                    args = [meshesToFreeze[0].name]
                title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, "assignBindTitle")
                msgText = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, msgKey, args)
                result = modo.dialogs.okCancel(title, msgText)
                if result == "cancel":
                    return False

            modo.Scene().select(meshesToFreeze, add=False)
            rs.run("!transform.freeze all")
        return True

    def _testWorldTransforms(self, meshModoItems):
        """ Tests whether meshes have world transforms already.
        """
        meshesToFreeze = []
        for modoItem in meshModoItems:
            if modox.LocatorUtils.hasWorldTransform(modoItem):
                meshesToFreeze.append(modoItem)
        return meshesToFreeze
        
    def _getMeshes(self):
        scene = modo.Scene()
        if self.isArgumentSet(self.ARG_MESH):
            meshIdent = self.getArgumentValue(self.ARG_MESH)
            
            if meshIdent:
                try:
                    return [scene.item(meshIdent)]
                except LookupError:
                    return []
        
        selected = scene.selectedByType('mesh')
        if not selected:
            return []
        
        meshes = []
        for modoItem in selected:
            # The mesh cannot be in a rig already
            if rs.RigComponentSetup.isModoItemInSetup(modoItem):
                continue
            if rs.Item.isRigItem(modoItem):
                continue
            meshes.append(modoItem)
        return meshes

rs.cmd.bless(CmdAssignBindMesh, "rs.bind.assignMesh")


class CmdUnassignBindMesh(rs.RigCommand):
    """ Unassigns bind meshes from the rig.
    """

    ARG_AUTO_UNBIND = 'autoUnbind'
    ARG_MESH = 'mesh'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        autoUnbind = rs.cmd.Argument(self.ARG_AUTO_UNBIND, 'boolean')
        autoUnbind.flags = 'optional'
        autoUnbind.defaultValue = False
        
        meshArg = rs.cmd.Argument(self.ARG_MESH, '&item')
        meshArg.flags = ['optional', 'hidden']
        meshArg.defaultValue = None

        return [autoUnbind, meshArg] + superArgs

    def restoreItemSelection(self):
        return True

    def autoFocusItemListWhenDone(self):
        return True

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        if len(self._getMeshes()) > 0:
            return True

        msg.set(rs.c.MessageTable.DISABLE, "unassignBind")
        return False
    
    def execute(self, msg, flags):
        bmeshes = self._getMeshes()
        if not bmeshes:
            return

        # Bail out if user decided not to unbind bound meshes first.
        if not self._unbindBoundMeshes(bmeshes):
            return
        
        # We shouldn't need to instance bind meshes operator for each bind mesh
        # as all bind meshes should be coming from the same rig but we do it just to be sure
        # so we always unassign the mesh for the rig that it was assigned to.
        for bindMesh in bmeshes:
            try:
                bindMeshes = rs.BindMeshes(bindMesh.rigRootItem)
            except TypeError:
                continue
            bindMeshes.unassign(bindMesh)

        # Notify UI.
        # TODO: This is excessive, need to optimise later.
        rs.service.notify(rs.c.Notifier.UI_GENERAL, rs.c.Notify.DATATYPE)

        # Reset the context
        rsScene = rs.Scene()
        rsScene.contexts.refreshCurrent()

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _unbindBoundMeshes(self, bmeshList):
        """ Handles automatically unbinding any bound bind meshes.
        
        Returns
        -------
        bool
            False if user aborted automatic unbinding.
        """
        boundMeshes = self._testForBoundMeshes(bmeshList)
        if boundMeshes:
            if not self.getArgumentValue(self.ARG_AUTO_UNBIND):
                if len(boundMeshes) > 1:
                    msgKey = "unassignBindUnbindN" 
                    args = []
                else:
                    msgKey = "unassignBindUnbind1"
                    args = [boundMeshes[0].modoItem.name]
                title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, "unassignBindTitle")
                msgText = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, msgKey, args)
                result = modo.dialogs.okCancel(title, msgText)
                if result == "cancel":
                    return False

            for bmesh in boundMeshes:
                rs.run("rs.unbind mesh:{%s}" % bmesh.modoItem.id)
        return True
        
    def _testForBoundMeshes(self, bmeshList):
        """ Tests if any of the given bind meshes is bound.
        
        Returns
        -------
        the list of bound meshes.
        """
        boundMeshes = []
        for bmesh in bmeshList:
            if bmesh.isBound:
                boundMeshes.append(bmesh)
        return boundMeshes

    def _getMeshes(self):
        """
        
        Returns
        -------
        list of BindMeshItem
        """
        scene = modo.Scene()
        if self.isArgumentSet(self.ARG_MESH):
            meshIdent = self.getArgumentValue(self.ARG_MESH)
            
            if meshIdent:
                try:
                    return [scene.item(meshIdent)]
                except LookupError:
                    return []
        
        selected = scene.selectedByType('mesh')
        if not selected:
            return []
        
        editRigRootItem = rs.Scene.getEditRigRootItemFast()
        bmeshes = []
        for modoItem in selected:
            try:
                bmesh = rs.BindMeshItem(modoItem)
            except TypeError:
                continue
            if bmesh.rigRootItem == editRigRootItem:
                bmeshes.append(bmesh)
        return bmeshes

rs.cmd.bless(CmdUnassignBindMesh, "rs.bind.unassignMesh")


