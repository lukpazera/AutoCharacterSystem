

import os

import lx
import lxu
import modo

import rs


class CmdRigSave(rs.Command):
    """ Saves edit rig to a preset.
    """

    ARG_FILENAME = 'filename'
    ARG_CAPTURE_THUMB = 'captureThumb'
    
    def init(self):
        self._path = None

    def arguments(self):
        filename = rs.command.Argument(self.ARG_FILENAME, 'string')
        filename.flags = ['optional']
        filename.defaultValue = ''
        
        thumb = rs.command.Argument(self.ARG_CAPTURE_THUMB, 'boolean')
        thumb.flags = ['optional']
        thumb.defaultValue = False
        return [filename, thumb]

    def interact(self):
        if rs.Scene().editRig is None:
            return False

        if self.isArgumentSet(self.ARG_FILENAME):
            return True

        self._path = modo.dialogs.customFile(
            dtype='fileSave',
            title='Save Rig',
            names=('lxp',),
            unames=('ACS Rig',),
            ext=('lxp',))
        if self._path is None:
            return False
        return True

    def setupMode(self):
        return True

    def execute(self, msg, flags):
        captureThumb = self.getArgumentValue(self.ARG_CAPTURE_THUMB)

        # Make sure scene is in neutral state when saving rig.
        rsScene = rs.Scene()
        rsScene.resetContextSceneChanges()
        
        rigToSave = rs.Scene().editRig
        if rigToSave is None:
            return

        if self.isArgumentSet(self.ARG_FILENAME):
            self._path = self.getArgumentValue(self.ARG_FILENAME)
        if self._path is None:
            return

        rigToSave.save(self._path, captureThumb)

        # Reapply current context to get corrent visibility/selectability
        # for rig items again.
        rsScene.refreshContext()

rs.cmd.bless(CmdRigSave, "rs.rig.save")


class CmdRigQuickSave(rs.RigCommand):
    """ Saves rig to a preset without asking for filename.
    """

    ARG_CAPTURE_THUMB = 'captureThumb'
    
    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        thumb = rs.command.Argument(self.ARG_CAPTURE_THUMB, 'boolean')
        thumb.flags = ['optional']
        thumb.defaultValue = False
        return [thumb] + superArgs

    def setupMode(self):
        return True

    def interact(self):
        rigToSave = self.rigToQuery
        if rigToSave is None:
            return False

        fname = self._getSaveFilename(rigToSave)
        if os.path.isfile(fname):
            result = modo.dialogs.okCancel('Save Rig', '%s rig preset is already present and will be overwritten. Continue?' % rigToSave.name)
            if result == 'cancel':
                return False
        return True

    def execute(self, msg, flags):
        captureThumb = self.getArgumentValue(self.ARG_CAPTURE_THUMB)

        # Make sure scene is in neutral state when saving rig.
        rsScene = rs.Scene()
        rsScene.resetContextSceneChanges()
        
        rigToSave = self.rigToQuery
        if rigToSave is None:
            return

        fname = self._getSaveFilename(rigToSave)
        rigToSave.save(fname, captureThumb)

        # Reapply current context to get corrent visibility/selectability
        # for rig items again.
        rsScene.refreshContext()

    # -------- Private methods
    
    def _getSaveFilename(self, rig):
        fname = rig.name + '.lxp'
        return os.path.join(rs.service.path[rs.c.Path.RIGS], fname)
        
rs.cmd.bless(CmdRigQuickSave, "rs.rig.quickSave")