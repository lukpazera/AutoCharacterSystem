

import lx
import lxu
import modo
import modox

import rs


def testAndConfirmApproveMesh(meshItem):
    """
    For some reason attaching a mesh which scale is less than 3% is breaking attachments.
    """
    scale = modox.LocatorUtils.getItemScale(meshItem, action=lx.symbol.s_ACTIONLAYER_EDIT)
    if scale.x < 0.03 or scale.y < 0.03 or scale.z < 0.03:
        title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, 'attachTitle')
        msg = modox.Message.getMessageTextFromTable(rs.c.MessageTable.DIALOG, 'attachFreezeScale', [meshItem.name])
        result = modo.dialogs.okCancel(title, msg)
        if result == 'cancel':
            return False
    return True


def approveMesh(meshItem):
    scale = modox.LocatorUtils.getItemScale(meshItem, action=lx.symbol.s_ACTIONLAYER_EDIT)
    if scale.x < 0.03 or scale.y < 0.03 or scale.z < 0.03:
        modox.ItemSelection().set(meshItem, selMode=modox.SelectionMode.REPLACE)
        rs.run('transform.freeze scale')


class CmdAttachmentAdd(rs.RigCommand):
    """ Attaches an item to the rig.
    """

    ARG_TYPE = 'type'
    ARG_MESH = 'mesh'
    ARG_ITEM = 'item'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        typeArg = rs.cmd.Argument(self.ARG_TYPE, 'string')
        typeArg.defaultValue = ''

        meshArg = rs.cmd.Argument(self.ARG_MESH, '&item')
        meshArg.flags = 'optional'
        meshArg.defaultValue = None

        itemArg = rs.cmd.Argument(self.ARG_ITEM, '&item')
        itemArg.flags = 'optional'
        itemArg.defaultValue = None

        return [typeArg, meshArg, itemArg] + superArgs

    def setupMode(self):
        return True

    def restoreItemSelection(self):
        return True
    
    def enable(self, msg):
        return len(self._getMeshes()) > 0 and self._getItem() is not None

    def interact(self):
        for mesh in self._getMeshes():
            if not testAndConfirmApproveMesh(mesh):
                return False
        return True

    def execute(self, msg, flags):
        attachType = self.getArgumentValue(self.ARG_TYPE)
        if not attachType:
            return 

        meshes = self._getMeshes()
        if meshes is None:
            return

        item = self._getItem()
        if item is None:
            return

        editRig  = self.firstRigToEdit
        if editRig is None:
            return
            
        attach = rs.Attachments(editRig)
        for mesh in meshes:
            approveMesh(mesh)
            attach.attachItem(mesh, item, attachType)
        
        rs.Scene().contexts.refreshCurrent()

    # -------- Private methods
        
    def _getMeshes(self):
        scene = modo.Scene()
        meshIdent = self.getArgumentValue(self.ARG_MESH)
        
        if meshIdent:
            meshItem = scene.item(meshIdent)
            return [meshItem]
        
        selected = []
        for item in scene.selected:
            if item.type in ['mesh', 'meshInst']:
                selected.append(item)
        
        return selected

    def _getItem(self):
        scene = modo.Scene()
        itemIdent = self.getArgumentValue(self.ARG_ITEM)
        
        if itemIdent:
            item = scene.item(itemIdent)
            return item
        
        selected = scene.selected
        if not selected or len(selected) < 1:
            return None
        
        for item in selected:
            try:
                bindLoc = rs.BindLocatorItem(item)
            except TypeError:
                continue
            return item

        return None

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

rs.cmd.bless(CmdAttachmentAdd, 'rs.attach.add')


class CmdAttachmentAutoAdd(rs.RigCommand):
    """ Attaches an item to the rig.
    """

    ARG_TYPE = 'type'
    ARG_MESH = 'mesh'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        typeArg = rs.cmd.Argument(self.ARG_TYPE, 'string')
        typeArg.defaultValue = ''

        meshArg = rs.cmd.Argument(self.ARG_MESH, '&item')
        meshArg.flags = 'optional'
        meshArg.defaultValue = None

        return [typeArg, meshArg] + superArgs

    def setupMode(self):
        return True

    def restoreItemSelection(self):
        return True

    def enable(self, msg):
        return len(self._getMeshes()) > 0

    def interact(self):
        for mesh in self._getMeshes():
            if not testAndConfirmApproveMesh(mesh):
                return False
        return True

    def execute(self, msg, flags):
        attachType = self.getArgumentValue(self.ARG_TYPE)
        if not attachType:
            return

        meshes = self._getMeshes()
        if meshes is None:
            return

        editRig = self.firstRigToEdit
        if editRig is None:
            return

        bindSkeleton = rs.BindSkeleton(editRig)
        attach = rs.Attachments(editRig)
        for mesh in meshes:
            if mesh.type == 'mesh':
                approveMesh(mesh)
                centerTuple = mesh.geometry.getMeshCenter()
                centerPoint = modo.Vector3(centerTuple)
                worldXfrmMtx = modox.LocatorUtils.getItemWorldTransform(mesh)
                centerPoint.mulByMatrixAsPoint(worldXfrmMtx)
            else:
                centerTuple = modox.LocatorUtils.getItemWorldPosition(mesh)
                centerPoint = modo.Vector3(centerTuple)

            closestBindLocator = bindSkeleton.getJointClosestToPoint(centerPoint, ignoreHidden=True)
            attach.attachItem(mesh, closestBindLocator.modoItem, attachType)

        rs.Scene().contexts.refreshCurrent()

    # -------- Private methods

    def _getMeshes(self):
        scene = modo.Scene()
        meshIdent = self.getArgumentValue(self.ARG_MESH)

        if meshIdent:
            meshItem = scene.item(meshIdent)
            return [meshItem]

        selected = []
        for item in scene.selected:
            if item.type in ['mesh', 'meshInst']:
                selected.append(item)

        return selected

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

rs.cmd.bless(CmdAttachmentAutoAdd, 'rs.attach.addAuto')


class CmdAttachmentRemove(rs.RigCommand):
    """ Detaches an item from the rig.
    """

    ARG_MESH = 'mesh'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        meshArg = rs.cmd.Argument(self.ARG_MESH, '&item')
        meshArg.flags = 'optional'
        meshArg.defaultValue = None

        return [meshArg] + superArgs

    def setupMode(self):
        return True

    def restoreItemSelection(self):
        return True

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        return len(self._getMeshes()) > 0

    def execute(self, msg, flags):
        meshes = self._getMeshes()
        if meshes is None:
            return

        editRig = self.firstRigToEdit
        attach = rs.Attachments(editRig)
        for mesh in meshes:
            attach.detachItem(mesh)
            
        rs.Scene().refreshContext()

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getMeshes(self):
        scene = modo.Scene()
        meshIdent = self.getArgumentValue(self.ARG_MESH)
        
        if meshIdent:
            meshItem = scene.item(meshIdent)
            return [meshItem]
        
        selected = []
        for item in scene.selected:
            if item.type in ['mesh', 'meshInst']:
                selected.append(item)
        
        return selected

rs.cmd.bless(CmdAttachmentRemove, "rs.attach.remove")


class CmdEditResolutionAttachments(rs.RigCommand):
    """ Edits all attachments of given type within given or current resolution.

    Edit options are:
    select
    delete
    """

    ARG_TYPE = 'type'
    ARG_ACTION = 'action'
    ARG_RESOLUTION = 'resolution'

    ACTION_HINTS = ((0, 'select'),
                    (1, 'delete'))

    def arguments(self):
        argType = rs.cmd.Argument(self.ARG_TYPE, 'string')

        argAction = rs.cmd.Argument(self.ARG_ACTION, 'integer')
        argAction.hints = self.ACTION_HINTS
        argAction.defaultValue = 0
        argAction.flags = 'optional'

        argResolution = rs.cmd.Argument(self.ARG_RESOLUTION, 'string')
        argResolution.defaultValue = ''
        argResolution.flags = 'optional'

        return [argType, argAction, argResolution] + rs.RigCommand.arguments(self)

    def execute(self, msg, flags):
        editRig = self.firstRigToEdit
        res = rs.Resolutions(editRig.rootItem)

        attachType = self.getArgumentValue(self.ARG_TYPE)

        if self.isArgumentSet(self.ARG_RESOLUTION):
            resolutionName = self.getArgumentValue(self.ARG_RESOLUTION)
        else:
            resolutionName = res.currentResolution
        if not resolutionName:
            return

        attachments = rs.Attachments(editRig)
        allProxies = attachments.getAttachmentsOfType(attachType)
        proxiesToManage = []
        for proxyRigItem in allProxies:
            if proxyRigItem.isInResolution(resolutionName):
                proxiesToManage.append(proxyRigItem)

        modoItems = [proxy.modoItem for proxy in proxiesToManage]
        scene = modo.Scene()
        action = self.getArgumentValue(self.ARG_ACTION)

        if action == 0:  # Select
            scene.select(modoItems, add=False)
        elif action == 1:  # Delete
            for modoItem in modoItems:
                attachments.detachItem(modoItem)
                scene.removeItems(modoItem, children=False)

lx.bless(CmdEditResolutionAttachments, 'rs.bind.editResolutionAttachments')