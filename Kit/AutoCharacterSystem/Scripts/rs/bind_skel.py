

import modo
import modox
from modox import LocatorUtils

from . import const as c
from .log import log
from .debug import debug
from .rig import Rig
from .items.bind_loc import BindLocatorItem


class BindSkeleton(object):
    """ Represents rig's bind skeleton.
    
    Parameters
    ----------
    rig : Rig, RootItem
        Either a rig or an item the rig can be initialised with.
        
    Raises
    ------
    TypeError
        When trying to initialise with bad item.
    """
        
    @property
    def modoItems(self):
        """ Gets all bind skeleton locators as regular modo items.
        
        The order may be random.
        
        Returns
        -------
        list of modo.Item
        """
        return self._rig.getElements(c.ElementSetType.BIND_SKELETON)

    @property
    def items(self):
        """ Gets all bind skeleton items as a list of BindLocatorItem.
        
        The order may be random.
        
        Returns
        -------
        list of BindLocatorItem
        """
        items = self.modoItems
        locs = []
        for item in items:
            locs.append(BindLocatorItem(item))
        return locs

    @property
    def rootLocatorsCount(self):
        """
        Gets a number of bind locators that are roots - not parented to other bind locators.

        A continuous bind skeleton hierarchy should have a single root.
        Multiple roots may mean that some modules are disconnected.
        """
        rootCount = 0
        for bindLoc in self.items:
            parent, external = bindLoc.getParentBindLocator()
            if parent is None:
                rootCount += 1
        return rootCount

    @property
    def rootItems(self):
        """ Gets only these locators that are not childs of other bind locators.
        
        These are considered root bind locators.
        
        Returns
        -------
        list of BindLocatorItem
        """
        roots = []
        for modoItem in self.modoItems:
            parent = modoItem.parent
            try:
                bindLoc = BindLocatorItem(parent)
            except TypeError:
                roots.append(BindLocatorItem(modoItem))
        return roots
    
    @property
    def itemsHierarchy(self):
        """ Gets all bind skeleton locators in hierarchical order.
        
        Returns
        -------
        list of BindLocatorItem
        """
        hrch = []
        for root in self.rootItems:
            hrch.append(root)
            modohrch = modox.ItemUtils.getHierarchyRecursive(root.modoItem, includeRoot=False)
            # Skip any items that are not bind locators.
            # Log errors on the way.
            for modoItem in modohrch:   
                try:
                    bloc = BindLocatorItem(modoItem)
                except TypeError:
                    if debug.output:
                        log.out("%s item is not bind locator, skipping it!" % modoItem.name, log.MSG_ERROR)
                    continue
                hrch.append(bloc)
        return hrch

    @property
    def weightMaps(self):
        """
        Gets names of all the weight containers and maps that this rig is using.

        Return
        ------
        list(str)
        """
        weightMaps = []
        for bloc in self.items:
            blocmap = bloc.weightMapName
            if blocmap is not None:
                weightMaps.append(blocmap)

    def getJointClosestToPoint(self, worldPosVec, ignoreHidden=True):
        """ Returns bind locator closest to a given point in world space.
        
        Only joint type bind locators are considered, meaning only ones
        that have a 'length' by having a child item to point at.
        
        Parameters
        ----------
        worldPosVec : modo.Vector3

        ignoreHidden : bool
            When True hidden bind locators will be ignored when looking for the closest one.

        Returns
        -------
        BindLocatorItem
        """
        self._cacheBindLocatorsWorldPositions(ignoreHidden=ignoreHidden)
        closestIndex = -1
        closestDistance = 1000000.0

        for x in range(len(self._wposCache)):
            dist = worldPosVec.distanceBetweenPoints(self._wposCache[x])
            if dist < closestDistance:
                closestDistance = dist
                closestIndex = x
        
        return self._bindLocCache[closestIndex]

    # -------- Private methods
    
    def _cacheBindLocatorsWorldPositions(self, ignoreHidden=True):
        try:
            if self._wposCache:
                return
        except AttributeError:
            self._wposCache = []
            self._bindLocCache = []
            for bindloc in self.items:
                if bindloc.isLeaf:
                    continue
                if ignoreHidden and bindloc.hidden:
                    continue
                self._wposCache.append(bindloc.centerPoint)
                self._bindLocCache.append(bindloc)
    
    def __init__(self, rig):
        if not isinstance(rig, Rig):
            try:
                rig = Rig(rig)
            except TypeError:
                raise
        self._rig = rig