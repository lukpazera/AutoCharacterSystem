

import math

import lx
import modo
import modox

from .item_features.controller_fit import ControllerFitFeature as ItemShapeFitFeature
from .util import run
from .log import log


class ItemShapeFitter(object):
    """ Fits locator shape to a mesh using auto fit item feature properties.
    """
    
    def autoFit(self, rigItem):
        """ Automatically fits item shape.
        """
        try:
            itemShapeFit = ItemShapeFitFeature(rigItem)
        except TypeError:
            return False

        if not rigItem.modoItem.internalItem.PackageTest("glItemShape"):
            return False
            
        rayOriginVec = modo.Vector3(modox.LocatorUtils.getItemWorldPosition(rigItem.modoItem))
        wrotMtx = modox.LocatorUtils.getItemWorldRotation(rigItem.modoItem)
                
        spreadAngle = 0 #math.radians(itemShapeFit.raycastSpreadAngle)
        # Angle Step - fixed for now.
        angleStep = math.radians(15.0)
        
        # We always sample the raycast vec and limits of the spread angle.
        sampleAngles = []
        sampleAngles.append(0)
        
        startAngle = spreadAngle / 2 * -1.0
        endAngle = spreadAngle / 2
        sampleAngles.append(startAngle)
        sampleAngles.append(endAngle)
        
        longestDistance = 0.0
        shortestDistance = 1000000.0

        raycastingVectors = []

        positiveRaycastAxes = itemShapeFit.positiveRaycastAxes
        if positiveRaycastAxes:
            for axis in positiveRaycastAxes:
                raycastVec = modo.Vector3(wrotMtx.m[axis])
                raycastingVectors.append(raycastVec)
    
            negativeRaycastAxes = itemShapeFit.negativeRaycastAxes
            if negativeRaycastAxes:
                for axis in negativeRaycastAxes:
                    raycastVec = modo.Vector3(wrotMtx.m[axis]) * -1.0
                    raycastingVectors.append(raycastVec)

        totalDistance = 0.0
        samples = 0
        
        for meshItem in self._meshItems:
            with meshItem.geometry as geo:
             #
                    #angles = [0.0, 0.0, 0.0]
                    #angles[positiveRaycastAxis] = angle
                    #offsetMtx = modo.Matrix4.fromEuler()
                for raycastVec in raycastingVectors:
                    try:
                        distance = self._calculateHit(geo, rayOriginVec, raycastVec)
                    except ValueError:
                        continue
                    if distance > longestDistance:
                        longestDistance = distance
                    if distance < shortestDistance:
                        shortestDistance = distance
                    totalDistance += distance
                    samples += 1

        if samples > 0:
        #if longestDistance > 0.0 and shortestDistance < 999999.0:
            #fitMaxDistance = longestDistance * itemShapeFit.scaleFactor
            #fitMinDistance = shortestDistance * itemShapeFit.scaleFactor
            #fitDistance = ((fitMaxDistance - fitMinDistance) / 2.0) + fitMinDistance
            scaleFactor = itemShapeFit.margin + 1.0
            fitDistance = totalDistance / float(samples) * scaleFactor
            size = fitDistance * 2.0
            # this is where we want to perform the auto fit.
            run('!channel.value %f channel:{%s:isRadius}' % (fitDistance, rigItem.modoItem.id))
            
            run('!channel.value %f channel:{%s:isSize.X}' % (size, rigItem.modoItem.id))
            run('!channel.value %f channel:{%s:isSize.Y}' % (size, rigItem.modoItem.id))
            run('!channel.value %f channel:{%s:isSize.Z}' % (size, rigItem.modoItem.id))

    # -------- Private methods

    def _calculateHit(self, geo, pos, rayDir):
        """ Calculates distance to hit mesh.
        
        Parameters
        ----------
        pos : modo.Vector3
        
        rayDir : modo.Vector3
        
        Returns
        -------
        float
        
        Raises
        ------
        ValueError
            If there was no hit.
        """
        polygons = geo.polygons
        rawPolygons = polygons.accessor

        hit, normal, dist = rawPolygons.IntersectRay(pos.values, rayDir.values)
        if not hit:
            lx.out('Sample did not hit anything')
            raise ValueError
        
        return dist

    def __init__(self, meshItems):
        if type(meshItems) not in (list, tuple):
            meshItems = [meshItems]
        self._meshItems = meshItems
