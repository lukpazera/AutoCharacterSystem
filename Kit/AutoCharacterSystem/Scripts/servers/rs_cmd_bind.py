

import lx
import lxu
import modo
import modox

import rs


def testBindMesh(rawItem):
    """ Accept regular meshes and unbound bind meshes only.
    """
    return rawItem.Type() == lx.symbol.i_CIT_MESH


class BindMeshListContent(rs.cmd.ArgumentItemsContent):
    def __init__(self):
        self.noneOption = True
        self.testOnRawItems = True
        self.itemTestFunction = testBindMesh


class CmdBind(rs.RigCommand):
    """ Wrapper for MODO native binding to make it work with ACS.

        This command will perform standard MODO binding, use its results to set up
        RS rig binding and then discard MODO setup.

        deform.bind item:hierarchyRoot mesh:meshItem type:heat falloff:medium segs:true limitWeights:true numWeights:4 minWeight:0.01
    """

    ARG_MESH = 'mesh'
    ARG_TYPE = 'type'
    ARG_SKIP_UNUSED = 'skipUnused'
    ARG_EVALUATION = 'evaluation' # OOO or normalized

    TYPE_HINTS = ((0, 'rigid'),
                  (1, 'smoothD'),
                  (2, 'smoothV'),
                  (3, 'heat'))
    
    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        argType = rs.command.Argument(self.ARG_TYPE, 'integer')
        argType.defaultValue = 1
        argType.hints = self.TYPE_HINTS

        argSkipUnused = rs.command.Argument(self.ARG_SKIP_UNUSED, 'boolean')
        argSkipUnused.defaultValue = True
        argSkipUnused.flags = 'optional'
        
        argEval = rs.command.Argument(self.ARG_EVALUATION, 'string')
        argEval.flags = ['optional', 'hidden']
        argEval.defaultValue = 'norm'

        argMesh = rs.cmd.Argument(self.ARG_MESH, '&item')
        argMesh.flags = ['optional', 'hidden']

        return [argType, argSkipUnused, argEval, argMesh] + superArgs

    def setupMode(self):
        return True

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        
        if self._getMesh() is not None:
            return True
        
        msg.set(rs.c.MessageTable.DISABLE, "newBind")
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
        if not self._testBindSkeletonIntegrity(editRig):
            return False
        return True

    def execute(self, msg, flags):
        editRig = self.firstRigToEdit
        if editRig is None:
            return

        mesh = self._getMesh()
        
        evaluation = self.getArgumentValue(self.ARG_EVALUATION)
        bindType = self.getArgumentValue(self.ARG_TYPE)
        skipUnusedDeformers = self.getArgumentValue(self.ARG_SKIP_UNUSED)

        monitor = modox.Monitor(100, "Normalized Bind")
        
        shadow = rs.BindSkeletonShadow(editRig)
        monitor.tick(1)

        shadow.build(rs.bind_skel_shadow.BindShadowDescription(), monitor=monitor, availableTicks=29)

        monitor.progress = 30
        
        # We run one bind for each skeleton root.
        skeletonRoots = shadow.hierarchyRootModoItems
        for skeletonRoot in skeletonRoots:
            result = self._runBind(skeletonRoot, mesh.modoItem, bindType)

        monitor.tick(30)
        
        modoBind = rs.ModoBind(shadow)
        bind = rs.Bind(editRig)
        bind.setFromModoBind(modoBind, skipUnusedDeformers)
        bind.embedMap(mesh)
        
        monitor.tick(20)
        
        modoBind.delete()
        
        monitor.tick(10)
        
        shadow.delete()
    
        monitor.tick(10)
        monitor.release()

        rs.Scene().contexts.refreshCurrent()
        
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

    def _testBindSkeletonIntegrity(self, rig):
        """
        Tests if bind skeleton is a single hierarchy.
        Bind will most likely not go good if it's not.
        """
        if rs.BindSkeleton(rig).rootLocatorsCount > 1:
            title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, "warnSkeletonBindTitle")
            msgText = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, "warnSkeletonBind")
            result = modo.dialogs.okCancel(title, msgText)
            if result == "cancel":
                return False
        return True

    def _getMesh(self):
        """ Gets a mesh that should be edited.
        
        If mesh is not set explicitly we grab selection.
        
        Returns
        -------
        modo.Item. BindMeshItem, None
            None is returned if no mesh can be found.
            modo.Item is returned if mesh was selected but it's not a bind mesh yet.
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

    def _runBind(self, skeletonRoot, mesh, bindType):
        """ Runs the actual MODO bind command.
        
        Parameters
        ----------
        skeletonRoot : modo.Item
        
        mesh : modo.Item
        
        bindType : str
        """
        try:
            lx.eval('!deform.bind item:{%s} mesh:{%s} type:{%s} falloff:medium segs:true limitWeights:true numWeights:4 minWeight:0.01' % (skeletonRoot.id, mesh.id, bindType))
        except RuntimeError:
            return False
        return True

rs.cmd.bless(CmdBind, 'rs.bind')