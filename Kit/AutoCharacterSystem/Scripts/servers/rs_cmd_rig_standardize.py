

import os.path

import modo
import modox.message

import rs


class CmdRigStandardize(rs.RigCommand):
    """ Convert rig to all vanilla modo items.
    """

    ARG_SUFFIX = 'suffix'
    ARG_DELETE_GUIDE = 'delGuide'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        suffix = rs.cmd.Argument(self.ARG_SUFFIX, 'string')
        suffix.defaultValue = '_std'

        delGuide = rs.cmd.Argument(self.ARG_DELETE_GUIDE, 'boolean')
        delGuide.defaultValue = True
        delGuide.flags = ['optional']

        return [suffix, delGuide] + superArgs

    def applyEditActionPre(self):
        return True

    def applyEditActionPost(self):
        return True

    def setupMode(self):
        return True

    def restoreSetupMode(self):
        return True

    def interact(self):
        scene = modo.Scene()
        filename = scene.filename
        if not filename:
            self.message.set(rs.c.MessageTable.CMDEXE, "stdNoFilename")
            return False
        return True

    def execute(self, msg, flags):
        rigsToEdit = self.rigsToEdit
        if not rigsToEdit:
            return

        deleteGuide = self.getArgumentValue(self.ARG_DELETE_GUIDE)

        scene = rs.Scene()
        contextBkp = scene.contexts.current

        scene.contexts.current = rs.c.Context.ANIMATE
        for rig in rigsToEdit:
            if deleteGuide:
                rs.Guide(rig).selfDelete()
            scene.standardizeRig(rig)
        scene.resetEditRig()
        modo.Scene().select(None)
        scene.contexts.current = contextBkp

        self._saveSceneCopy()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers

    def restoreItemSelection(self):
        """ Standardize should NOT restore selection in normal manner.
        
        Standardize changes item types and if an item was selected that
        was changed to different type trying to restore non-existent item
        will crash.
        """
        return False

    # -------- Private methods

    def _saveSceneCopy(self):
        scene = modo.Scene()
        filename, ext = os.path.splitext(scene.filename)
        filename += self.getArgumentValue(self.ARG_SUFFIX)
        filename += ext

        fileFormat = scene.FileFormat()
        rs.run('scene.saveAs {%s} {%s} false' % (filename, fileFormat))

rs.cmd.bless(CmdRigStandardize, 'rs.rig.standardize')