

import os

import lx
import lxu
import modo

import rs


class RSCmdModuleSave(rs.base_OnModuleCommand):
    """ Command for saving new rig preset.
    """

    ARG_FILENAME = 'filename'
    ARG_CAPTURE_THUMB = 'captureThumb'

    def init(self):
        self._path = None

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)
        
        filename = rs.command.Argument(self.ARG_FILENAME, 'string')
        filename.flags = ['optional']
        filename.defaultValue = ''

        thumb = rs.command.Argument(self.ARG_CAPTURE_THUMB, "boolean")
        thumb.flags = ['optional']
        thumb.defaultValue = False
        return [filename, thumb] + superArgs

    def flags(self):
        return lx.symbol.fCMD_UNDO | lx.symbol.fCMD_UNDO_AFTER_EXEC

    def setupMode(self):
        return True

    def enable(self, msg):
        module = self.moduleToQuery
        if module is None:
            return False
        # Save is not possible if module has no identifier.
        if not module.identifier:
            return False
        return True

    def interact(self):
        if rs.Scene().editRig is None:
            return False

        if self.isArgumentSet(self.ARG_FILENAME):
            self._path = self.getArgumentValue(self.ARG_FILENAME)
            return True

        self._path = modo.dialogs.customFile(
            dtype='fileSave',
            title='Save Module',
            names=('lxp',),
            unames=('ACS Module',),
            ext=('lxp',))
        if self._path is None:
            return False
        return True

    def execute(self, msg, flags):
        captureThumb = self.getArgumentValue(self.ARG_CAPTURE_THUMB)

        moduleToSave = self.moduleToQuery #_getModuleToSave()
        if moduleToSave is None:
            return

        # Make sure scene is in neutral state when saving module.
        rsScene = rs.Scene()
        rsScene.resetContextSceneChanges()

        if self._path:
            moduleOp = rs.ModuleOperator(moduleToSave.rigRootItem)
            moduleOp.saveModule(moduleToSave, self._path, captureThumb)

        # Reapply current context to get current visibility/selectability
        # for rig items again.
        rsScene.refreshContext()

    def notifiers(self):
        notifiers = rs.base_OnModuleCommand.notifiers(self)

        # For the popup to refresh command needs to react to
        # datatype change when new rig root item is added or removed
        notifiers.append(('item.event', "add[%s] +t" % rs.c.RigItemType.MODULE_ROOT))
        notifiers.append(('item.event', "remove[%s] +t" % rs.c.RigItemType.MODULE_ROOT))

        # React to changes to current Rig graph as well
        # this changes current selection.
        notifiers.append(('graphs.event', '%s +t' % rs.module_op.ModuleOperator.GRAPH_EDIT_MODULE))
        notifiers.append(('graphs.event', '%s +t' % rs.Scene.GRAPH_EDIT_RIG))

        return notifiers

rs.cmd.bless(RSCmdModuleSave, "rs.module.save")


class CmdModuleQuickSave(rs.base_OnModuleCommand):
    """ Saves module to a preset without asking for filename.

    Note that since this is command that backs out its changes to scene
    there's no need to reset context or remove saved variants.
    """

    ARG_CAPTURE_THUMB = 'captureThumb'
    
    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)
        
        thumb = rs.command.Argument(self.ARG_CAPTURE_THUMB, 'boolean')
        thumb.flags = ['optional']
        thumb.defaultValue = False
        return [thumb] + superArgs

    def flags(self):
        return lx.symbol.fCMD_UNDO | lx.symbol.fCMD_UNDO_AFTER_EXEC

    def setupMode(self):
        return True

    def interact(self):
        moduleToSave = self.moduleToQuery
        if moduleToSave is None:
            return False

        fname = self._getSaveFilename(moduleToSave)
        if os.path.isfile(fname):
            result = modo.dialogs.okCancel('Save Module', '%s module preset is already present and will be overwritten. Continue?' % moduleToSave.filename)
            if result == 'cancel':
                return False
        return True

    def execute(self, msg, flags):
        captureThumb = self.getArgumentValue(self.ARG_CAPTURE_THUMB)

        # Make sure scene is in neutral state when saving rig.
        rsScene = rs.Scene()
        rsScene.resetContextSceneChanges()
        
        moduleToSave = self.moduleToQuery
        if moduleToSave is None:
            return

        moduleOp = rs.ModuleOperator(moduleToSave.rigRootItem)
        moduleOp.saveModule(moduleToSave,
                            filename=None,
                            captureThumb=captureThumb)

        # Save variants as well
        featuredModuleOp = rs.FeaturedModuleOperator(moduleToSave.rigRootItem)
        featuredModuleOp.saveVariants(moduleToSave)

    # -------- Private methods
    
    def _getSaveFilename(self, moduleToSave):
        fname = moduleToSave.filename + '.lxp'
        return os.path.join(rs.service.path[rs.c.Path.MODULES], fname)
    
rs.cmd.bless(CmdModuleQuickSave, "rs.module.quickSave")