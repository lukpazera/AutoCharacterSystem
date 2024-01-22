

import lx
import modo

from ..color_scheme import Color
from ..item_feature import LocatorSuperTypeItemFeature
from ..item import Item
from .. import const as c


class ColorItemFeature(LocatorSuperTypeItemFeature):
    """ Allows for setting item color according to rig color scheme.
    """

    CHAN_COLOR_IDENT = 'rsclIdent'

    # -------- Description attributes
    
    descIdentifier = c.ItemFeatureType.COLOR
    descUsername = 'Color'
    descPackages = 'rs.pkg.color'

    # -------- Public methods

    # --- Custom methods
    
    def reapplyColor(self):
        rigRootItem = self.item.rigRootItem
        if rigRootItem is None:
            return
        colorScheme = rigRootItem.colorScheme
        try:
            colorObj = colorScheme[self.color]
        except LookupError:
            return
        self.color = colorObj

    @property
    def colorIdentifier(self):
        """ Gets an identifier of item's color.
        
        Returns
        -------
        str
        """
        return self.modoItem.channel(self.CHAN_COLOR_IDENT).get()

    @property
    def color(self):
        """ Gets item's color object.
        
        Returns
        -------
        Color, None
            None when item doesn't have a color set or its identifier cannot
            be recognised and tied with any of the colors in the current
            color scheme.
        """
        rigRootItem = self.item.rigRootItem
        if rigRootItem is None:
            return None
        colorScheme = rigRootItem.colorScheme
        try:
            return colorScheme[self.colorIdentifier]
        except LookupError:
            pass
        return None

    @color.setter
    def color(self, colorObject):
        """ Sets new color from the color scheme for an item.
        
        Parameters
        ----------
        colorObject : Color, str, None
            Either color object directly or its string identifier.
            If it's identifier color will be looked up within the color scheme
            for a rig to which the item with the feature belongs.
        """
        if colorObject is None:
            identString = ''
        else:
            colorObject = self._getColorObject(colorObject)
            if colorObject is None:
                return # Bail out with no changes if color object is not valid.
            identString = colorObject.identifier
        
        self.item.setChannelProperty(self.CHAN_COLOR_IDENT, identString)

        if colorObject is None:
            return

        itemIdent = self.modoItem.id
    
        # Test if draw options are added
        if not self.modoItem.internalItem.PackageTest('glDraw'):
            lx.eval('!item.draw add locator item:{%s}' % itemIdent)

        # Make sure both wire and fill colors are set to user
        lx.eval('!item.channel locator$wireOptions user item:{%s}' % itemIdent)
        lx.eval('!item.channel locator$fillOptions user item:{%s}' % itemIdent)

        if colorObject.isTricolor:
            try:
                rigItem = Item.getFromModoItem(self.modoItem)
            except TypeError:
                return

            side = rigItem.side

            if side == c.Side.RIGHT:
                wireColor = colorObject.wire.evalRight
                fillColor = colorObject.fill.evalRight
            elif side == c.Side.LEFT:
                wireColor = colorObject.wire.evalLeft
                fillColor = colorObject.fill.evalLeft
            else:
                wireColor = colorObject.wire.center
                fillColor = colorObject.fill.center
        else:
            wireColor = colorObject.wire.center
            fillColor = colorObject.fill.center

        if wireColor is not None:
            lx.eval('!item.channel locator$wireColor {%f %f %f} item:{%s}' % (wireColor[0], wireColor[1], wireColor[2], itemIdent))
        if fillColor is not None:
            lx.eval('!item.channel locator$fillColor {%f %f %f} item:{%s}' % (fillColor[0], fillColor[1], fillColor[2], itemIdent))

    # -------- Private methods
    
    def _getColorObject(self, initializer):
        """ Gets color object from initialiser.
        
        Parameters
        ----------
        initialiser : Color, str
            Either color object or its string identifier.
        """
        if isinstance(initializer, Color):
            return initializer
        elif isinstance(initializer, str):
            # We need to reach out to rig to get the color scheme.
            rigRoot = self.item.rigRootItem
            if rigRoot is None:
                return None
            colors = rigRoot.colorScheme.colors
            try:
                index = colors.index(initializer)
            except ValueError:
                return None
            else:
                return colors[index]

        return None