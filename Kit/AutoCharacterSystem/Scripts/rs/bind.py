

import lx
import modo
import modox

from .rig import Rig
from .log import log
from .items.bind_loc import BindLocatorItem
from .items.bind_mesh import BindMeshItem
from .bind_map import BindMap
from . import const as c

    
class VertexMapTransferMethod(object):
    RAYCAST = "raycast"
    DISTANCE = "distance"


class Bind(object):

    TransferMethod = VertexMapTransferMethod
    
    _WMAP_NAME_COMPONENTS = [c.NameToken.MODULE_NAME, c.NameToken.SIDE, c.NameToken.BASE_NAME]
       
    def setFromModoBind(self, modoBind, skipUnusedDeformers=True):
        """ Applies existing standard bind setup back to rig.
        
        Do this after running modo's bind command.
        """
        skeleton = modoBind.shadowSkeleton.skeleton

        bindMeshes = []

        for locShadow in skeleton:
            # shadow influence is general influence set up by MODO during default bind.
            shadowInfluence = self._getEffectorGeneralInfluence(locShadow.modoItem)
            if shadowInfluence is None:
                continue
            
            # if it has check if its source bind locator has one.
            bindLoc = locShadow.sourceBindLocator
            rigInfluence = self._getEffectorGeneralInfluence(bindLoc.modoItem)
            if not rigInfluence:
                continue

            meshes = shadowInfluence.meshes

            # Need to add shadow influence mesh to the list
            # of bind meshes if it's not on it already.
            # It's excessive because most likely there will be the same
            # mesh on every joint but maybe it's a bit more future proof this way.
            for meshModoItem in meshes:
                if meshModoItem not in bindMeshes:
                    bindMeshes.append(meshModoItem)

            mapNameToCopy = shadowInfluence.mapName
            weightContainers = rigInfluence.weightContainers
            
            # Before copying weights a mesh that was bound (or multiple meshes)
            # need to be plugged into rig deformers.
            # We have to make it work with and without weight containers setup.
            # Test if the influence has containers first.
            # If it has - we will plug mesh into weight container rather then
            # into the influence directly.

            if weightContainers:
                mapNameToSet = "__item_" + weightContainers[0].id
            else:
                mapNameToSet = bindLoc.renderNameFromTokens(self._WMAP_NAME_COMPONENTS)
                
            for meshItem in meshes:
                mesh = modo.Mesh(meshItem)
                mesh.select(replace=True)
                
                # Do not connect a deformer if its weight map is empty.
                if skipUnusedDeformers:
                    # Need to select weight map for now because the rs.vertexMap.empty command
                    # works off currently selecte map - its arguments are not implmeented yet.
                    lx.eval('select.vertexMap {%s} wght replace' % mapNameToCopy)
                    isEmpty = lx.eval('rs.vertexMap.empty ? type:wght name:{%s}' % mapNameToCopy)
                    if isEmpty:
                        continue
                
                if weightContainers:
                    for modoItem in weightContainers:
                        modox.WeightContainer(modoItem).meshes = meshItem
                else:
                    rigInfluence.meshes = meshItem
                    
                geo = mesh.geometry
                if not geo.vmaps[mapNameToSet]: # This returns empty list if vertex map is not on the item.
                    geo.vmaps.addWeightMap(mapNameToSet)
                    geo.setMeshEdits()
                else:
                    # if map is already there we have to clear it first.
                    lx.eval('!vertMap.clearByName type:wght name:{%s}' % mapNameToSet)
                
                lx.eval('!vertMap.copyByName type:wght name:{%s}' % mapNameToCopy)
                lx.eval('!vertMap.pasteByName type:wght name:{%s}' % mapNameToSet)
        
            # Copy weight map name to the rig's influence as well and set its
            # effect to weight map.
            if not weightContainers:
                rigInfluence.influenceType = rigInfluence.InfluenceType.WEIGHT_MAP
                rigInfluence.mapName = mapNameToSet

        # Set all meshes as bound
        for meshModoItem in bindMeshes:
            try:
                BindMeshItem(meshModoItem).isBound = True
            except TypeError:
                continue

        # Last processed modo bind weight map will be selected at this point.
        # Make sure to clear vertex map selection here so it's not hanging selected.
        # This should ideally only clear selection of weight maps but there's currently
        # no way to do that, all vertex map selection has to be cleared.
        modox.VertexMapSelection().clear()

    def fromMap(self, bindMesh):
        """
        Binds mesh from map.

        Parameters
        ----------
        bindMesh : BindMeshItem
        """
        bindLocModoItems = self._rig[c.ElementSetType.BIND_SKELETON].elements
        bindMap = bindMesh.bindMap.get()

        # Disconnect all deformers from bind mesh and set up new ones.
        modox.DeformedItem(bindMesh.modoItem).disconnectDeformers()

        for modoItem in bindLocModoItems:
            try:
                bindLocator = BindLocatorItem(modoItem)
            except TypeError:
                continue
            if not bindLocator.isEffector:
                continue

            blocKey = bindLocator.renderNameFromTokens(
                [c.NameToken.SIDE, c.NameToken.MODULE_NAME, c.NameToken.BASE_NAME])
            try:
                wmapName = bindMap[blocKey]
            except KeyError:
                wmapName = None

            if wmapName is not None:
                self.bindMeshToEffector(bindMesh, bindLocator, wmapName)

        bindMesh.isBound = True

    def transfer(self,
                 bindMeshFrom,
                 bindMeshTo,
                 method=VertexMapTransferMethod.DISTANCE,
                 skipUnusedDeformers=True,
                 monitor=None,
                 ticks=0):
        """ Transfers bind between two bind meshes.

        Parameters
        ----------
        bindMeshFrom : BindMeshItem

        bindMeshTo : BindMeshItem
        """
        # Need to plug all deformers of mesh from to mesh to.
        deformerModoItems = bindMeshFrom.deformerModoItems
        if not deformerModoItems:
            log.out("No bind to transfer from.", log.MSG_ERROR)
            return
        
        modox.DeformedItem(bindMeshTo.modoItem).setDeformers(deformerModoItems, replace=True)
        wmapsWithDeformers = self._getWeightMapsWithDeformers(deformerModoItems)
        wmapsList = list(wmapsWithDeformers.keys())

        if monitor is not None:
            steps = len(wmapsList) + 4
            tick = float(ticks) / float(steps)
        
        with modo.Mesh(bindMeshTo.modoItem).geometry as geo:
            for wmapName in wmapsList:
                if not geo.vmaps[wmapName]: # This returns empty list if vertex map is not on the item.
                    geo.vmaps.addWeightMap(wmapName)
            geo.setMeshEdits()
        
        if monitor:
            monitor.tick(tick * 2.0)
        
        # Select mesh from first, then override it with mesh to.
        # I think this puts the meshTo as active (foreground) mesh and puts
        # meshFrom as background mesh.
        # Seems to work correctly with the transfer weights command.
        bindMeshFrom.modoItem.select(replace=True)
        bindMeshTo.modoItem.select(replace=True)

        for wmapName in wmapsList:
            # Select weight map to which data will be transfered.
            lx.eval('select.vertexMap %s wght replace' % wmapName)
            lx.eval('vertMap.transfer {%s} weight local %s off true' % (wmapName, method))
            if monitor:
                monitor.tick(tick)

        # Make sure to set bind mesh as bound
        bindMeshTo.isBound = True

        # Optimize unused deformers.
        if skipUnusedDeformers:
            self.disconnectDeformersWithNoInfluence(bindMeshTo)

        modox.VertexMapSelection().clear()

        monitor.tick(tick * 2.0)

    def copy(self,
             bindMeshFrom,
             bindMeshTo,
             skipUnusedDeformers=True,
             monitor=None,
             ticks=0):
        """
        Copies bind setup from one mesh to another.

        This simply has to get all the deformers from one mesh and plug to another.
        Before plugging deformer weight map has to be tested for whether it's empty (or it exists)
        on a target mesh. If it doesn't exist or is empty - this deformer does not need to be plugged.
        """
        deformerModoItems = bindMeshFrom.deformerModoItems
        if not deformerModoItems:
            log.out("No bind to copy from.", log.MSG_ERROR)
            return

        # Copy all deformer links first.
        targetDeformedItem = modox.DeformedItem(bindMeshTo.modoItem)
        targetDeformedItem.setDeformers(deformerModoItems, replace=True)

        # Now we're going to check against non-existent maps.
        # If a map doesn't exist on a target mesh - we have to disconnect deformer.
        wmapsWithDeformers = self._getWeightMapsWithDeformers(deformerModoItems)
        wmapsList = list(wmapsWithDeformers.keys())

        if monitor is not None:
            steps = len(wmapsList) + 4
            tick = float(ticks) / float(steps)

        with modo.Mesh(bindMeshTo.modoItem).geometry as geo:
            for wmapName in wmapsList:
                if not geo.vmaps[wmapName]:  # This returns empty list if vertex map is not on the item.
                    targetDeformedItem.disconnectDeformers(wmapsWithDeformers[wmapName])

                if monitor:
                    monitor.tick(tick)

        # Make sure to set bind mesh as bound
        bindMeshTo.isBound = True

        # Optimize unused deformers by testing if any of existing maps are empty.
        if skipUnusedDeformers:
            self.disconnectDeformersWithNoInfluence(bindMeshTo)

        monitor.tick(tick * 4.0)

    def disconnectDeformersWithNoInfluence(self, bindMeshItem):
        """
        Disconnects deformers that have no influence over the mesh (their weight maps are empty).

        Parameters
        ----------
        bindMeshItem : BindMeshItem

        Returns
        -------
        int
            Number of disconnected deformers.
        """
        deformerModoItems = bindMeshItem.deformerModoItems
        if not deformerModoItems:
            return

        wmapsWithDeformers = self._getWeightMapsWithDeformers(deformerModoItems)
        wmapsList = list(wmapsWithDeformers.keys())

        deformed = modox.DeformedItem(bindMeshItem.modoItem)
        bindMeshItem.modoItem.select(replace=True)

        count = 0

        for wmapName in wmapsList:
            # Need to select weight map for now because the rs.vertexMap.empty command
            # works off currently selecte map - its arguments are not implmeented yet.
            lx.eval('select.vertexMap {%s} wght replace' % wmapName)
            isEmpty = lx.eval('rs.vertexMap.empty ? type:wght name:{%s}' % wmapName)
            if isEmpty:
                deformers = wmapsWithDeformers[wmapName]
                deformed.disconnectDeformers(deformers)
                count += len(deformers)

        return count

    def embedMap(self, bindMesh):
        """ Embeds bind map into mesh.
        
        This should be done on a bound map only!
        
        Parameters
        ----------
        bindMesh : BindMeshItem
        """
        bindMap = BindMap(bindMesh)
        bindMap.clear()
        
        bindLocModoItems = self._rig[c.ElementSetType.BIND_SKELETON].elements
        for modoItem in bindLocModoItems:
            try:
                bloc = BindLocatorItem(modoItem)
            except TypeError:
                continue
            mapName = bloc.weightMapName
            if mapName is not None:
                bindMap.setMapping(bloc, mapName)
        
    def unbind(self, bindMesh, backupWeights=True, effectors=None):
        """ Unbinds mesh from the rig.
        
        Parameters
        ----------
        bindMesh : BindMeshItem
        
        backupWeights : bool
            When False weight containers will be cleared, directly used
            weight maps will be deleted.
            When True values in weight containers will be copied to weight maps
            before weight containers are cleared. Directly used weight maps
            will be left intact.
        """
        deformedItem = modox.DeformedItem(bindMesh.modoItem)
        deformerModoItems = deformedItem.deformers
        
        # key is name of the target map, value is the name of the source map.
        mapsToCopy = {}
        # list of maps that should be deleted.
        mapsToDelete = []
        
        for modoItem in deformerModoItems:
            deformer = modox.Deformer(modoItem)
            weightContainers = deformer.weightContainers
            if weightContainers:
                for modoItem in weightContainers:
                    weightContainer = modox.WeightContainer(modoItem)
                    containerMapName = weightContainer.weightMapName
 
                    mapsToDelete.append(containerMapName)
                    
                    if backupWeights:
                        bindLocModoItem = deformer.effector
                        try:
                            bindLoc = BindLocatorItem(bindLocModoItem)
                        except TypeError:
                            pass
                        else:
                            mapNameToCopy = bindLoc.renderNameFromTokens(self._WMAP_NAME_COMPONENTS)
                            mapsToCopy[mapNameToCopy] = containerMapName
            else:
                if not backupWeights:
                    mapName = deformer.mapName
                    if mapName:
                        mapsToDelete.append(mapName)

        bindMesh.modoItem.select(replace=True)
        
        if mapsToCopy:
            mapsToClear = []
            # Add any maps that are not there yet.
            with modo.Mesh(bindMesh.modoItem).geometry as geo:
                for wmapName in list(mapsToCopy.keys()):
                    if not geo.vmaps[wmapName]: # This returns empty list if vertex map is not on the item.
                        geo.vmaps.addWeightMap(wmapName)
                    else:
                        mapsToClear.append(wmapName)
                geo.setMeshEdits()
            
            for wmapName in mapsToClear:
                lx.eval('!vertMap.clearByName type:wght name:{%s}' % wmapName)
                
            for wmapName in list(mapsToCopy.keys()):
                lx.eval('!vertMap.copyByName type:wght name:{%s}' % mapsToCopy[wmapName])
                lx.eval('!vertMap.pasteByName type:wght name:{%s}' % wmapName)

        if mapsToDelete:
            for wmapName in mapsToDelete:
                lx.eval('!vertMap.deleteByName type:wght name:{%s}' % wmapName)
                
        deformedItem.disconnectDeformers()

        # Make sure to unbind the mesh connection link
        bindMesh.isBound = False

    def bindMeshToEffector(self, bindMesh, bindLocator, weightMapName):
        """ Sets up binding between given mesh and a bind locator effector.

        Note that this methods has to select the bind mesh in the scene
        if the binding is set up via weight container.
        """
        eff = modox.Effector(bindLocator.modoItem)
        if not eff.isEffector:
            return
        
        deformers = eff.deformers
        if not deformers:
            return
        
        # We just take first deformer.
        # This is something to consider for future, do I need to make it work with multiple deformers?
        deformer = modox.Deformer(deformers[0])
        deformerModoItem = deformers[0]
        weightContainers = deformer.weightContainers
        
        # Before copying weights a mesh that was bound (or multiple meshes)
        # need to be plugged into rig deformers.
        # We have to make it work with and without weight containers setup.
        # Test if the influence has containers first.
        # If it has - we will plug mesh into weight container rather then
        # into the influence directly.

        if weightContainers:
            bindMesh.modoItem.select(replace=True)

            weightContainer = modox.WeightContainer(weightContainers[0])
            mapNameToSet = weightContainer.weightMapName

            mesh = modo.Mesh(bindMesh.modoItem)
            geo = mesh.geometry
            if not geo.vmaps[mapNameToSet]: # This returns empty list if vertex map is not on the item.
                geo.vmaps.addWeightMap(mapNameToSet)
                geo.setMeshEdits()
            else:
                # if map is already there we have to clear it first.
                lx.eval('!vertMap.clearByName type:wght name:{%s}' % mapNameToSet)
            
            lx.eval('!vertMap.copyByName type:wght name:{%s}' % weightMapName)
            lx.eval('!vertMap.pasteByName type:wght name:{%s}' % mapNameToSet)

            weightContainer.meshes = bindMesh.modoItem

        else:
            try:
                genInf = modox.GeneralInfluence(deformerModoItem)
            except TypeError:
                pass
            else:
                genInf.meshes = bindMesh.modoItem
                genInf.influenceType = modox.GeneralInfluence.InfluenceType.WEIGHT_MAP
                genInf.mapName = weightMapName

    # -------- Private methods

    def _getWeightMapsWithDeformers(self, deformerModoItems):
        """ Gets a dictionary of weight map names and deformers for set of deformer items.
        
        Returns
        -------
        dict {str : list of modo.Item}
            Keys are weight map names, values are deformers using these weight maps.
        """
        weightsWithDeformers = {}
        
        for modoItem in deformerModoItems:
            deformer = modox.Deformer(modoItem)
            for mapName in deformer.weightMapNames:
                if mapName not in weightsWithDeformers:
                    weightsWithDeformers[mapName] = [modoItem]
                else:
                    weightsWithDeformers[mapName].append(modoItem)
        return weightsWithDeformers
        
    def _getEffectorGeneralInfluence(self, modoItem):
        eff = modox.Effector(modoItem)
        genInfs = eff.generalInfluences
        if not genInfs:
            return None
        return modox.GeneralInfluence(genInfs[0])

    def __init__(self, rig):
        if not isinstance(rig, Rig):
            try:
                rig = Rig(rig)
            except TypeError:
                raise
        
        self._rig = rig
    