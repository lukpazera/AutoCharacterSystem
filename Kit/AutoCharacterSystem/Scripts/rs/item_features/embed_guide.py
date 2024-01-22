

import lx
import modo
import modox

from ..item_feature import LocatorSuperTypeItemFeature
from ..item import Item
from .. import const as c
from ..xfrm_in_mesh import EmbedPositionSource
from ..element_sets.guides import GuidesElementSet
from ..items.guide import GuideItem
from ..items.guide import ReferenceGuideItem
from ..module_guide import ModuleGuide


class EmbedGuideFeature(LocatorSuperTypeItemFeature):
    """ Allows for setting properties for guide that is meant to be saved in mesh.
    """

    _GRAPH_AXES_SOURCE = 'rs.egAxesSource'
    _CHAN_POSITION_SOURCE = 'rsegPosSource'
    _POSITION_SOURCE_FROM_HINT = {'xaxis': EmbedPositionSource.AXIS_X,
                                  'yaxis': EmbedPositionSource.AXIS_Y,
                                  'zaxis': EmbedPositionSource.AXIS_Z,
                                  'closest': EmbedPositionSource.CLOSEST}

    PositionSource = EmbedPositionSource

    # -------- Description attributes
    
    descIdentifier = c.ItemFeatureType.EMBED_GUIDE
    descUsername = 'Embed Guide In Mesh'
    descPackages = ['rs.pkg.embedGuide']
    descExclusiveItemType = c.RigItemType.GUIDE
    
    # -------- Public methods

    @property
    def axesReferenceGuide(self):
        graph = self.modoItem.itemGraph(self._GRAPH_AXES_SOURCE)
        try:
            return graph.forward(0)
        except LookupError:
            return None
    
    @axesReferenceGuide.setter
    def axesReferenceGuide(self, guideItem):
        """ Gets/sets reference orientation that is used to embed guide position in the mesh.
        
        Typically this will be the guide that is driven by direction constraint set up
        in conjuction with the edit guide.
        
        Parameters
        ----------
        guideItem : GuideItem
        
        Returns
        -------
        modo.Item, None
        """
        modox.ItemUtils.clearForwardGraphConnections(self.item.modoItem, self._GRAPH_AXES_SOURCE)
        
        if guideItem is None:
            return

        modox.ItemUtils.addForwardGraphConnections(self.item.modoItem, guideItem.modoItem, self._GRAPH_AXES_SOURCE)

    @property
    def axesReferenceGuidesPopup(self):
        """ Gets a list of guides that are available to set as axes reference.
        
        We only allow for reference guides.
        
        Returns
        -------
        list of ReferenceGuideItem
        """
        rigRoot = self.item.rigRootItem
        moduleRoot = self.item.moduleRootItem
        modGuide = ModuleGuide(moduleRoot)
        refGuides = []
        
        for refGuide in modGuide.referenceGuides:
            if refGuide.modoItem == self.item.modoItem:
                continue
            refGuides.append(refGuide)
        
        return refGuides

    @property
    def positionSource(self):
        """ Gets position source.
        """
        # Note that returned value is string hint.
        posSrcHint = self.item.getChannelProperty(self._CHAN_POSITION_SOURCE)
        return self._POSITION_SOURCE_FROM_HINT[posSrcHint]
    
    @positionSource.setter
    def positionSource(self, source):
        """ Gets/Sets source for embedding guide position.
        
        Parameters
        ----------
        source : str, PositionSource.XXX constant
            either hint or PositionSource constant.
        """
        if isinstance(source, str):
            source = self._POSITION_SOURCE_FROM_HINT[source]
        self.item.setChannelProperty(self._CHAN_POSITION_SOURCE, source)

    @property
    def forwardOrientationSource(self):
        pass
    
    @forwardOrientationSource.setter
    def forwardOrientationSource(self, modoItem):
        """ Gets/sets item that will serve as forward orientation reference point.
        
        For best results the reference point needs to be embedded in a mesh as well.
        """
        pass

    @property
    def upOrientationSource(self):
        pass
    
    @upOrientationSource.setter
    def upOrientationSource(self, modoItem):
        """ Gets/sets item that will serve as up orientation reference point.
        
        For best results the reference point needs to be embedded in a mesh as well.
        """
        pass