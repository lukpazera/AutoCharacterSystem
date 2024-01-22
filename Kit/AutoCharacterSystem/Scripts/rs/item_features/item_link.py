

import lx
import modo
import modox

from ..item_feature import LocatorSuperTypeItemFeature
from ..item import Item
from .. import const as c


class ItemLinkLinePattern(object):
    NONE = 0
    DOTS = 1
    DOTS_LONG = 2
    DASH = 3
    DASH_LONG = 4
    DASH_EXTRA_LONG = 5
    DOTS_AND_DASHES = 6

    
class ItemLinkColorSource(object):
    WIREFRAME = 0
    FILL = 1
    CUSTOM = 2    
    
        
class ItemLinkFeature(LocatorSuperTypeItemFeature):
    """ Allows for drawing a link between 2 items.
    """

    GRAPH_ITEM_LINK = 'rs.itemLink'
    CHAN_ENABLE = 'rsilEnable'

    _CHAN_PATTERN = "rsilPattern";
    _CHAN_THICKNESS = "rsilThickness";
    _CHAN_OPACITY = "rsilOpacity";
    _CHAN_POINT_SIZE = "rsilPointSize";
    _CHAN_COLOR_TYPE = "rsilColorType";
    _CHAN_COLOR_R = "rsilColor.R";
    _CHAN_COLOR_G = "rsilColor.G";
    _CHAN_COLOR_B = "rsilColor.B";
    
    LinePattern = ItemLinkLinePattern
    ColorSource = ItemLinkColorSource

    _LINE_PATTERN_HINTS = {
        "none": 0,
        "dots": 1,
        "dotslong": 2,
        "dash": 3,
        "dashlong": 4,
        "dashxlong": 5,
        "dotdash": 6}
    
    _COLOR_SOURCE_HINTS = {
        "wire": 0,
        "fill": 1,
        "custom": 2}

    # -------- Description attributes
    
    descIdentifier = c.ItemFeatureType.ITEM_LINK
    descUsername = 'Draw Item Link'
    descPackages = 'rs.pkg.itemLink'
    descCategory = c.ItemFeatureCategory.DRAWING

    # -------- Public methods

    # --- Custom methods
    
    @property
    def enable(self):
        return self.item.getChannelProperty(self.CHAN_ENABLE)

    @enable.setter
    def enable(self, state):
        """ Sets item link drawing enable state.
        
        Parameters
        ----------
        state : bool
        
        Returns
        -------
        bool
            True when enable state was changed, False otherwise.
        """
        return self.item.setChannelProperty(self.CHAN_ENABLE, state)
    
    @property
    def linkedItem(self):
        graph = self.modoItem.itemGraph(self.GRAPH_ITEM_LINK)
        try:
            return graph.forward(0)
        except LookupError:
            return None
    
    @linkedItem.setter
    def linkedItem(self, modoItem):
        """ Gets/sets the item to draw the link to.
        
        Parameters
        ----------
        modoItem : modo.Item, None
            Item to draw the link to. Pass None to clear linked item connection.

        Returns
        -------
        modo.Item
        """
        modox.ItemUtils.clearForwardGraphConnections(self.modoItem, self.GRAPH_ITEM_LINK)
        if modoItem is not None:
            modox.ItemUtils.addForwardGraphConnections(self.modoItem, modoItem, self.GRAPH_ITEM_LINK)
    
    @property
    def color(self):
        r = self.item.getChannelProperty(self._CHAN_COLOR_R)
        g = self.item.getChannelProperty(self._CHAN_COLOR_G)
        b = self.item.getChannelProperty(self._CHAN_COLOR_B)
        return (r, g, b)
    
    @color.setter
    def color(self, rgb):
        """ Gets/sets link color.
        
        Paramters
        ---------
        rgb : tuple
            R, G, B values in 0.0-1.0 float range.
            
        Returns
        -------
        tuple(r,g,b)
        """
        self.item.setChannelProperty(self._CHAN_COLOR_R, rgb[0])
        self.item.setChannelProperty(self._CHAN_COLOR_G, rgb[1])
        self.item.setChannelProperty(self._CHAN_COLOR_B, rgb[2])
                
    @property
    def colorSource(self):
        return self._COLOR_SOURCE_HINTS[self.item.getChannelProperty(self._CHAN_COLOR_TYPE)]
    
    @colorSource.setter
    def colorSource(self, const):
        """ Gets color source property.
        
        Parameters
        ----------
        const : int
            ColorSource.XXX

        Returns
        -------
        int
            ColorSource.XXX
        """
        self.item.setChannelProperty(self._CHAN_COLOR_TYPE, const)
    
    @property
    def endPointsSize(self):
        return self.item.getChannelProperty(self._CHAN_POINT_SIZE)
    
    @endPointsSize.setter
    def endPointsSize(self, size):
        """ Gets/sets size of link end points.
        
        Parameters
        ----------
        size : int
        
        Returns
        -------
        int
        """        
        self.item.setChannelProperty(self._CHAN_POINT_SIZE, size)
    
    @property
    def linePattern(self):
        return self._LINE_PATTERN_HINTS[self.item.getChannelProperty(self._CHAN_PATTERN)]
    
    @linePattern.setter
    def linePattern(self, pattern):
        """ Gets line pattern property.
        
        Parameters
        ----------
        pattern : int
            LinePattern.XXX

        Returns
        -------
        int
            LinePattern.XXX
        """        
        self.item.setChannelProperty(self._CHAN_PATTERN, pattern)
    
    @property
    def lineThickness(self):
        return self.item.getChannelProperty(self._CHAN_THICKNESS)
    
    @lineThickness.setter
    def lineThickness(self, thickness):
        """ Gets/sets item link line thickness.
        
        Parameters
        ----------
        thickness : int
        
        Returns
        -------
        int
        """
        self.item.setChannelProperty(self._CHAN_THICKNESS, thickness)
        
    def onRemove(self):
        """ Needs to clear any left over graph links.
        """
        self.linkedItem = None
