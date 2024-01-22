

import lx
import lxu
import modo
import modox

from .module import Module
from .log import log
from .rig import Rig
from .util import run
from .item import Item
from .log import log
from . import const as c
from .const import EventTypes as e
from .event_handler import EventHandler
from .item_features.controller import ControllerItemFeature
from .scene import Scene
from .core import service
from .scene_event import SceneEvent


class RigClaySymmetryMode(object):
    NONE = 0
    AXIS = 1
    TOPOLOGICAL = 2
    CURRENT = 3


class RigClayUtils(object):

    SymmetryMode = RigClaySymmetryMode

    @classmethod
    def setupRegionOnWholeMesh(cls, meshItem, regionItem, addSelectionSet=True):
        """
        Parameters
        ----------
        meshItem : modo.Item

        regionItem : modo.Item

        addSelectionSet : bool
            When True selection set will be created for the region.
        """
        scene = modo.Scene()
        scene.select(meshItem, add=False)
        run('!select.type polygon')
        run('!select.all')
        cls.assignSelectedPolygonsToRegion(regionItem, addSelectionSet=addSelectionSet)
        cls._assignRegionToPolygonSelection(regionItem, addSelectionSet)

    @classmethod
    def assignSelectedPolygonsToRegion(cls,
                                       regionItem,
                                       symmetryMode=RigClaySymmetryMode.NONE,
                                       addSelectionSet=True):
        """
        Assigns polygons currently selected in a scene to given polygon region.

        This function assumes MODO is in polygon selection mode and
        relevant mesh is selected too.

        Parameters
        ----------
        regionRigItem : modo.Item

        symmetryMode : int

        addSelectionSet : bool
        """
        cls._assignRegionToPolygonSelection(regionItem, addSelectionSet)
        cls._assignRegionToSymmetric(regionItem, symmetryMode, addSelectionSet)

    @classmethod
    def isRegionAssignedToMesh(cls, regionItem):
        """
        Tests whether given region has at least one mesh assigned.
        """
        return modox.ItemUtils.hasReverseGraphConnections(regionItem, 'cmdRegion.mesh.graph')

    @classmethod
    def renderSelectionSetName(cls, regionModoItem):
        """
        Renders name for selection set that should be associated with particular region.

        Parameters
        ----------
        regionModoItem : modo.Item, Item

        Returns
        -------
        str
        """
        rigItem = Item.getFromOther(regionModoItem)

        rigName = rigItem.rigRootItem.name
        nameBody = rigItem.referenceUserName

        return rigName + ': ' + nameBody + ' Region'

    @classmethod
    def clearSetupFromRegions(cls,
                              regions,
                              meshes,
                              clearSelectionSets=False,
                              symmetry=True):
        """
        Clears rig clay setup from given regions.

        Parameters
        ----------
        regions : [Item], Item, [modo.Item], modo.Item
            Regions need to be passed as rig items.

        meshes : [modo.Item]
            List of meshes that should be affected.

        clearSelectionSets : bool, optional
            Set this to False if you want to keep selection sets outlining
            all the regions.

        symmetry : bool
            When True region will be cleared from symmetrical module too (if any is found).
        """
        if type(regions) not in (list, tuple):
            regions = [regions]

        run('!select.type item')
        modox.ItemSelection().set(meshes, modox.SelectionMode.REPLACE)

        for region in regions:
            try:
                regionModoItem = region.modoItem
            except AttributeError:
                regionModoItem = region
            cls._clearRegion(regionModoItem, clearSelectionSets)
            if symmetry:
                cls._clearRegionFromSymmetric(regionModoItem, clearSelectionSets)

    @classmethod
    def getRegionsEnableState(cls):
        """
        Gets command regions state for animate context.

        Returns
        -------
        bool
        """
        return Scene().settings.get('cmdreg', cls._getRegionsStateFromScene())

    @classmethod
    def setRegionsEnableState(cls, state):
        """
        Sets regions enable state for animate context.

        Parameters
        ----------
        state : bool
        """
        if state:
            # Make sure to enable regions both as a whole and also command regions tool.
            # Command region tool needs to be switched after disable toggle is off,
            # the gesture.enable command is disabled otherwise.
            run('!cmdRegions.disable disable:0')  # main on/off switch
            run('!gesture.enable 1')  # command regions tool
        else:
            # This disables regions completely so they don't appear over meshes at all.
            run('!cmdRegions.disable disable:1')

        Scene().settings.set('cmdreg', state)

    @classmethod
    def setRegionsEnableStateFromScene(cls):
        """
        Sets animate context command regions state based on values of MODO's native switches.

        Regions will be enabled when both the main disable switch is off and
        the gesture tool is on. It'll be set to False otherwise.
        """
        state = cls._getRegionsStateFromScene()
        cls.setRegionsEnableState(state)

    @classmethod
    def updateRegionsEnableState(cls):
        """
        Reinforces animate context regions state.

        If the state is not stored in the scene yet it'll be saved based on current
        state of MODO's native command regions switches.
        """
        state = cls.getRegionsEnableState()
        cls.setRegionsEnableState(state)

    # -------- Private methods

    @classmethod
    def _getRegionsStateFromScene(cls):
        state = True
        disable = bool(run('!cmdRegions.disable disable:?'))
        if disable:
            state = False

        if state:
            tool = bool(run('!gesture.enable ?'))
            if not tool:
                state = False

        return state

    @classmethod
    def _clearRegion(cls, regionModoItem, clearSelectionSet=False):
        run('!item.pcrClear "%s"' % regionModoItem.name)

        if clearSelectionSet:
            run('!select.type polygon')
            selectionSetName = RigClayUtils.renderSelectionSetName(regionModoItem)
            run('!select.deleteSet "%s"' % selectionSetName)

    @classmethod
    def _assignRegionToSymmetric(cls, regionItem, symmetryMode, addSelectionSet):
        if symmetryMode == RigClaySymmetryMode.NONE:
            return True

        try:
            symmetricRegionRigItem = cls._getSymmetricRegion(regionItem)
        except LookupError:
            return False

        cls._setSymmetry(symmetryMode)

        if cls._makeSymmetricalSelection():
            cls._assignRegionToPolygonSelection(symmetricRegionRigItem.modoItem, addSelectionSet)

        cls._revertSymmetry(symmetryMode)

        return True

    @classmethod
    def _clearRegionFromSymmetric(cls, regionModoItem, clearSelectionSet):
        try:
            symmetricRegionRigItem = cls._getSymmetricRegion(regionModoItem)
        except LookupError:
            return False

        cls._clearRegion(symmetricRegionRigItem.modoItem, clearSelectionSet)

        return True

    @classmethod
    def _makeSymmetricalSelection(cls):
        # Get polygon selection
        # Try to get symmetrical polygons using polygon interface and Symmetry() method.
        polySelection = modox.PolygonSelection()
        selectedPolys = polySelection.get()

        if len(selectedPolys) == 0:
            return False

        symmetricIds = []
        for mesh, meshPolygon in selectedPolys:
            # Ignore polygons belonging to bind proxies or bind locators
            # we don't support symmetry on these.
            if Item.getTypeFromModoItem(mesh) in [c.RigItemType.BIND_PROXY, c.RigItemType.RIGID_MESH]:
                continue

            try:
                # There's inconsistency between OSX and Win here.
                # Win returns id as long which is what is needed, OSX returns int.
                # Casting to long is crucial to make the code work on OSX.
                symmetricId = int(meshPolygon.accessor.Symmetry())
            except RuntimeError:
                continue

            symmetricIds.append(symmetricId)

        if len(symmetricIds) > 0:
            selectedPolys[0][0].geometry.polygons.select(symmetricIds, replace=True)
            return True

        return False

    @classmethod
    def _setSymmetry(cls, symmetryMode=RigClaySymmetryMode.NONE):
        # If symmetry mode is set to current we do not touch symmetry settings.
        # For other modes we do change settings and then revert back
        # after we're done.
        if symmetryMode != RigClaySymmetryMode.CURRENT:
            # Set up axis symmetry.
            # backup symmetry settings
            cls._symBkp = bool(run('!symmetry.state ?'))
            cls._symAxis = run('symmetry.axis ?')
            cls._topoBkp = bool(run('!symmetry.topology ?'))

            run('!symmetry.state 1')
            run('!symmetry.axis 0')  # X axis

            if symmetryMode == RigClaySymmetryMode.TOPOLOGICAL:
                run('!symmetry.topology 1')
            else:
                run('!symmetry.topology 0')

    @classmethod
    def _revertSymmetry(cls, symmetryMode=RigClaySymmetryMode.NONE):
        # Restore symmetry settings
        if symmetryMode != RigClaySymmetryMode.CURRENT:
            run('!symmetry.topology %d' % int(cls._topoBkp))
            run('!symmetry.axis %d' % cls._symAxis)
            run('!symmetry.state %d' % int(cls._symBkp))

    @classmethod
    def _assignRegionToPolygonSelection(self, regionModoItem, addSelectionSet=True):
        itemSel = modox.ItemSelection()
        itemSel.set(regionModoItem, selMode=modox.SelectionMode.ADD)
        run('!polyCmdRegion.edit mode:add')

        if addSelectionSet:
            selectionSetName = self.renderSelectionSetName(regionModoItem)
            self._clearAllOtherRegionSelectionSetsFromPolygonSelection(selectionSetName)
            run('!select.editSet "%s" add' % selectionSetName)

        itemSel.set(regionModoItem, selMode=modox.SelectionMode.SUBSTRACT)

    @classmethod
    def _clearAllOtherRegionSelectionSetsFromPolygonSelection(cls, selectionSetName):
        rigNameLength = selectionSetName.find(':') + 1
        rigNamePrefix = selectionSetName[:rigNameLength]

        polySelection = modox.PolygonSelection()
        selectedPolys = polySelection.get()

        tagID = lxu.lxID4('PICK')
        for mesh, meshPolygon in selectedPolys:
            try:
                v = meshPolygon.getTag(tagID)
            except LookupError:
                continue
            sets = v.split(';')

            for selset in sets:
                if selset == selectionSetName:
                    continue
                if selset.startswith(rigNamePrefix):
                    lx.eval('select.editSet "%s" remove' % selset)

    @classmethod
    def _getSymmetricRegion(cls, regionItem):
        # Check to which module region item belongs
        try:
            regionRigItem = Item.getFromModoItem(regionItem)
        except TypeError:
            raise LookupError

        try:
            module = Module(regionRigItem.moduleRootItem)
        except TypeError:
            raise LookupError

        # Check if this module has symmetrical counterpart.
        try:
            symmetryRelatedModule = module.symmetryLinkedModules[0]
        except IndexError:
            raise LookupError

        # Find region with the same name in the other module.
        symModuleRigClayOp = RigClayModuleOperator(symmetryRelatedModule)
        symRegions = symModuleRigClayOp.polygonRegions

        symmetricRegionRigItem = None
        nameToMatch = regionRigItem.name
        for region in symRegions:
            if region.name == nameToMatch:
                symmetricRegionRigItem = region
                break

        if symmetricRegionRigItem is None:
            raise LookupError

        return symmetricRegionRigItem


class RigClayAssemblyItem(Item):

    descType = c.RigItemType.RIG_CLAY_ASSEMBLY
    descUsername = 'Rig Clay Assembly'
    descModoItemType = 'group'
    descModoItemSubtype = 'assembly'
    descFixedModoItemType = True
    descDefaultName = 'Rig Clay'
    descPackages = ['rs.pkg.generic']

    def onAdd(self, subtype):
        xitem = modox.Item(self.modoItem.internalItem)
        c1 = xitem.addUserChannel('rsrcFreeform', lx.symbol.sTYPE_BOOLEAN, 'Gesture Freeform')
        c2 = xitem.addUserChannel('rsrcConstrained', lx.symbol.sTYPE_BOOLEAN, 'Gesture Constrained')
        c3 = xitem.addUserChannel('rsrcTool', lx.symbol.sTYPE_BOOLEAN, 'Tool')
        modox.Assembly.assignChannelsAsInput([c1, c2, c3])


class RigClayMode(object):

    TOOL = 0,
    FREE = 1,
    CONSTRAINED = 2


class RigClayOperator(object):

    ClayMode = RigClayMode

    def setClayMode(self, mode):
        """
        Sets rig clay interaction mode to one of 3 possible ones.

        Parameters
        ----------
        mode : int
            One of RigClayMode constants.
        """
        for module in self._rig.modules.allModules:
            moduleOp = RigClayModuleOperator(module)

            clayAssemblies = moduleOp.rigClayAssemblies

            if mode == self.ClayMode.TOOL:
                values = (True, False, False)
            elif mode == self.ClayMode.FREE:
                values = (False, True, False)
            else:
                values = (False, False, True)

            channelNames = ('rsrcTool', 'rsrcFreeform', 'rsrcConstrained')

            for rigItem in clayAssemblies:
                for x in range(len(values)):
                    channel = rigItem.modoItem.channel(channelNames[x])
                    if not channel:
                        continue
                    value = values[x]
                    channel.set(value, 0.0, False, lx.symbol.s_ACTIONLAYER_SETUP)

    def setRegionsOpacity(self, value):
        """
        Sets opacity for all regions in the rig.

        Parameters
        ----------
        value : float
        """
        for region in self.polygonRegions:
            modoxRegion = modox.CommandRegionPolygon(region.modoItem)
            modoxRegion.opacity = value

    @property
    def polygonRegions(self):
        """
        Gets all polygon regions in entire rig.

        Returns
        -------
        [Item]
        """
        regions = []
        for module in self._rig.modules.allModules:
            moduleOp = RigClayModuleOperator(module)
            regions.extend(moduleOp.polygonRegions)
        return regions

    def clearSetup(self, meshes, clearSelectionSets=False):
        """
        Clears rig clay setup from the rig.

        Parameters
        ----------
        clearSelectionSets : bool
            Set this to False if you want to keep selection sets outlining
            all the regions.
        """
        allRegions = self.polygonRegions
        RigClayUtils.clearSetupFromRegions(allRegions,
                                           meshes,
                                           clearSelectionSets,
                                           symmetry=False)

    # -------- Private methods

    def __init__(self, rigInitializer):
        if not isinstance(rigInitializer, Rig):
            try:
                self._rig = Rig(rigInitializer)
            except TypeError:
                raise
        else:
            self._rig = rigInitializer


class RigClayModuleOperator(object):

    @property
    def polygonRegions(self):
        """
        Gets a list of polygon regions in a module.

        Returns
        -------
        [Item]
        """
        self._regions = []
        modox.Assembly.iterateOverItems(self._module.assemblyModoItem,
                                        self._testPolygonCommandRegion,
                                        includeSubassemblies=True)
        regionRigItems = []
        for regionModoItem in self._regions:
            try:
                rigItem = Item.getFromModoItem(regionModoItem)
            except TypeError:
                continue
            regionRigItems.append(rigItem)
        return regionRigItems

    @property
    def rigClayAssemblies(self):
        """
        Gets all the rig clay assemblies that are in the module.

        Returns
        -------
        [RigClayAssemblyItem]
        """
        self._clayAssemblies = []
        modox.Assembly.iterateOverItems(self._module.assemblyModoItem,
                                        self._testRigClayAssembly,
                                        includeSubassemblies=True)
        return self._clayAssemblies

    def clearSetup(self, meshes, clearSelectionSets=False, symmetry=False):
        """
        Clears rig clay regions from entire module.

        Parameters
        ----------
        meshes : [modo.Item]

        clearSelectionSets : bool
        """
        regions = self.polygonRegions
        RigClayUtils.clearSetupFromRegions(regions,
                                           meshes,
                                           clearSelectionSets,
                                           symmetry=symmetry)

    # -------- Private methods

    def _testPolygonCommandRegion(self, modoItem):
        if modoItem.type == 'cmdRegionPolygon':
            self._regions.append(modoItem)

    def _testRigClayAssembly(self, modoItem):
        try:
            rigItem = RigClayAssemblyItem(modoItem)
        except TypeError:
            return
        self._clayAssemblies.append(rigItem)

    def __init__(self, moduleInitializer):
        if not isinstance(moduleInitializer, Module):
            try:
                self._module = Module(moduleInitializer)
            except TypeError:
                raise
        else:
            self._module = moduleInitializer


class RigClayEventHandler(EventHandler):
    """ Handles events that affect rig clay setup.
    """

    descIdentifier = 'rigclay'
    descUsername = 'Rig Clay'

    @property
    def eventCallbacks(self):
        return {e.RIG_NAME_CHANGED: self.event_rigNameChanged,
                e.RIG_STANDARDIZE_PRE: self.event_rigStandardizePre,
                e.MODULE_SAVE_PRE: self.event_moduleSavePre,
                e.MODULE_NAME_CHANGED: self.event_moduleNameChanged,
                e.MODULE_SIDE_CHANGED: self.event_moduleSideChanged}

    def event_rigNameChanged(self, **kwargs):
        try:
            rig = kwargs['rig']
        except KeyError:
            return
        try:
            oldName = kwargs['oldName']
        except KeyError:
            return
        try:
            newName = kwargs['newName']
        except KeyError:
            return

        if oldName == newName:
            return

        meshes = rig[c.ElementSetType.RESOLUTION_BIND_MESHES].elements
        meshes.extend(rig[c.ElementSetType.RESOLUTION_RIGID_MESHES].elements)
        meshes.extend(rig[c.ElementSetType.RESOLUTION_BIND_PROXIES].elements)

        rigOp = RigClayOperator(rig)
        rigRegions = rigOp.polygonRegions  # list of Item

        newNameLength = len(newName)

        for mesh in meshes:
            mesh.select(replace=True)
            run('select.type polygon')

            for region in rigRegions:
                regionNewName = RigClayUtils.renderSelectionSetName(region)
                regionOldName = oldName + regionNewName[newNameLength:]
                run('!select.editSet "%s" rename "%s"' % (regionOldName, regionNewName))
                # Need to delete the old set for some reason as renaming the set is duplicating it with new name
                run('!select.deleteSet "%s"' % regionOldName)

        run('select.type item')

    def event_rigStandardizePre(self, **kwargs):
        """
        To standardize rig clay setup we need to get all the region command nodes
        and check item command on them.
        If it's a generic rig system command and rig controller is plugged into
        command as item selection - we take baked (evaluated) rig controller item command
        string and set it on the command node.
        This way the command on the node is the same as on the controller
        and can be run on vanilla MODO.

        NOTE: Better solution is to make rig clay setup command nodes get commands
        from controller item directly by linking command channels between node and the controller.
        """
        try:
            rig = kwargs['rig']
        except KeyError:
            return

        rigOp = RigClayOperator(rig)
        rigRegions = rigOp.polygonRegions

        # We need to standardize all the
        commandsToStandardize = []

        for rigRegion in rigRegions:
            try:
                polyRegion = modox.CommandRegionPolygon(rigRegion.modoItem)
            except TypeError:
                continue

            gestures = polyRegion.gestures
            if not gestures:
                continue

            for gesture in gestures:
                commandsToStandardize.extend(gesture.commands)

        for cmd in commandsToStandardize:
            # Skip processing command node if it's not firing
            # generic rig system command
            if cmd.commandString != c.ItemCommand.GENERIC:
                continue

            itemSelection = cmd.itemSelection
            if not itemSelection or len(itemSelection) == 0:
                continue

            for modoItem in itemSelection:
                try:
                    ctrl = ControllerItemFeature(modoItem)
                except TypeError:
                    cmd.commandString = None
                    continue

                # Remember, baked item command string will be either string or None
                # if command can't be converted to vanilla MODO
                itemCmdString = ctrl.bakedItemCommandString
                cmd.commandString = itemCmdString  # Setting commandString property accepts None to set cmd to empty string
                break

    def event_moduleSavePre(self, **kwargs):
        run('!rs.rig.clayMode tool')

    def event_moduleNameChanged(self, **kwargs):
        try:
            module = kwargs['module']
        except KeyError:
            return
        try:
            oldName = kwargs['oldName']
        except KeyError:
            return
        try:
            newName = kwargs['newName']
        except KeyError:
            return

        newRefName = module.referenceName
        oldRefName = newRefName.replace(newName, oldName)

        modOp = RigClayModuleOperator(module)
        for region in modOp.polygonRegions:
            commandRegion = modox.CommandRegionPolygon(region.modoItem)
            currentToolTip = commandRegion.tooltip
            commandRegion.tooltip = currentToolTip.replace(oldRefName, newRefName)

    def event_moduleSideChanged(self, **kwargs):
        try:
            module = kwargs['module']
        except KeyError:
            return
        try:
            oldSide = kwargs['oldSide']
        except KeyError:
            return
        try:
            newSide = kwargs['newSide']
        except KeyError:
            return

        newRefName = module.referenceName
        oldRefName = module.renderReferenceNameFromTokens(oldSide, module.name)

        modOp = RigClayModuleOperator(module)
        for region in modOp.polygonRegions:
            commandRegion = modox.CommandRegionPolygon(region.modoItem)
            currentToolTip = commandRegion.tooltip
            commandRegion.tooltip = currentToolTip.replace(oldRefName, newRefName)


class event_CommandRegionsDisableToggled(SceneEvent):

    descIdentifier = 'cmdRegDisable'
    descUsername = 'Command Regions Disable Toggled'

    def process(self, arguments):
        RigClayUtils.setRegionsEnableStateFromScene()