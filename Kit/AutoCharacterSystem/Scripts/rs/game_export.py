""" Export character to game engines via fbx.
"""

import os
import shutil

import lx
import modo
import modox

from . import bind_skel_shadow
from . import bake_op
from . import const as c
from . import sys_component
from . import notifier
from .log import log
from .util import run


class NotifierGameExport(notifier.Notifier):
    """ Notify when game export panel should be updated.
    """

    descServerName = c.Notifier.GAME_EXPORT
    descUsername = 'Game Export Panel Notifier'


class GameExportCommandId(object):
    ALL_SINGLE_FILE = 'allsingle'
    ALL_MULTIPLE_FILES = 'allmulti'
    SKELETAL_MESH = 'skelmesh'
    ALL_ACTIONS = 'actall'
    CURRENT_ACTION = 'actcur'


class GameExportSet(sys_component.SystemComponent):
    """
    Game Export set is a set of presets for exporting rigs to particular application or engine.

    Attributes
    ----------
    CommandId : GameExportCommandId
        Contains constants for predefined set of export commands.
        When a command is implemented it'll be possible to use it from UI.

    descIdentifier : str
        Unique identifier of the set within all registered sets.
        Usually it'll be lowercase name of the export application ie. unity, unreal, etc.

    descUsername : str
        Name for the set that will be displayed in UI.

    descExportCommands : {GameExportSet.CommandId: GameExportCommand}
        A dictionary with all commands that set implements.
        Key is one of GameExportSet.CommandId, value is a class of implemented command.
    """

    _CHAN_NAME_SET = 'rsGameExportSet'

    CommandId = GameExportCommandId

    descIdentifier = ''
    descUsername = ''
    descExportCommands = {}

    # -------- System component implementation

    @classmethod
    def sysType(cls):
        return c.SystemComponentType.GAME_EXPORT_SET

    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier

    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Game Export Set'

    @classmethod
    def sysSingleton(cls):
        return True

    # -------- Public methods

    @classmethod
    def getGameExportSetFromRig(cls, rig):
        return rig.rootItem.getChannelProperty(cls._CHAN_NAME_SET)

    @classmethod
    def setGameExportSetOnRig(cls, rig, setIdent):
        rig.rootItem.setChannelProperty(cls._CHAN_NAME_SET, setIdent)


class GameExportOperator(object):
    """ Game Export Operator does the real export job.

    Export operator needs to be initialized with rig object and then
    do() methods can be called with export command to perform.

    Paramters
    ---------
    rig : Rig
        Rig to initialize export with.
    """

    @classmethod
    def testExportPath(cls, rig):
        exportPath = rig.rootItem.getChannelProperty(rig.rootItem.PropertyChannels.CHAN_GAME_EXPORT_FOLDER)
        return os.path.isdir(exportPath)

    def do(self, commandClass, monitor=None, ticksCount=0.0):
        """ Perform export process

        Parameters
        ----------
        commandClass : GameExportCommand
            A command to execute to perform export process.

        monitor : modox.Monitor
            Optional progress monitor.

        ticksCount : float, int
            Number of ticks available for the entire export process.
            Monitor will be increased by this number of ticks.
        """
        cmd = commandClass(self._rig)

        bindSkelTicks = ticksCount * 0.45
        bakeTicks = ticksCount * 0.45

        self._preExportCommon()
        cmd.preProcess()
        self._buildBindSkeletonShadow(monitor, bindSkelTicks)
        self._bake(cmd, monitor, bakeTicks)

        cmd.postProcess(self._bindSkelShadow)
        cmd.setSelection(self._bindSkelShadow)
        cmd.save()

        self._postExportCommon()

        if monitor is not None:
            monitor.progress = ticksCount

    # -------- Private methods

    def _export(self, monitor=None):
        """ Main export function. All it does is exports bind skeleton
        in its current state into a file.
        Override this method to do batch export multiple times or implement
        custom export behaviour.
        """
        self._bake(monitor)

        if monitor is not None:
            monitor.Increment(self.monitorStep)

    def _preExportCommon(self):
        pass

    def _postExportCommon(self):
        # Clear FBX preset. It seems like undo doesn't work well
        # if I leave preset selected here.
        run('game.sceneSettings fbxPreset:(none)')

    def _buildBindSkeletonShadow(self, monitor=None, availableTicks=1):
        shadowDesc = bind_skel_shadow.BakeShadowDescription()
        shadowDesc.supportStretching = self._rig.rootItem.settings.get(self._rig.rootItem.SETTING_STRETCH, False)

        self._bindSkelShadow = bind_skel_shadow.BindSkeletonShadow(self._rig)
        self._bindSkelShadow.build(shadowDesc,
                                   monitor=monitor,
                                   availableTicks=availableTicks)

    def _bake(self, cmd, monitor=None, availableTicks=1):
        bakeDesc = bake_op.BakeDescription()
        bakeDesc.actions = cmd.exportActions
        bakeDesc.meshes = cmd.exportMeshes
        bakeDesc.actorName = self._rig.name + "_baked"
        bakeDesc.unlinkSource = True

        self._bake = bake_op.BakeOperator(self._bindSkelShadow)
        self._bake.bake(bakeDesc, monitor=monitor, monitorTicks=availableTicks)

    def __init__(self, rig):
        self._rig = rig


class GameExportCommand(object):
    """
    Game Export Command gets executed to perform export process.

    You need to implement the command for particular export set to have it called from UI.
    """

    Actions = bake_op.BakeActionChoice

    fbxPresetName = ''
    exportMeshes = True
    exportActions = Actions.ALL

    @property
    def fbxFilename(self):
        """
        Name for the filename to save. It's used by standard save() method.

        If you override save() method and you want to provide fbx filename in some other way
        you can ignore this property.
        """
        return ''

    def init(self):
        """
        Init gets called on the initialization of the command object, before
        anything is done to the rig.
        """
        pass

    def preProcess(self):
        """
        Pre processing happens before source rig is baked.
        Use this to prepare the source rig or to set scene state
        before baking.
        """
        pass

    def postProcess(self, bakedSkeleton):
        """
        Post processing happens after creating version of the rig to export
        but before export itself. Use this method to process the export
        rig in any way.

        Parameters
        ----------
        bakedSkeleton : BindSkeletonShadow
            This object gives access to the temporary exportable rig that gets
            created off the source rig.
            This temporary rig is really just a hierarchy of joints with meshes
            and deformers necessary to influence the meshes.
        """
        pass

    def setSelection(self, bakedSkeleton):
        """
        This method sets selection appropriate for export
        (it has to work with what is set in the fbx preset, export selected,
        export hierarchy, etc.).

        By default it selects the folder item that contains entire export rig.
        The assumption is that fbx preset will export item and its hierarchy.
        """
        self.selectBakedSkeletonFolder(bakedSkeleton)

    def save(self):
        """
        This method saves the actual fbx file from the export rig.

        Default implementation selects fbx preset defined in fbxPresetName property
        and exports the rig.

        If you need to perform save in custom way you can reimplement this method.
        """
        self.selectFbxSettingsPreset(self.fbxPresetName)
        self.exportFbxFile(self.fbxFilename)

    @property
    def rig(self):
        """
        Returns source rig object this command will work on.

        Returns
        -------
        Rig
        """
        return self._rig

    def selectBakedSkeletonFolder(self, bakedSkeleton):
        itemSelection = modox.ItemSelection()
        shadowFolder = bakedSkeleton.skeletonRoot
        itemSelection.set(shadowFolder, selMode=modox.SelectionMode.REPLACE)

    def selectFbxSettingsPreset(self, presetName):
        """
        Use this method to select fbx preset.

        This method reverts the preset right after it's selected.
        This is to prevent issues when the preset is somehow changed by user locally.

        Parameters
        ----------
        presetName : str
            Name of the fbx preset to set.
        """
        run('game.sceneSettings fbxPreset:"%s"' % presetName)
        # We need to force revert preset to make sure it was not changed
        # by user accidentaly.
        run('preset.fbx (revert)')

    def exportFbxFile(self, fbxFilename):
        """
        Exports rig to given fbx file.

        Path is determined by export path setting on the rig.

        Parameters
        ----------
        fbxFilename : str
            Name of the fbx file without extension.
        """
        if not fbxFilename:
            log.out("Fbx file not defined, cannot export!", log.MSG_ERROR)
            return

        outputFilename = self._getFbxOutputFilename(fbxFilename)
        cmd = 'game.export exportPath:{%s} fileDialog:false' % outputFilename
        run(cmd)

    # -------- Private methods

    def _getFbxOutputFilename(self, fbxFilename):
        exportPath = self._rig.rootItem.getChannelProperty(self._rig.rootItem.PropertyChannels.CHAN_GAME_EXPORT_FOLDER)
        return os.path.join(exportPath, fbxFilename + os.path.extsep + "fbx")

    def __init__(self, rig):
        self._rig = rig
        self.init()


class ExportSkeletalMeshCommand(GameExportCommand):
    """
    Basic implementation of export command that saves skeletal mesh (mesh + rig skeleton).

    No animation is saved.
    """
    exportActions = GameExportCommand.Actions.NONE
    exportMeshes = True

    @property
    def fbxFilename(self):
        return self.rig.name

    def postProcess(self, bakedSkeleton):
        # Skeleton has to be exported from Setup Mode,
        # it'll have rest pose from currenet animation frame otherwise.
        modox.SetupMode().state = True


class ExportCurrentActionCommand(GameExportCommand):
    """
    Basic implementation of export command that exports current action.
    """

    exportActions = GameExportCommand.Actions.CURRENT
    exportMeshes = False

    def postProcess(self, bakedSkeleton):
        self._bakedActor = bakedSkeleton.actor
        modox.SetupMode().state = False

    @property
    def bakedActor(self):
        return self._bakedActor

    @property
    def fbxFilename(self):
        return self.bakedActor.currentAction.name

    def init(self):
        self._bakedActor = None


class ExportAllActionsCommand(GameExportCommand):
    """
    Basic implementation of export command that exports all actions in separate fbx files.
    """

    exportActions = GameExportCommand.Actions.ALL
    exportMeshes = False

    def postProcess(self, bakedSkeleton):
        """
        Post process is used to cache baked actor item.
        """
        self._bakedActor = bakedSkeleton.actor
        modox.SetupMode().state = False

    @property
    def bakedActor(self):
        return self._bakedActor

    def getFbxActionName(self, actionName):
        return actionName

    def save(self):
        """
        Save method needs to output multiple fbx files.
        """
        self.selectFbxSettingsPreset(self.fbxPresetName
                                     )
        for action in self.bakedActor.actions:
            action.actionClip.SetActive(1)
            filename = self.getFbxActionName(action.name)
            self.exportFbxFile(filename)

    def init(self):
        self._bakedActor = None


class ExportAllSeparateCommand(GameExportCommand):
    """
    Basic implementation of a command that exports both skeletal mesh and all actions in separate files.
    """

    exportActions = GameExportCommand.Actions.ALL
    exportMeshes = True

    skeletalFbxPresetName = ''
    actionFbxPresetName = ''

    def postProcess(self, bakedSkeleton):
        # Cache bind skeleton shadow here.
        self._bakedActor = bakedSkeleton.actor
        self._bakedSkeleton = bakedSkeleton

    @property
    def bakedActor(self):
        return self._bakedActor

    @property
    def skeletalMeshName(self):
        return self.rig.name

    def getFbxActionName(self, actionName):
        return actionName

    def save(self):
        """
        Save method needs to output multiple fbx files.
        """
        setup = modox.SetupMode()
        setup.state = True

        # Export skeletal mesh
        self.selectFbxSettingsPreset(self.skeletalFbxPresetName)
        self.exportFbxFile(self.skeletalMeshName)

        # We unparent bind meshes from bind skeleton shadow hierarchy
        # so they don't get exported in animation clips.
        self._unparentBindMeshes()

        setup.state = False

        # Export all actions
        # Watch out here for the hierarchy root item to still be selected
        # if you do more edits with save before starting actions export.
        # For example removing items from scene seems to clear selection
        # and then you need to select bind skeleton root before export again.
        self.selectFbxSettingsPreset(self.actionFbxPresetName)
        for action in self.bakedActor.actions:
            action.actionClip.SetActive(1)
            filename = self.getFbxActionName(action.name)
            self.exportFbxFile(filename)

    def init(self):
        self._bakedActor = None
        self._bakedSkeleton = None

    # -------- Private methods

    def _unparentBindMeshes(self):
        bindMeshes = self._bakedSkeleton.bindMeshes
        for mesh in bindMeshes:
            mesh.setParent(None)


class ExportAllSingleCommand(GameExportCommand):
    """
    Basic implementation of a command that exports skeletal mesh and actions all within single fbx file.
    """

    exportActions = GameExportCommand.Actions.ALL
    exportMeshes = True

    @property
    def fbxFilename(self):
        return self.rig.name

    def postProcess(self, bakedSkeleton):
        # Saving fbx from setup action so the skeleton has proper rest pose.
        modox.SetupMode().state = True