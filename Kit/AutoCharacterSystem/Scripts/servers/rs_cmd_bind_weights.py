

import lx
import lxu
import modo
import modox

import rs


class CmdBindSetWeights(rs.Command):
    """ Sets weights on a current weight map to a given value.
    
    This is simply using the adjust weights tool with proper parameters.
    It's not rigging system specific command really, can be regular MODO extension.
    
    Note that this command works properly only when weight map is selected
    by selecting the effector driving influence or the influence item that is using
    the weight map.
    """

    ARG_VALUE = 'value'
    ARG_NORMALIZE = 'normalize'
    ARG_ADDITIVE = 'additive'

    _ICON_BASE_NAME_SET = "rs.weights.set"
    _ICON_BASE_NAME_ADD = "rs.weights.add"
    _ICON_BASE_NAME_SUB = "rs.weights.sub"

    def cmd_Icon(self):
        val = self.getArgumentValue(self.ARG_VALUE)

        if self.getArgumentValue(self.ARG_ADDITIVE):
            basename = self._ICON_BASE_NAME_ADD
            if self.getArgumentValue(self.ARG_VALUE) < 0.0:
                basename = self._ICON_BASE_NAME_SUB
            intval = int(abs(val) * 1000.0)
        else:
            basename = self._ICON_BASE_NAME_SET
            intval = int(val * 100.0)

        return basename + str(intval)
        
    def enable(self, msg):
        return True

    def basic_ButtonName(self):
        v = self.getArgumentValue(self.ARG_VALUE)
        v = int(v * 100.0)

        additive = self.getArgumentValue(self.ARG_ADDITIVE)
        key = 'setWeights'
        if additive:
            if v >= 0:
                key = 'incWeights'
            else:
                v = abs(v)
                key = 'decWeights'

        button = modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)
        return button + ' ' + str(v) + '%'

    def arguments(self):      
        valueArg = rs.cmd.Argument(self.ARG_VALUE, 'float')
        valueArg.defaultValue = 1.0
    
        normalizeArg = rs.cmd.Argument(self.ARG_NORMALIZE, 'boolean')
        normalizeArg.flags = ['optional']
        normalizeArg.defaultValue = True

        additiveArg = rs.cmd.Argument(self.ARG_ADDITIVE, 'boolean')
        additiveArg.flags = ['optional']
        additiveArg.defaultValue = False

        return [valueArg, normalizeArg, additiveArg]

    def restoreItemSelection(self):
        """
        Running weight map commands is destroying item selection.
        If a vertex map is selected directly the selection will switch to the weight map.
        It feels like a bug when that happens so we force restore selection here
        so weight map selection via joint items overrides any direct selection.
        """
        return True

    def execute(self, msg, flags):
        weight = self.getArgumentValue(self.ARG_VALUE)
        normalize = self.getArgumentValue(self.ARG_NORMALIZE)
        additive = self.getArgumentValue(self.ARG_ADDITIVE)

        lx.eval('tool.set WeightSelectAndGo on')
        toolAdditive = lx.eval('tool.attr vertMap.setWeight additive ?')
        toolNormalize = bool(lx.eval('tool.attr vertMap.setWeight normalize ?'))
        #toolWeight = lx.eval('tool.attr vertMap.setWeight weight ?')
        
        revertNormalize = False
        
        if additive:
            lx.eval('tool.attr vertMap.setWeight additive true')
        else:
            lx.eval('tool.attr vertMap.setWeight additive false')
            
        if toolNormalize != normalize:
            lx.eval('tool.attr vertMap.setWeight normalize %d' % int(normalize))
            revertNormalize = True

        lx.eval('tool.setAttr vertMap.setWeight weight %f' % weight)
        lx.eval('tool.noChange')
        lx.eval('tool.doApply')
        
        if toolAdditive != additive:
            lx.eval('tool.attr vertMap.setWeight additive %d' % int(toolAdditive))
            
        if revertNormalize:
            lx.eval('tool.attr vertMap.setWeight normalize %d' % int(toolNormalize))

        lx.eval('tool.set WeightSelectAndGo off')

        # If value was set to 0 in non-additive more - cull values close to 0
        if not additive:
            rs.run('rs.bind.runVMapCmd {vertMap.cull 0.001 false}')

rs.cmd.bless(CmdBindSetWeights, "rs.bind.setWeights")


class SelectMapFromMeshMode(object):
    AUTO = 0
    VIEW = 1
    SELECTION = 2


class CmdBindSelectNextWeightMap(rs.Command):
    """ Selects weight map either from selection or from under the mouse.
    """

    ARG_MODE = 'mode'
    ARG_DIRECTION = 'direction'

    Mode = SelectMapFromMeshMode
    
    MODE_HINTS = (
        (Mode.AUTO, 'auto'),
        (Mode.VIEW, 'view'),
        (Mode.SELECTION, 'selection')
    )
    
    DIRECTION_HINTS = (
        (-1, 'prev'),
        (1, 'next'),
        (2, 'all')
    )
    
    def arguments(self):
        modeArg = rs.cmd.Argument(self.ARG_MODE, 'integer')
        modeArg.defaultValue = 0
        modeArg.flags = 'optional'
        modeArg.hints = self.MODE_HINTS

        dirArg = rs.cmd.Argument(self.ARG_DIRECTION, 'integer')
        dirArg.defaultValue = 2
        dirArg.flags = 'optional'
        dirArg.hints = self.DIRECTION_HINTS
        
        return [modeArg, dirArg]

    def enable(self, msg):
        return True

    def execute(self, msg, flags):
        rsScene = rs.Scene()
        editRig = rsScene.editRig
        if editRig is None:
            return

        # Pull a list of vertices to work on first.
        # List is in format (modo.Mesh, modo.meshVertex)
        verts = self._vertsToWorkFrom
        if not verts:
            return

        wmapNamesToChooseFrom, wmapStrengthByName = self._getWeightsInfluencingVertices(verts)

        # Get names of weight maps used in the current edit rig.
        bindskel = rs.BindSkeleton(editRig)
        bindlocs = bindskel.items

        rigWeightMapNames = []
        for bloc in bindlocs:
            blocwmap = bloc.weightMapName
            if blocwmap is None:
                continue
            if blocwmap not in rigWeightMapNames:
                rigWeightMapNames.append(blocwmap)
        
        # Filter weight maps list by maps that belong to the edit rig.
        # Only maps that are on both lists should be cycled through.
        filteredMaps = []
        for x in range(len(wmapNamesToChooseFrom)):
            if wmapNamesToChooseFrom[x] in rigWeightMapNames:
                filteredMaps.append(wmapNamesToChooseFrom[x])
        
        if not filteredMaps:
            return

        filteredStrength = {}
        for mapName in filteredMaps:
            filteredStrength[mapName] = wmapStrengthByName[mapName]

        strongestMapName = self._getStrongestMapName(filteredStrength)
        strongestMapIndex = filteredMaps.index(strongestMapName)

        dir = self.getArgumentValue(self.ARG_DIRECTION)
        if dir == 2: # Select all maps
            itemsToSelect = []
            for bloc in bindlocs:
                if bloc.weightMapName in filteredMaps:
                    itemsToSelect.append(bloc.modoItem)
            modo.Scene().select(itemsToSelect, add=False)

        else:
            offset = dir
            # see which weight map is currently selected.
            # we do this by checking if bind skeleton joint or a deformer driven by a joint is selected.
            selectedBindLocator = self._getSelectedBindLocator()
            if selectedBindLocator is None: # no weight map selection
                newMapIndex = strongestMapIndex
            else:
                currentWMap = selectedBindLocator.weightMapName
                if currentWMap is None: # bind loc selected but has no reference to any weightmap
                    newMapIndex = strongestMapIndex
                else:
                    try:
                        newMapIndex = filteredMaps.index(currentWMap) + offset
                    except ValueError:
                        newMapIndex = strongestMapIndex

                    if newMapIndex >= len(filteredMaps):
                        newMapIndex = 0
                    elif newMapIndex < 0:
                        newMapIndex = len(filteredMaps) - 1

            mapToSet = filteredMaps[newMapIndex]
            # Now find bind locator for the map and select it.
            for bloc in bindlocs:
                if bloc.weightMapName == mapToSet:
                    bloc.modoItem.select(replace=True)

    # -------- Private methods

    def _getWeightsInfluencingVertices(self, verts):
        """ Gets all weight maps that are influencing given vertices.

        Paramters
        ---------
        verts : list of (modo.Mesh, modo.MeshVertex)
            List of vertices that need to be scanned for influencing weight maps.

        Returns
        -------
        list(str)
            List with names of influencing weight maps
        dict(str : float)
            dictionary defining the strength of the weightmap.
            Key is name of weight map, value is the strength amount being the sum
            of influences on all vertices.
        """
        # Lists defining weight maps that are under mouse pointer/selection
        wmapsToChooseFrom = []
        wmapNamesToChooseFrom = []
        # Dictionary that will contain strength for each weight map.
        wmapStrengthByName = {}

        # Pick the first mesh from vertices list as the one that we want to work on.
        meshToRead = verts[0][0] # tyoe : modo.Mesh
        wmaps = meshToRead.geometry.vmaps.weightMaps

        # generate a list of weight maps that have values above threshold set
        # for the selected vertices
        # Also calculates strength of each map by adding weights for all the
        # vertices that we are scanning.
        for x in range(len(verts)):
            mesh = verts[x][0]
            vertex = verts[x][1]
            vertIndex = vertex.index

            if mesh != meshToRead:
                continue

            for wmap in wmaps:
                weight = wmap[vertIndex]
                if weight is None:
                    continue
                if weight[0] < 0.09:  # fixed threshold for now
                    continue

                if wmap.name not in wmapNamesToChooseFrom:
                    wmapsToChooseFrom.append(wmap)
                    wmapNamesToChooseFrom.append(wmap.name)

                # Be sure to add weight for each processed vertex
                # but only add it to maps that will be considered
                # for selecting.
                if wmap.name in wmapNamesToChooseFrom:
                    if wmap.name not in wmapStrengthByName:
                        wmapStrengthByName[wmap.name] = 0.0
                    wmapStrengthByName[wmap.name] += weight[0]

        return wmapNamesToChooseFrom, wmapStrengthByName

    def _getStrongestMapName(self, mapsByStrength):
        strongestMapName = None
        maxStrength = 0.0
        for key in mapsByStrength:
            if mapsByStrength[key] > maxStrength:
                maxStrength = mapsByStrength[key]
                strongestMapName = key
        return strongestMapName

    def _getSelectedBindLocator(self):
        for item in modo.Scene().selected:
            try:
                return rs.BindLocatorItem(item)
            except TypeError:
                continue
        return None

    @property
    def _vertsToWorkFrom(self):
        """ Gets a list of vertices that will be used to determine map to select.
        
        In auto mode view will be tried first, if there is no polygon under mouse
        selection will be looked at.
        Note that only current component selection will be taken into account.

        Returns
        -------
        list of (modo.Mesh, modo.MeshVertex) or None
        """
        mode = self.getArgumentValue(self.ARG_MODE)
        if mode == self.Mode.AUTO:
            verts = self._vertsUnderMouse
            if not verts:
                verts = self._vertsFromSelection
            return verts
        elif mode == self.Mode.VIEW:
            return self._vertsUnderMouse
        elif mode == self.Mode.SELECTION:
            return self._vertsFromSelection

    @property
    def _vertsUnderMouse(self):
        """ Gets vertices under mouse pointer in viewport.
        
        These will be vertices of a polygon that is under the mouse.

        Returns
        -------
        list of (modo.Mesh, modo.MeshVertex) or None
        """
        itemId = lx.eval("query view3dservice element.over ? ITEM")
        if itemId is None:
            return []
    
        scene = modo.Scene()
        item = scene.item(itemId)

        # POLY query returns a string in format:  mesh_index,polygon_index
        # So I need to parse that string to extract index integers.
        # It is also possible to get multiple polygons if you have more then one active
        # mesh or you're over an edge that belongs to 2 polygons.
        # In such case you will get a tuple of strings and polygons are ordered by depth
        # (closest one is first).
        p = lx.eval("query view3dservice element.over ? POLY")
        if p is None:
            # We're over a mesh but it's not active one so poly query returns None.
            scene.select(item)
            p = lx.eval("query view3dservice element.over ? POLY")
    
        if p is None:
            return []
    
        if not isinstance(p, tuple):
            p = [p]
        strings = p[0].split(',')
        mIndex = int(strings[0])
        pIndex = int(strings[1])
    
        meshType = lx.service.Scene().ItemTypeLookup('mesh')
        rawItem = scene.ItemByIndex(meshType, mIndex)
        mesh = modo.Mesh(rawItem)
        
        polygon = modo.MeshPolygon(pIndex, mesh.geometry)
        return [(mesh, vertex) for vertex in polygon.vertices]

    @property
    def _vertsFromSelection(self):
        return modox.SelectionUtils.currentComponentSelectionAsVertexSelection()

rs.cmd.bless(CmdBindSelectNextWeightMap, "rs.bind.nextWeightMap")


class CmdBindShiftWeights(rs.RigCommand):
    """ Shifts selected weights to strongest, weakest or average value.

    Use this to quickly even out weights on selected vertices.
    """

    ARG_MODE = 'mode'

    MODE_HINTS = ((0, "average"),
                  (1, "highest"),
                  (2, "lowest"))

    def enable(self, msg):
        return True

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        modeArg = rs.cmd.Argument(self.ARG_MODE, 'integer')
        modeArg.defaultValue = 0
        modeArg.hints = self.MODE_HINTS

        return [modeArg] + superArgs

    def restoreItemSelection(self):
        """
        Running weight map commands is destroying item selection.
        If a vertex map is selected directly the selection will switch to the weight map.
        It feels like a bug when that happens so we force restore selection here
        so weight map selection via joint items overrides any direct selection.
        """
        return True

    def execute(self, msg, flags):
        mode = self.getArgumentValue(self.ARG_MODE)

        vertMapSelection = modox.VertexMapSelection()
        vertMapSelection.store(weight=True)

        rs.run('!rs.bind.selectWeightsDirect')

        selectedVerts = modox.SelectionUtils.currentComponentSelectionAsVertexSelection()
        self._setValues(selectedVerts, mode)

        vertMapSelection.restoreByCommand()

    # -------- Private methods

    def _setValues(self, vertSelection, mode):
        if len(vertSelection) > 0:
            vmapSelection = modox.VertexMapSelection()
            sel = vmapSelection.get(lx.symbol.i_VMAP_WEIGHT)
            mesh = vertSelection[0][0] # We assume all vertices come from the same mesh for performance reasons.
            weightMaps = mesh.geometry.vmaps.weightMaps
            filteredMaps = [map for map in weightMaps if map.name in sel]

            for wmap in filteredMaps:

                lowest = 1.0
                highest = 0.0

                total = 0.0

                for v in vertSelection:
                    vertIndex = v[1].index
                    weight = wmap[vertIndex]
                    if weight is None:
                        lowest = 0.0
                        continue
                    weight = weight[0] # weight value is a vector
                    if weight < lowest:
                        lowest = weight
                    if weight > highest:
                        highest = weight
                    total += weight

                # apply here
                val = None
                if mode == 0: # average
                    val = total / len(vertSelection)
                elif mode == 1: # highest
                    val = highest
                elif mode == 2: # lowest
                    val = lowest

                if val is not None:
                    vmapSelection.setByCommand(wmap.name, lx.symbol.i_VMAP_WEIGHT, modox.SelectionMode.REPLACE)
                    rs.run('rs.bind.setWeights %f normalize:1 additive:0' % val)

rs.cmd.bless(CmdBindShiftWeights, "rs.bind.shiftWeights")