

import os

import lx
import lxu
import modo
import modox

import rs


class CmdRigBake(rs.RigCommand):

    ARG_ACTION = 'action'
    ARG_SUFFIX = 'suffix'
    ARG_BAKE_SCALING = 'flatSkeleton'

    ACTION_HINTS = ((0, 'all'),
                    (1, 'current'),
                    (2, 'none'))

    def init(self):
        self._deleteGuide = False
        self._bakeSceneFilename = self._resolveBakeFilename()

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        action = rs.cmd.Argument(self.ARG_ACTION, 'integer')
        action.hints = self.ACTION_HINTS
        action.defaultValue = 0

        suffix = rs.cmd.Argument(self.ARG_SUFFIX, 'string')
        suffix.defaultValue = '_baked'

        bakeScaling = rs.cmd.Argument(self.ARG_BAKE_SCALING, 'boolean')
        bakeScaling.defaultValue = False

        return [action, suffix, bakeScaling] + superArgs

    def applyEditActionPre(self):
        return True

    def interact(self):
        return self._saveScenePre()

    def execute(self, msg, flags):
        editRigs = self.rigsToEdit
        rigCount = len(editRigs)

        bindSkelBuildTicks = 100.0
        deleteRigTicks = 50.0
        totalTicks = 500 * rigCount

        monitor = modox.Monitor(ticksCount=totalTicks, title="Bake")

        shadowDesc = rs.BakeShadowDescription()
        shadowDesc.supportStretching = self.getArgumentValue(self.ARG_BAKE_SCALING)

        bakeDesc = rs.BakeDescription()
        bakeDesc.actions = self._getActionsChoice()
        bakeDesc.meshes = True

        for editRig in editRigs:
            bindSkelShadow = rs.BindSkeletonShadow(editRig)
            bindSkelShadow.build(shadowDesc,
                                 monitor=monitor,
                                 availableTicks=bindSkelBuildTicks)

            monitor.progress = bindSkelBuildTicks

            bake = rs.BakeOperator(bindSkelShadow)
            bake.bake(bakeDesc, monitor=monitor, monitorTicks=350.0)

            editRig.selfDelete()

            monitor.tick(deleteRigTicks)

        self._saveScenePost()

        monitor.release()

    # -------- Private methods

    def _saveScenePre(self):
        # Can't bake if scene was not saved first.
        if self._bakeSceneFilename is None:
            title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, 'bakeTitle')
            msg = modox.Message.getMessageTextFromTable(rs.c.MessageTable.DISABLE, 'bakeUnsavedScene')
            modo.dialogs.alert(title, msg, 'error')
            return False

        if os.path.isfile(self._bakeSceneFilename):
            title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, 'bakeTitle')
            msg = modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDEXE, 'bakeOverwrite', [self._bakeSceneFilename])
            result = modo.dialogs.okCancel(title, msg)
            if result == 'cancel':
                return False
        return True

    def _saveScenePost(self):
        fileFormat = modo.Scene().FileFormat()
        rs.run('scene.saveAs {%s} {%s} false' % (self._bakeSceneFilename, fileFormat))

    def _resolveBakeFilename(self):
        suffix = self.getArgumentValue(self.ARG_SUFFIX)
        scene = modo.Scene()
        sceneFilename = scene.filename
        if sceneFilename is None:
            return None
        tokens = sceneFilename.rpartition('.')
        return tokens[0] + suffix + tokens[1] + tokens[2]

    def _getActionsChoice(self):
        actionChoiceRaw = self.getArgumentValue(self.ARG_ACTION)
        if actionChoiceRaw == 0: # all actions
            actionChoice = rs.BakeOperator.ActionChoice.ALL
        elif actionChoiceRaw == 1: # current action
            actionChoice = rs.BakeOperator.ActionChoice.CURRENT
        else:
            actionChoice = rs.BakeOperator.ActionChoice.NONE
        return actionChoice

rs.cmd.bless(CmdRigBake, "rs.rig.bake")