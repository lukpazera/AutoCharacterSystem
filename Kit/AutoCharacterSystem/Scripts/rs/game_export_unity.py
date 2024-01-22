

from . import game_export as ex


class UnityExportAllSingleCommand(ex.ExportAllSingleCommand):

    fbxPresetName = 'Rig Unity Skeletal Mesh With Actions'


class UnityExportAllSeparateCommand(ex.ExportAllSeparateCommand):

    skeletalFbxPresetName = 'Rig Unity Skeletal Mesh'
    actionFbxPresetName = 'Rig Unity Action'

    def getFbxActionName(self, actionName):
        return self.rig.name + "@" + actionName


class UnityExportSkeletalMeshCommand(ex.ExportSkeletalMeshCommand):

    fbxPresetName = 'Rig Unity Skeletal Mesh'


class UnityExportCurrentActionCommand(ex.ExportCurrentActionCommand):

    fbxPresetName = 'Rig Unity Action'

    @property
    def fbxFilename(self):
        return self.rig.name + "@" + self.bakedActor.currentAction.name


class UnityExportAllActionsCommand(ex.ExportAllActionsCommand):

    fbxPresetName = 'Rig Unity Action'

    def getFbxActionName(self, actionName):
        return self.rig.name + "@" + actionName


class UnityExportSet(ex.GameExportSet):

    descIdentifier = 'unity'
    descUsername = 'Unity'

    descExportCommands = {ex.GameExportSet.CommandId.ALL_SINGLE_FILE: UnityExportAllSingleCommand,
                          ex.GameExportSet.CommandId.ALL_MULTIPLE_FILES: UnityExportAllSeparateCommand,
                          ex.GameExportSet.CommandId.SKELETAL_MESH: UnityExportSkeletalMeshCommand,
                          ex.GameExportSet.CommandId.CURRENT_ACTION: UnityExportCurrentActionCommand,
                          ex.GameExportSet.CommandId.ALL_ACTIONS: UnityExportAllActionsCommand}
