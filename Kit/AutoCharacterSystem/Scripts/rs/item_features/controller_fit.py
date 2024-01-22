

import lx
import modo
import modox

from ..item_feature import LocatorSuperTypeItemFeature
from ..item import Item
from .. import const as c


class ControllerFitFeature(LocatorSuperTypeItemFeature):
    """ Allows for automatically fitting controller to a mesh.
    """

    CHAN_RAY_X_PLUS = 'rsisRayXPlus'
    CHAN_RAY_Y_PLUS = 'rsisRayYPlus'
    CHAN_RAY_Z_PLUS = 'rsisRayZPlus'

    CHAN_RAY_X_MINUS = 'rsisRayXMinus'
    CHAN_RAY_Y_MINUS = 'rsisRayYMinus'
    CHAN_RAY_Z_MINUS = 'rsisRayZMinus'
    
    CHAN_MARGIN = 'rsisMargin'

    # -------- Description attributes
    
    descIdentifier = c.ItemFeatureType.CONTROLLER_FIT
    descUsername = 'Fit Controller Shape'
    descPackages = ['rs.pkg.itemFitShape']
    descCategory = c.ItemFeatureCategory.DRAWING

    # -------- Public methods

    # --- Custom methods
    
    @property
    def positiveRaycastAxes(self):
        axes = []
        if self.item.getChannelProperty(self.CHAN_RAY_X_PLUS):
            axes.append(c.Axis.X)
        if self.item.getChannelProperty(self.CHAN_RAY_Y_PLUS):
            axes.append(c.Axis.Y)
        if self.item.getChannelProperty(self.CHAN_RAY_Z_PLUS):
            axes.append(c.Axis.Z)
        return axes

    @property
    def negativeRaycastAxes(self):
        axes = []
        if self.item.getChannelProperty(self.CHAN_RAY_X_MINUS):
            axes.append(c.Axis.X)
        if self.item.getChannelProperty(self.CHAN_RAY_Y_MINUS):
            axes.append(c.Axis.Y)
        if self.item.getChannelProperty(self.CHAN_RAY_Z_MINUS):
            axes.append(c.Axis.Z)
        return axes

    @property
    def margin(self):
        margin = self.item.getChannelProperty(self.CHAN_MARGIN)
        return margin
    
    @margin.setter
    def margin(self, value):
        self.item.setChannelProperty(self.CHAN_MARGIN, value)
