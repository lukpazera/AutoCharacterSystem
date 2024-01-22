

import lx
import modo
import modox

import rs


def helperGetMeshes(editRig):
    """
    Helper function to get meshes the rig clay command should operate on.

    Returns
    -------
    [Item]
    """
    meshes = modox.ItemSelection().getOfTypeModo(modo.c.MESH_TYPE)

    # Get all the items
    if len(meshes) == 0:
        meshes = editRig[rs.c.ElementSetType.RESOLUTION_BIND_MESHES].elements
        meshes.extend(editRig[rs.c.ElementSetType.RESOLUTION_RIGID_MESHES].elements)
        meshes.extend(editRig[rs.c.ElementSetType.RESOLUTION_BIND_PROXIES].elements)

    return helperGetRigMeshesFromModoMeshes(meshes, editRig)

def helperGetModoMeshes(editRig):
    """
    Helper function to get meshes (as modo items) the rig clay command should operate on.
    """
    meshes = modox.ItemSelection().getOfTypeModo(modo.c.MESH_TYPE)

    # Get all the items
    if len(meshes) == 0:
        meshes = editRig[rs.c.ElementSetType.RESOLUTION_BIND_MESHES].elements
        meshes.extend(editRig[rs.c.ElementSetType.RESOLUTION_RIGID_MESHES].elements)
        meshes.extend(editRig[rs.c.ElementSetType.RESOLUTION_BIND_PROXIES].elements)

    return meshes

def helperGetRigMeshesFromModoMeshes(meshes, editRig):
    """
    Helper function to filter out meshes not belonging to a given rig.
    """
    # Convert meshes to rig items,
    # only meshes from edit rig are valid.
    rigMeshes = []
    for mesh in meshes:
        try:
            rigItem = rs.Item.getFromModoItem(mesh)
        except TypeError:
            continue

        if editRig == rigItem.rigRootItem:
            rigMeshes.append(rigItem)

    return rigMeshes


class base_PolygonRegionPopupCommand(rs.base_OnModuleCommand):

    ARG_LIST = "list"

    def query(self, argument):
        if argument == self.ARG_LIST:

            module = self.moduleToQuery
            if module is None:
                return 0

            return 0

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.extend(rs.NotifierSet.EDIT_MODULE_CHANGED)
        return notifiers

    # -------- Private methods

    def _getRegionsList(self, module):
        rigClayOp = rs.RigClayModuleOperator(module)
        regionsList = rigClayOp.polygonRegions
        return rs.ItemUtils.sortRigItemsByName(regionsList)

    def _buildPopup(self):
        entries = []
        module = self.moduleToQuery
        regionsList = self._getRegionsList(module)

        for rigItem in regionsList:
            label = rigItem.name
            if not rs.RigClayUtils.isRegionAssignedToMesh(rigItem.modoItem):
                label += '   (Unassigned)'
            entries.append((rigItem.modoItem.id, label))
        return entries


class CmdModuleAssignPolygonRegionPopup(base_PolygonRegionPopupCommand):

    ARG_SYMMETRY = 'symmetry'
    ARG_SELECTION_SET = 'addSelectionSet'

    SYMMETRY_HINTS = ((0, 'none'),
                      (1, 'axis'),
                      (2, 'topo'),
                      (3, 'current'))

    def arguments(self):
        listArg = rs.cmd.Argument(self.ARG_LIST, 'integer')
        listArg.flags = 'query'
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        symmetryArg = rs.cmd.Argument(self.ARG_SYMMETRY, 'integer')
        symmetryArg.hints = self.SYMMETRY_HINTS
        symmetryArg.defaultValue = 1

        selectionSetArg = rs.cmd.Argument(self.ARG_SELECTION_SET, 'boolean')
        selectionSetArg.defaultValue = True
        selectionSetArg.flags = 'optional'

        return [listArg, symmetryArg, selectionSetArg] + rs.base_OnModuleCommand.arguments(self)

    def execute(self, msg, flags):
        identIndex = self.getArgumentValue(self.ARG_LIST)
        if identIndex < 0:
            return
        symmetryMode = self.getArgumentValue(self.ARG_SYMMETRY)

        module = self.moduleToQuery
        regionsList = self._getRegionsList(module)
        try:
            rs.RigClayUtils.assignSelectedPolygonsToRegion(regionsList[identIndex].modoItem, symmetryMode)
        except IndexError:
            pass

        rs.run('select.drop polygon')

rs.cmd.bless(CmdModuleAssignPolygonRegionPopup, 'rs.module.assignPolygonRegionPopup')


class CmdModuleClearPolygonRegionPopup(base_PolygonRegionPopupCommand):

    ARG_SYMMETRY = 'symmetry'
    ARG_SELECTION_SET = 'keepSelectionSet'

    def arguments(self):
        listArg = rs.cmd.Argument(self.ARG_LIST, 'integer')
        listArg.flags = 'query'
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        symmetryArg = rs.cmd.Argument(self.ARG_SYMMETRY, 'boolean')
        symmetryArg.defaultValue = True

        selectionSetArg = rs.cmd.Argument(self.ARG_SELECTION_SET, 'boolean')
        selectionSetArg.defaultValue = True
        selectionSetArg.flags = 'optional'

        return [listArg, symmetryArg, selectionSetArg] + rs.base_OnModuleCommand.arguments(self)

    def execute(self, msg, flags):
        identIndex = self.getArgumentValue(self.ARG_LIST)
        if identIndex < 0:
            return
        symmetry = self.getArgumentValue(self.ARG_SYMMETRY)
        clearSelectionSets = not self.getArgumentValue(self.ARG_SELECTION_SET)

        module = self.moduleToQuery
        rig = rs.Rig(module.rigRootItem)
        regionsList = self._getRegionsList(module)
        meshes = helperGetModoMeshes(rig)
        try:
            rs.RigClayUtils.clearSetupFromRegions(regionsList[identIndex].modoItem,
                                                  meshes,
                                                  clearSelectionSets,
                                                  symmetry)
        except IndexError:
            pass

rs.cmd.bless(CmdModuleClearPolygonRegionPopup, 'rs.module.clearPolygonRegionPopup')


class CmdRigClayAutoSetup(rs.RigCommand):
    """
    Auto setup will work on all meshes in current resolution if nothing is selected
    or only on selection if there are some meshes selected.
    """

    ARG_METHOD = 'method'
    ARG_ADD_SELECTION_SETS = 'addSelectionSets'

    METHOD_HINTS = ((0, 'default'),
                    (1, 'selsets'))

    def arguments(self):
        methodArg = rs.cmd.Argument(self.ARG_METHOD, 'integer')
        methodArg.hints = self.METHOD_HINTS
        methodArg.flags = 'hidden'
        methodArg.defaultValue = 0

        selectionSetArg = rs.cmd.Argument(self.ARG_ADD_SELECTION_SETS, 'boolean')
        selectionSetArg.defaultValue = True

        return [methodArg, selectionSetArg] + rs.RigCommand.arguments(self)

    def uiHints(self, argument, hints):
        if argument == self.ARG_ADD_SELECTION_SETS:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def icon(self):
        method = self.getArgumentValue(self.ARG_METHOD)
        if method == 1:  # selection sets
            return 'rs.rig.clayAutoSetupFromSets'
        return 'rs.rig.clayAutoSetup'
    
    def execute(self, msg, flags):
        methodArg = self.getArgumentValue(self.ARG_METHOD)
        addSelectionSets = self.getArgumentValue(self.ARG_ADD_SELECTION_SETS)

        editRig = self.firstRigToEdit
        rigMeshes = helperGetMeshes(editRig)

        if not rigMeshes:
            return

        if methodArg == 0:  # Default setup from bind joints and weight maps
            for mesh in rigMeshes:
                if mesh.type in [rs.c.RigItemType.BIND_MESH]:
                    self._setupRegionsFromWeightMaps(editRig, mesh.modoItem, addSelectionSets)
                elif mesh.type in [rs.c.RigItemType.BIND_PROXY, rs.c.RigItemType.RIGID_MESH]:
                    self._setupRegionOnAttachedMesh(mesh, addSelectionSets)

            rs.run('!select.vertexMap {} wght remove')

        # Setup from selection sets
        else:
            modoMeshes = [rigMesh.modoItem for rigMesh in rigMeshes]
            self._setupRegionsFromSelectionSets(editRig, modoMeshes)

        # Restore scene state
        rs.run('select.drop polygon')
        rs.run('!select.type item')
        modo.Scene().deselect(None)

    # -------- Private methods

    def _setupRegionsFromWeightMaps(self, editRig, mesh, addSelectionSets=True):
        scene = modo.Scene()
        # attachments = rs.Attachments(editRig)
        bindSkeleton = rs.BindSkeleton(editRig)

        bindlocsByMap = {}

        for bindloc in bindSkeleton.items:
            mapName = bindloc.weightMapName
            if mapName is not None:
                bindlocsByMap[mapName] = bindloc

        scene.select(mesh, add=False)

        # Selected weight map first.
        # We have to select weights for each mesh separately.
        # This is because we do not want to select maps that are not on a given mesh.
        # If map does not exist on a mesh the command will throw RuntimeError.
        lx.eval('!select.vertexMap {} wght remove')
        for mapName in bindlocsByMap:
            try:
                # Note that I'm using commands for setting and clearing vertex map selection.
                # This is because using vertex map selection class from modox is somehow
                # getting MODO in a bad state and eventually causing crash.
                lx.eval('!select.vertexMap {%s} wght add' % mapName)
            except RuntimeError:
                pass

        # This creates selection set for each region.
        rs.run('!rs.mesh.partitionByWeights item:%s subdivide:0 doubleSided:0 selectionSet:1' % (
        mesh.id))

        rs.run('select.type polygon')

        for mapName in bindlocsByMap:
            bindLoc = bindlocsByMap[mapName]
            relatedRegion = bindLoc.relatedCommandRegion
            if relatedRegion is None:
                continue
            # Selection set name is mesh name, '-' and map name.
            selectionSetName = mesh.name + '-' + mapName
            rs.run('select.drop polygon')
            rs.run('select.useSet {%s} select' % selectionSetName)
            rs.RigClayUtils.assignSelectedPolygonsToRegion(relatedRegion)

            # depending on the add selection sets argument we either rename existing
            # selection set properly or delete the set.
            if addSelectionSets:
                newSelectionSetName = rs.RigClayUtils.renderSelectionSetName(relatedRegion)
                rs.run('select.editSet "%s" rename "%s"' % (selectionSetName, newSelectionSetName))
            else:
                rs.run('select.deleteSet {%s}' % selectionSetName)

        rs.run('select.drop polygon')

    def _setupRegionOnAttachedMesh(self, mesh, addSelectionSets=True):
        attachedItem = rs.AttachItem(mesh)
        bindLoc = attachedItem.attachedToBindLocator
        if bindLoc is None:
            return
        relatedRegion = bindLoc.relatedCommandRegion
        if relatedRegion is None:
            return

        rs.RigClayUtils.setupRegionOnWholeMesh(mesh.modoItem, relatedRegion, addSelectionSets)

    def _setupRegionsFromSelectionSets(self, rig, meshes):
        scene = modo.Scene()
        scene.select(meshes, add=False)
        polygonSelection = modox.PolygonSelection()
        regions = rs.RigClayOperator(rig).polygonRegions
        for region in regions:
            selectionSetName = rs.RigClayUtils.renderSelectionSetName(region.modoItem)
            rs.run('select.drop polygon')
            rs.run('!select.useSet {%s} select' % selectionSetName)
            if polygonSelection.size == 0:
                continue
            rs.RigClayUtils.assignSelectedPolygonsToRegion(region.modoItem, addSelectionSet=False)

rs.cmd.bless(CmdRigClayAutoSetup, 'rs.rig.clayAutoSetup')


class CmdRigClayMode(rs.Command):
    """ Switches between one of 1 rig clay modes.
    """

    ARG_MODE = 'mode'

    MODE_HINTS = ((0, 'tool'),
                  (1, 'free'),
                  (2, 'constrained'))

    MODE_INT_TO_CLAY_MODE = {
        0: rs.RigClayOperator.ClayMode.TOOL,
        1: rs.RigClayOperator.ClayMode.FREE,
        2: rs.RigClayOperator.ClayMode.CONSTRAINED
    }

    def icon(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        if mode == 1:  # gesture
            return 'rs.rig.clayModeGesture'
        return 'rs.rig.clayModeTool'

    def arguments(self):
        modeArg = rs.cmd.Argument(self.ARG_MODE, 'integer')
        modeArg.hints = self.MODE_HINTS
        modeArg.defaultValue = 0

        return [modeArg]

    def basic_ButtonName(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)

    def cmd_Tooltip(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDTOOLTIP, key)

    def execute(self, msg, flags):
        mode = self.getArgumentValue(self.ARG_MODE)

        rsScene = rs.Scene()
        for rig in rsScene.rigs:
            clayOp = rs.RigClayOperator(rig)
            clayOp.setClayMode(self.MODE_INT_TO_CLAY_MODE[mode])

        rs.run('tool.drop')

    # -------- Private methods

    def _getMsgKey(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        if mode == 0:  # tool
            token = 'Tool'
        else:
            token = 'Gest'

        return 'clayMode' + token

rs.cmd.bless(CmdRigClayMode, 'rs.rig.clayMode')


class CmdRigClayClearModuleSetup(rs.RigCommand):
    """ Clear module rig clay setup.
    """

    ARG_SYMMETRY = 'symmetry'
    ARG_KEEP_SETS = 'keepSelectionSets'

    def arguments(self):
        symmetryArg = rs.cmd.Argument(self.ARG_SYMMETRY, 'boolean')
        symmetryArg.defaultValue = True

        clearSetsArg = rs.cmd.Argument(self.ARG_KEEP_SETS, 'boolean')
        clearSetsArg.defaultValue = True

        return [symmetryArg, clearSetsArg] + rs.RigCommand.arguments(self)

    def execute(self, msg, flags):
        # Need to clear all component selection
        # the command will not work otherwise.
        rs.run('select.drop vertex')
        rs.run('select.drop edge')
        rs.run('select.drop polygon')

        clearSets = not self.getArgumentValue(self.ARG_KEEP_SETS)
        symmetry = self.getArgumentValue(self.ARG_SYMMETRY)

        rig = self.firstRigToEdit
        meshes = helperGetMeshes(rig)
        modoMeshes = [mesh.modoItem for mesh in meshes]

        module = rig.modules.editModule
        if module:
            rigClayModuleOp = rs.RigClayModuleOperator(module)
            rigClayModuleOp.clearSetup(modoMeshes, clearSets, symmetry)

        rs.run('!select.type item')

rs.cmd.bless(CmdRigClayClearModuleSetup, 'rs.module.clearClaySetup')


class CmdRigClayClearSetup(rs.RigCommand):
    """ Clear entire rig clay setup.
    """

    ARG_KEEP_SETS = 'keepSelectionSets'

    def arguments(self):
        clearSetsArg = rs.cmd.Argument(self.ARG_KEEP_SETS, 'boolean')
        clearSetsArg.defaultValue = True

        return [clearSetsArg] + rs.RigCommand.arguments(self)

    def icon(self):
        return 'rs.gen.delete'

    def execute(self, msg, flags):
        # Need to clear all component selection
        # the command will not work otherwise.
        rs.run('select.drop vertex')
        rs.run('select.drop edge')
        rs.run('select.drop polygon')

        clearSets = not self.getArgumentValue(self.ARG_KEEP_SETS)

        rig = self.firstRigToEdit
        meshes = helperGetMeshes(rig)
        modoMeshes = [mesh.modoItem for mesh in meshes]

        rigClayOp = rs.RigClayOperator(rig)
        rigClayOp.clearSetup(modoMeshes, clearSets)

        rs.run('!select.type item')

rs.cmd.bless(CmdRigClayClearSetup, 'rs.rig.clearClaySetup')


class CmdRigClayEnable(rs.RigCommand):
    """ Use this to toggle command regions on/off.
    """

    ARG_STATE = 'state'

    def arguments(self):
        stateArg = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        stateArg.flags = 'query'
        stateArg.defaultValue = True

        return [stateArg] + rs.RigCommand.arguments(self)

    def execute(self, msg, flags):
        state = bool(self.getArgumentValue(self.ARG_STATE))
        rs.RigClayUtils.setRegionsEnableState(state)

    def query(self, argument):
        if argument == self.ARG_STATE:
            return rs.RigClayUtils.getRegionsEnableState()
        return False

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append((rs.c.Notifier.CMD_REGION_DISABLE, '+d'))
        return notifiers

rs.cmd.bless(CmdRigClayEnable, 'rs.gesture.enable')


class CmdRigClayRegionsOpacity(rs.RigCommand):
    """ Use this to change opacity of all regions in the rig.
    """

    ARG_VALUE = 'value'

    def arguments(self):
        valueArg = rs.cmd.Argument(self.ARG_VALUE, 'percent')
        valueArg.defaultValue = 0.7

        return [valueArg] + rs.RigCommand.arguments(self)

    def execute(self, msg, flags):
        value = self.getArgumentValue(self.ARG_VALUE)
        rig = rs.Scene().editRig

        clayOperator = rs.RigClayOperator(rig)
        clayOperator.setRegionsOpacity(value)

rs.cmd.bless(CmdRigClayRegionsOpacity, 'rs.rig.clayOpacity')
