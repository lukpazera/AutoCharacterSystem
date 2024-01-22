

import lx
import modo
import modox

from ..item_feature import LocatorSuperTypeItemFeature
from ..item import Item
from .. import const as c


class ItemShapeFeature(LocatorSuperTypeItemFeature):
    """ Allows for drawing custom item shapes for an item.
    """

    # -------- Description attributes
    
    descIdentifier = c.ItemFeatureType.ITEM_SHAPE
    descUsername = 'Draw Item Shapes'
    descPackages = 'rs.pkg.itemShape'
    descCategory = c.ItemFeatureCategory.DRAWING
    

class ItemAxisFeature(LocatorSuperTypeItemFeature):
    """ Allows for drawing item axes in viewport.
    """

    _AXIS_SOURCE_GRAPH = "rs.itemAxisSource"

    # -------- Description attributes
    
    descIdentifier = c.ItemFeatureType.ITEM_AXIS
    descUsername = 'Draw Item Axes'
    descPackages = 'rs.pkg.itemAxis'
    descCategory = c.ItemFeatureCategory.DRAWING
    
    @property
    def orientationSource(self):
        graph = self.modoItem.itemGraph(self._AXIS_SOURCE_GRAPH)
        try:
            return graph.forward(0)
        except LookupError:
            return None
    
    @orientationSource.setter
    def orientationSource(self, modoItem):
        """ Gets/sets the source for the orientation for drawing axes.
        
        If it's None the items itself is used. If it's set to another item
        the orientation of that other item will be used for drawing axes.
        """
        modox.ItemUtils.clearForwardGraphConnections(self.modoItem, self._AXIS_SOURCE_GRAPH)
        if modoItem is not None:
            modox.ItemUtils.addForwardGraphConnections(self.modoItem, modoItem, self._AXIS_SOURCE_GRAPH)