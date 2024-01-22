

from . import game_export as ex


class UnrealExportAllSingleCommand(ex.ExportAllSingleCommand):

    fbxPresetName = 'Rig Unreal Skeletal Mesh With Actions'


class UnrealExportAllSeparateCommand(ex.ExportAllSeparateCommand):

    skeletalFbxPresetName = 'Rig Unreal Skeletal Mesh'
    actionFbxPresetName = 'Rig Unreal Action'

    def getFbxActionName(self, actionName):
        return actionName


class UnrealExportSkeletalMeshCommand(ex.ExportSkeletalMeshCommand):

    fbxPresetName = 'Rig Unreal Skeletal Mesh'


class UnrealExportCurrentActionCommand(ex.ExportCurrentActionCommand):

    fbxPresetName = 'Rig Unreal Action'

    @property
    def fbxFilename(self):
        return self.bakedActor.currentAction.name


class UnrealExportAllActionsCommand(ex.ExportAllActionsCommand):

    fbxPresetName = 'Rig Unreal Action'

    def getFbxActionName(self, actionName):
        return actionName


class UnrealExportSet(ex.GameExportSet):

    descIdentifier = 'unreal'
    descUsername = 'Unreal'

    descExportCommands = {ex.GameExportSet.CommandId.ALL_SINGLE_FILE: UnrealExportAllSingleCommand,
                          ex.GameExportSet.CommandId.ALL_MULTIPLE_FILES: UnrealExportAllSeparateCommand,
                          ex.GameExportSet.CommandId.SKELETAL_MESH: UnrealExportSkeletalMeshCommand,
                          ex.GameExportSet.CommandId.CURRENT_ACTION: UnrealExportCurrentActionCommand,
                          ex.GameExportSet.CommandId.ALL_ACTIONS: UnrealExportAllActionsCommand}
