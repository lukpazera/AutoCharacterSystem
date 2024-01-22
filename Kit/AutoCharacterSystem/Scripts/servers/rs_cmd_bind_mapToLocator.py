

import lx
import lxifc
import lxu
import modo
import modox

import rs


class QueryWeightMapsNamesVisitor(lxifc.Visitor):
    """ Helper class to get list of weight maps from a mesh.
    """
    def __init__(self, meshmap):
        self._meshmap = meshmap
        self._meshService = lx.service.Mesh()
        self.mapNames = []

    def vis_Evaluate(self):
        mapType = self._meshmap.Type()
        if mapType != lx.symbol.i_VMAP_WEIGHT:
            return

        name = self._meshmap.Name()
        if not name:
            return

        self.mapNames.append(name)


class CmdBindMapWeightToLocatorPopup(rs.Command):
    """ Sets or queries weight map that will be mapped to bind locator.
    """

    ARG_BIND_LOCATOR = 'bindLoc'
    ARG_MESH = 'mesh'
    ARG_INDEX = 'popupIndex'
    
    def arguments(self):
        bloc = rs.cmd.Argument(self.ARG_BIND_LOCATOR, 'string')
        
        mesh = rs.cmd.Argument(self.ARG_MESH, '&item')
        
        index = rs.cmd.Argument(self.ARG_INDEX, 'integer')
        index.flags = 'query'
        index.valuesList = self._buildPopup
        index.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        return [bloc, mesh, index]

    def basic_ButtonName(self):
        bloc = self._getBindLocator()
        return bloc.name

    def execute(self, msg, flags):
        index = self.getArgumentValue(self.ARG_INDEX)
        
        bindLoc = self._getBindLocator()
        if bindLoc is None:
            return

        mesh = self._getBindMesh()
        if mesh is None:
            return
        
        wmapNames = self._getWeightMapNames(mesh.modoItem)

        if index == 0:
            wmapToSet = None
        else:
            index -= 1
        
            try:
                wmapToSet = wmapNames[index]
            except IndexError:
                return
        
        mesh.bindMap.setMapping(bindLoc, wmapToSet)

    def query(self, argument):
        if argument == self.ARG_INDEX:
            bindLoc = self._getBindLocator()
            if bindLoc is None:
                return 0
 
            mesh = self._getBindMesh()
            if mesh is None:
                return 0
            
            wmapNames = self._getWeightMapNames(mesh.modoItem)
            try:
                mappedWeightMap = mesh.bindMap.getMapping(bindLoc)
            except LookupError:
                return 0
            
            if not mappedWeightMap:
                return 0
            
            try:
                index = wmapNames.index(mappedWeightMap)
            except ValueError:
                index = -1
            
            if index >= 0:
                return index + 1 # account for the (none) option
            
            return 0

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append((rs.c.Notifier.BIND_MAP_UI, ''))
        return notifiers

    # -------- Private methods
    
    def _getBindLocator(self):
        blocIdent = self.getArgumentValue(self.ARG_BIND_LOCATOR)
        if not blocIdent:
            return None
        try:
            modoItem = modox.SceneUtils.findItemFast(blocIdent)
        except LookupError:
            return None
        
        try:
            return rs.BindLocatorItem(modoItem)
        except TypeError:
            pass
        return None

    def _getBindMesh(self):
        meshIdent = self.getArgumentValue(self.ARG_MESH)
        if not meshIdent:
            return None
        try:
            modoItem = modox.SceneUtils.findItemFast(meshIdent)
        except LookupError:
            return None
        
        try:
            return rs.BindMeshItem(modoItem)
        except TypeError:
            pass
        return None
    
    def _getWeightMapNames(self, meshModoItem):
        # There is a bug in td sdk such that a mesh cannot be accessed with read access
        # when we're in setup. It only allows for read access when out of setup.
        # This is bug in MeshProvider.
        # This is why this method needs to go via raw sdk.
        rawMeshItem = meshModoItem.internalItem
        scene = rawMeshItem.Context()
    
        # Get read only mesh from channel
        chanRead = scene.Channels(lx.symbol.s_ACTIONLAYER_EDIT, 0.0)
        readMeshObj = chanRead.ValueObj(rawMeshItem, rawMeshItem.ChannelLookup(lx.symbol.sICHAN_MESH_MESH))
        mesh = lx.object.Mesh(readMeshObj)
        meshMaps = lx.object.MeshMap(mesh.MeshMapAccessor())
        
        visitor = QueryWeightMapsNamesVisitor(meshMaps)
        meshMaps.Enumerate(lx.symbol.iMARK_ANY, visitor, 0)

        wmapsList = visitor.mapNames
        wmapsList.sort()
        return wmapsList
    
    def _buildPopup(self):
        """ Builds a popup that the command will present in UI.
        """
        entries = [('none', '(none)')]
        bindLoc = self._getBindLocator()
        mesh = self._getBindMesh()
        
        if bindLoc is not None and mesh is not None:
            wmapNames = self._getWeightMapNames(mesh.modoItem)
            for name in wmapNames:
                entries.append((name, name))
        return entries

rs.cmd.bless(CmdBindMapWeightToLocatorPopup, 'rs.bind.mapBindLocator')


class CmdBindMapAssignmentFCL(rs.RigCommand):
    """ Generates command list with item features.
    
    This command is used to add/remove features to rig items.
    """

    ARG_CMD_LIST = 'cmdList'
    ARG_SIDE = 'side'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        cmdList = rs.cmd.Argument(self.ARG_CMD_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFromCommandList
        cmdList.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST
        
        side = rs.cmd.Argument(self.ARG_SIDE, 'string')
        side.flags = 'optional'
        side.defaultValue = rs.c.Side.CENTER
        
        return [cmdList, side] + superArgs

    def execute(self, msg, flags):
        pass

    def query(self, argIndex):
        pass

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append((rs.c.Notifier.BIND_MAP_UI, ''))
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DATATYPE)
        return notifiers

    # -------- Private methods

    def _buildFromCommandList(self):
        """ Builds a list of features for an item.

        A feature needs to be listed and needs to past test
        on each item in selection in order to show up in properties.
        """
        side = self.getArgumentValue(self.ARG_SIDE)
        
        rig = self.firstRigToEdit
        if rig is None:
            return []
        
        bindSkeleton = rs.BindSkeleton(rig)
        bindLocators = bindSkeleton.itemsHierarchy
        
        mesh = self._getMesh()
            
        if mesh is None:
            return []
        
        bindLocatorsByModule = {}
        keyOrder = []
        
        for bloc in bindLocators:
            if bloc.side != side:
                continue
            if not bloc.isEffector:
                continue
            
            moduleRoot = bloc.moduleRootItem
            key = moduleRoot.nameAndSide
            if key not in keyOrder:
                keyOrder.append(key)

            if key in bindLocatorsByModule:
                bindLocatorsByModule[key].append(bloc)
            else:
                bindLocatorsByModule[key] = [bloc]

        commandList = []
        for moduleKey in keyOrder:
            commandList.append(modox.c.FormCommandList.DIVIDER + moduleKey)

            for bloc in bindLocatorsByModule[moduleKey]:
                commandList.append("rs.bind.mapBindLocator bindLoc:{%s} mesh:{%s} popupIndex:?" % (bloc.modoItem.id, mesh.id))

        return commandList

    def _getMesh(self):
            
        # Try selection
        selected = modo.Scene().selectedByType('mesh')
    
        for meshModoItem in selected:
            try:
                bindMesh = rs.BindMeshItem(meshModoItem)
            except TypeError:
                continue
            if not bindMesh.isBound:
                return meshModoItem
        
        return None

rs.cmd.bless(CmdBindMapAssignmentFCL, 'rs.bind.mappingFCL')