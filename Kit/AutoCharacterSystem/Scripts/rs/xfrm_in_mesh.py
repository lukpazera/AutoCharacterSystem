

import json

import lx
import lxu
import modo
import modox

from . import const as c
from .log import log


class EmbedPositionSource(object):
    AXIS_X = 0
    AXIS_Y = 1
    AXIS_Z = 2
    CLOSEST = 3


class HitType(object):
    RAYCAST = 'ray'
    CLOSEST = 'cst'


class HitDataPack(object):
    type = HitType.CLOSEST
    identifier = ''
    hitPoint = modo.Vector3()
    polygonIndex = -1
    triangleIndex = -1
    baryCoords = modo.Vector3()
    coefficient = 0.0 # t for linear interpo in raycast and distance/polygon area in closest.
    
    
class TransformsInMesh(object):
    """ Allows for embeding transform into meshes.
    
    NOTE: This code works properly only on polygonal mesh!!!
    
    Parameters
    ----------
    meshModoItems : modo.Mesh
    """
    
    TAG = 'RSGD'
    TAG_ID = lxu.utils.lxID4(TAG)
    
    def clearEmbeddedData(self):
        """ Clears all the embedded data from mesh.
        """
        with self._mesh.geometry as geo:
            for polygon in geo.polygons:
                try:
                    val = polygon.getTag(self.TAG_ID)
                except LookupError:
                    continue
    
                polygon.setTag(self.TAG_ID, None)
        
    def embedItemPosition(self, modoItem, identifier, positionSource=EmbedPositionSource.AXIS_X):
        """ Embeds given modo item's position into the mesh.
        
        Parameters
        ----------
        modoItem : modo.Item
            Item to embed.
            
        identifier : str
            Identifier under which data will be embedded.
        
        positionSource : int
            one of EmbedPositionSource.XXX
            Tells which axis to use for raycasting or if closest method should be used.

        Returns
        -------
        bool
            True if embedding was successfull, False otherwise.
        """
        xfrm = modox.LocatorUtils.getItemWorldTransform(modoItem)
        pos = modo.Vector3(xfrm.position)
        rot = modo.Matrix3(xfrm)
        
        if positionSource == EmbedPositionSource.CLOSEST:
            self._storeHitByClosest(identifier, pos, rot)
        else:
            axis = positionSource # This is based on fact that position source 0,1,2 is the same as axis constant.
            # Prepare rays for casting towards outisde of the mesh.
            rayDir = modo.Vector3(rot.m[axis])
            rayDirOpposite = modo.Vector3(rayDir)
            rayDirOpposite *= -1.0
    
            with self._mesh.geometry as geo:
                try:
                    hitData = self._calculateHit(geo, pos, rayDir)
                except ValueError:
                    return False
                
                try:
                    oppositeHitData = self._calculateHit(geo, pos, rayDirOpposite)
                except ValueError:
                    return False
            
                # Calculate where on the line between first and second hit point given position is.
                AB = hitData.hitPoint - oppositeHitData.hitPoint
                AP = pos - oppositeHitData.hitPoint
                
                t = AP.length() / AB.length()
                
                hitData.coefficient = t
                oppositeHitData.coefficient = None
                
                hitData.identifier = identifier
                oppositeHitData.identifier = identifier
                
                self._storeTag(geo, hitData)
                self._storeTag(geo, oppositeHitData)
            
        return True

    def _storeHitByClosest(self, identifier, pos, rot):
        """ Does Closest hit and stores hit data to tag.
        """
        with self._mesh.geometry as geo:
            try:
                hitData = self._calculateHitByClosest(geo, pos)
            except ValueError:
                return False
            
            hitData.identifier = identifier
            
            self._storeTag(geo, hitData)
        
    def embedOrientation(self, modoItem):
        pass
    
    def readEmbeddedTransforms(self, itemsToSet):
        """ Reads transforms embedded in mesh and applies them to items from given set.
        
        Parameters
        ----------
        itemsToSet : OrderedDict
            key is item identifier as it is within the mesh.
            value is the modo item itself.
        """
        with self._mesh.geometry as geo:
            points = {}
            for polygon in geo.polygons:
                try:
                    val = polygon.getTag(self.TAG_ID)
                except LookupError:
                    continue
    
                valuesList = json.loads(val)
                for hitd in valuesList:
                    #hitd = 
                    if hitd['id'] not in points:
                        points[hitd['id']] = []
                        
                    points[hitd['id']].append(hitd)
    
            scene = modo.Scene()
    
            log.out('----------')
            # Items need to be processed in hierarchical order.
            for key in list(itemsToSet.keys()):
                targetItem = itemsToSet[key]
    
                log.out('Reading embedded position: %s' % key)
                
                if key not in points:
                    log.out('This item does not have data embedded')
                    continue
                
                raycastRecords = []
                closestRecords = []
                
                for record in points[key]:
                    if record['tp'] == HitType.RAYCAST:
                        raycastRecords.append(record)
                    elif record['tp'] == HitType.CLOSEST:
                        closestRecords.append(record)
                
                if raycastRecords:
                    self._applyRaycastRecord(geo, targetItem, raycastRecords)
                elif closestRecords:
                    self._applyClosestRecord(geo, targetItem, closestRecords)
    
    def _applyClosestRecord(self, geo, targetItem, closestRecords):
        """ Applies closest records to a given item.
        """
        points = []
        for r in closestRecords:
            P = self._getPointPositionFromTriangle(geo, r['pix'], r['tix'], r['coords'])
            if P is None:
                continue
            
            # Offset the point along polygon normal by distance T multiplied by polygon area.
            polygon = modo.MeshPolygon(r['pix'], geo)
            n = polygon.normal
            O = modo.Vector3(n[0], n[1], n[2]) * r['t'] * polygon.area
            points.append(P + O)
        
        P = modo.Vector3()
        for point in points:
            P = P + point
        
        # Add all points from all records together.
        P = P * (1.0 / float(len(points)))
        
        log.out('applying point from closest at: %s' % str(P.values))
    
        targetItem.select(replace=True)
        lx.eval('item.setPosition x:%f y:%f z:%f mode:world' % (P.values[0], P.values[1], P.values[2]))
        
    def _applyRaycastRecord(self, geo, targetItem, raycastRecords):
        """
        Parameters:
        """
        # Forced raycast compatibility.
        if len(raycastRecords) != 2:
            log.out('Bad polygon set entry')
            return
        
        data = raycastRecords[0]
        if data['t'] is None:
            primary = raycastRecords[0]
            secondary = raycastRecords[1]
        else:
            primary = raycastRecords[1]
            secondary = raycastRecords[0]
        
        # POINT FROM
        PA = self._getPointPositionFromTriangle(geo, primary['pix'], primary['tix'], primary['coords'])

        # POINT TO
        PB = self._getPointPositionFromTriangle(geo, secondary['pix'], secondary['tix'], secondary['coords'])
    
        # Get t
        t = secondary['t']

        P = PA + ((PB - PA) * t)

        log.out('applying point at: %s' % str(P.values))

        targetItem.select(replace=True)
        lx.eval('item.setPosition x:%f y:%f z:%f mode:world' % (P.values[0], P.values[1], P.values[2]))

    def _getPointPositionFromTriangle(self, geo, polygonIndex, triangleIndex, barycoords):
        """ Gets a position for a point from data coming from a mesh.
        
        Parameters
        ----------
        geo : modo.Geometry
        
        polygonIndex : int
        
        triangleIndex : int
        
        barycoords : tuple, list
            Barycentric coordinates to calculate point position from.
            
        Returns
        -------
        modo.Vector3, None
        """
        polygon = modo.MeshPolygon(polygonIndex, geo)
        triangles = polygon.triangles
        if triangleIndex >= len(triangles):
            return None
        verts = triangles[triangleIndex]
        
        vert = modo.MeshVertex(verts[0], geo)
        P0 = modo.Vector3(vert.position)
        vert = modo.MeshVertex(verts[1], geo)
        P1 = modo.Vector3(vert.position)
        vert = modo.MeshVertex(verts[2], geo)
        P2 = modo.Vector3(vert.position)

        P = P0 * barycoords[0] + P1 * barycoords[1] + P2 * barycoords[2]
        return P

    # -------- Private methods
    
    def _storeTag(self, geo, hitData):
        """ Stores given hit data as polygon tag.
        
        This methods needs to append to existing tag as it's possible that
        multiple hit data records are on the same polygon.
        
        
        Parameters
        ----------
        geo : modo.Mesh.geometry
        
        hitData : HitData
        """
        polygon = modo.MeshPolygon(hitData.polygonIndex, geo)
        
        values = {}
        
        values['tp'] = hitData.type
        values['id'] = hitData.identifier
        values['coords'] = hitData.baryCoords
        values['pix'] = hitData.polygonIndex
        values['tix'] = hitData.triangleIndex
        values['t'] = hitData.coefficient
    
        log.out(str(values))

        try:
            rawTagVal = polygon.getTag(self.TAG_ID)
            val = json.loads(rawTagVal)
        except LookupError:
            val = None
            
        if val is None:
            val = [values]
        else:
            val.append(values)
        polygon.setTag(self.TAG_ID, json.dumps(val))
    
    def _calculateHitByClosest(self, geo, pos):
        """ Performs closest hit and returns hit data pack.
        
        Returns
        -------
        HitDataPack
        
        Raises
        ------
        ValueError
            If hit was not successfull.
        """
        polygons = geo.polygons
        rawPolygons = polygons.accessor
        
        hitData = HitDataPack()
        hitData.type = HitType.CLOSEST
        hitResult, hitPos, normal, dist = rawPolygons.Closest(0, pos.values)

        if not hitResult:
            lx.out('No closest hit.')
            raise ValueError
        
        hitPoint = modo.Vector3(hitPos)

        hitPolyIndex = rawPolygons.Index()
        polygon = modo.MeshPolygon(hitPolyIndex, geo)

        try:
            triangleIndex, baryCoords = self._calculateHitTriangleAndCoordinates(geo, polygon, hitPoint)
        except ValueError:
            raise

        hitData.hitPoint = hitPoint
        hitData.polygonIndex = hitPolyIndex
        hitData.triangleIndex =triangleIndex
        hitData.baryCoords = baryCoords
        hitData.coefficient = dist / rawPolygons.Area()
    
        # debug
        #loc = modo.Scene().addItem('locator', 'HitPoint')
        #loc.position.x.set(hitData.hitPoint.x)
        #loc.position.y.set(hitData.hitPoint.y)
        #loc.position.z.set(hitData.hitPoint.z)
        
        #target = hitData.hitPoint + (modo.Vector3(normal) * dist)
        #loc = modo.Scene().addItem('locator', 'Hit Target')
        #loc.position.x.set(target.x)
        #loc.position.y.set(target.y)
        #loc.position.z.set(target.z)
        
        hitData.hitPoint
        
        return hitData

    def _calculateHit(self, geo, pos, rayDir):
        """ Calculates coordinates.
        
        Parameters
        ----------
        pos : modo.Vector3
        
        rayDir : modo.Vector3
        
        Returns
        -------
        HitDataPack
        
        Raises
        ------
        ValueError
            If hit was not successfull.
        """
        polygons = geo.polygons
        rawPolygons = polygons.accessor
        
        hitData = HitDataPack()
        hitData.type = HitType.RAYCAST
        hitResult, normal, dist = rawPolygons.IntersectRay(pos.values, rayDir.values)
 
        if not hitResult:
            lx.out('Cannot embed the point')
            raise ValueError
        
        hitPoint = pos + (rayDir * dist)

        hitPolyIndex = rawPolygons.Index()
        polygon = modo.MeshPolygon(hitPolyIndex, geo)

        try:
            triangleIndex, baryCoords = self._calculateHitTriangleAndCoordinates(geo, polygon, hitPoint)
        except ValueError:
            raise
            
        hitData.hitPoint = hitPoint
        hitData.polygonIndex = hitPolyIndex
        hitData.triangleIndex =triangleIndex
        hitData.baryCoords = baryCoords
        
        return hitData

    def _calculateHitTriangleAndCoordinates(self, geo, polygon, hitPoint):
        """ Calculates barycentric coordinates of a point on a polygon.
        
        Parameters
        ----------
        polygon : modo.MeshPolygon
        
        Returns
        -------
        triangle Index : int
        baryCoods : tuple of 3 floats
        """
        # Find triangle which was hit by the ray.
        # This is done using barycentric coords.
        triangles = polygon.triangles
        baryCoords = None
        triangleIndex = -1
        for x in range(len(triangles)):
            triangle = triangles[x]

            ix = triangle[0]
            vert = modo.MeshVertex(ix, geo)
            P0 = modo.Vector3(vert.position)
            
            ix = triangle[1]
            vert = modo.MeshVertex(ix, geo)
            P1 = modo.Vector3(vert.position)

            ix = triangle[2]
            vert = modo.MeshVertex(ix, geo)
            P2 = modo.Vector3(vert.position)
                        
            u, v, w = self._barycentricCoordinates(P0, P1, P2, hitPoint)
            
            # This is the triangle
            if (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0 and 0.0 <= w <= 1.0):
                baryCoords = (u, v, w)
                triangleIndex = x
                return triangleIndex, baryCoords
        
        raise ValueError

    def _barycentricCoordinates(self, P0, P1, P2, P):
        """
        Parameters
        ----------
        P0 : modo.Vector3
        P1 : modo.Vector3
        P2 : modo.Vector3
        P  : modo.Vector3
     
        Returns the barycentric coords of P
        
        Transcribed from Christer Ericson's Real-Time Collision Detection (which, incidentally, is an excellent book)
        This is effectively Cramer's rule for solving a linear system
        """
        v0 = P1 - P0
        v1 = P2 - P0
        v2 = P - P0
     
        # dot products
        d00 = v0.dot(v0)
        d01 = v0.dot(v1)
        d11 = v1.dot(v1)
        d20 = v2.dot(v0)
        d21 = v2.dot(v1)
        
        denom = d00 * d11 - d01 * d01
        v = (d11 * d20 - d01 * d21) / denom
        w = (d00 * d21 - d01 * d20) / denom
        u = 1.0 - v - w
     
        return u, v, w

    def __init__(self, meshModoItem):
        self._mesh = meshModoItem


