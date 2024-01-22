

import lx
import lxu
import modo
import modox

import rs


class CmdBindReuse(rs.RigCommand):
    """ Experimental command for using existing weights for binding.
    
    This command calculates center point for each weight map and then
    tries to find closest bind skeleton joint.
    """
    
    VISUALISE = False

    def init(self):
        self._vertPositions = []

    def enable(self, msg):
        return True

    def setup(self):
        return True

    def execute(self, msg, flags):
        scene = modo.Scene()
        mesh = self._mesh
        if mesh is None:
            return
        
        editRig = self.firstRigToEdit
        bindSkel = rs.BindSkeleton(editRig)
        
        self._cacheVertPositions(mesh.modoItem)
        
        threshold = 0.3
        
        weightMaps = mesh.modoItem.geometry.vmaps.weightMaps
        bindMap = mesh.bindMap
        
        for wmap in weightMaps:
        
            mapCenter = modo.Vector3()
            vcount = 0
        
            for index, weight in enumerate(wmap):
                if weight is None: # None is no weight value assigned
                    continue
                if weight[0] > threshold: # weight is a vector, really
                    vcount += 1
                    mapCenter += self._vertPositions[index]
        
            if vcount > 0:
                mapCenter /= vcount
                
                if self.VISUALISE:
                    item = scene.addItem('locator', wmap.name)
                    loc = modo.LocatorSuperType(item)
                    loc.position.set(mapCenter.values)

                closestBindLocator = bindSkel.getJointClosestToPoint(mapCenter)
                bindMap.setMapping(closestBindLocator, wmap.name)

        rs.service.notify(rs.c.Notifier.BIND_MAP_UI, lx.symbol.fCMDNOTIFY_DATATYPE)

    def _cacheVertPositions(self, mesh):
        self._vertPositions = []
        
        for vertex in mesh.geometry.vertices:
            self._vertPositions.append(modo.Vector3(vertex.position))

    @property
    def _mesh(self):
        for mesh in modo.Scene().selectedByType('mesh'):
            try:
                bmesh = rs.BindMeshItem(mesh)
            except TypeError:
                continue
            if not bmesh.isBound:
                return bmesh
        return None

rs.cmd.bless(CmdBindReuse, 'rs.bind.fromMesh')