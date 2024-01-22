

import modox

from .core import service
from .xfrm_link_setup import TransformLinkSetup
from .component_setup import ComponentSetup
from .item_features.item_link import ItemLinkFeature
from .log import log
from . import const as c


class TransformLink(object):
    """ Represents a link between two locator type rig items.
    
    Transforms of itemFrom are linked with another item.
    
    Parameters
    ----------
    itemFrom : modo.Item
        The item from which the link is going to another item.
        Item from is the constrained item.
    
    Raises
    ------
    TypeError
        When there is no transform link going from the given item.
    """

    TAG_ID = 'RSXL'
    GRAPH_NAME = 'rs.xfrmLink'

    @classmethod
    def new(self, itemFrom, itemTo, linkType, compensation=True):
        """ Creates new link between two items.
        
        If this item is already linked the existing link
        will be removed first.
        
        Parameters
        ----------
        itemFrom : modo.Item

        linkType : str
            Transform link setup identifier.
            
        Raises
        ------
        TypeError
            When link of a given type is not registered with the system.
        """
        # Be sure the requsted link type exists
        try:
            setupClass = service.systemComponent.get(c.SystemComponentType.XFRM_LINK_SETUP, linkType)
        except LookupError:
            raise TypeError
        
        # Be sure to remove any existing links
        try:
            xfrmLink = TransformLink(itemFrom)
        except TypeError:
            pass
        else:
            xfrmLink.remove()

        # Set tag
        itemFrom.setTag(self.TAG_ID, linkType)
        
        # Make new link graph connection
        itemFromGraph = itemFrom.itemGraph(self.GRAPH_NAME)
        itemToGraph = itemTo.itemGraph(self.GRAPH_NAME)
        itemFromGraph >> itemToGraph
    
        linkSetup = setupClass(itemFrom, itemTo)
        linkSetup.onNew(compensation) # This actually sets up the link

        # Add all setup items to correct component setups.
        setup = ComponentSetup.getSetupFromModoItem(itemFrom)
        if setup is not None:
            setup.addItem(linkSetup.onAddToSetup())
        targetSetup = ComponentSetup.getSetupFromModoItem(itemTo)
        if targetSetup is not None:
            targetSetup.addItem(linkSetup.onAddToTargetSetup())

        return self(itemFrom)
    
    @classmethod
    def clearFromItemIfNotValid(cls, itemFrom):
        """ Clears transform link for an item if the link happens to not be complete.
        
        This can happen when module assembly was saved and then loaded to another scene.
        The 'itemTo' part of link setup will be missing.
        
        Parameters
        ----------
        itemFrom : modo.Item
            The item that has the potentially incomplete link setup.
        
        Raises
        ------
        TypeError
            If there is a link of unknown type found.
        """
        # See if item has link tag.
        try:
            linkType = itemFrom.readTag(cls.TAG_ID)
        except LookupError:
            return
        try:
            linkSetupClass = service.systemComponent.get(c.SystemComponentType.XFRM_LINK_SETUP, linkType)
        except LookupError:
            raise TypeError

        try:
            linkSetupClass.clearFromItemIfNotValid(itemFrom)
        except AttributeError:
            pass

    @classmethod
    def getLinkedTransformLinksFromTarget(cls, modoItem, linkType=None):
        """
        Gets a list of Transform links that are attached to this item.

        This is a way of getting transfrom links from the target item.
        Single link target item can have multiple links associated with it.

        Returns
        -------
        [TransformLink]
        """
        linkedItems = modox.ItemUtils.getReverseGraphConnections(modoItem, cls.GRAPH_NAME)
        links = []
        for modoItem in linkedItems:
            try:
                xfrmLink = TransformLink(modoItem)
            except TypeError:
                continue
            if linkType is not None and linkType != xfrmLink.type:
                continue
            links.append(xfrmLink)
        return links

    @property
    def type(self):
        """ Gets the type of a link.
        
        Returns
        -------
        str
            None is returned when there is no link.
        """
        return self._getLinkType(self._itemFrom)

    def remove(self):
        """ Removes current transform link.
        """
        # Clear tag
        self._itemFrom.setTag(self.TAG_ID, None)
        
        # Clear graph link
        itemFromGraph = self._itemFrom.itemGraph(self.GRAPH_NAME)
        itemToGraph = self._itemTo.itemGraph(self.GRAPH_NAME)
        itemToGraph << itemFromGraph
        
        try:
            self._linkSetup.onRemove()
        except AttributeError:
            pass

    def deactivate(self):
        """ Deactivates the transform link.
        
        The link will still be there but not evaluating.
        """
        try:
            self._linkSetup.onDeactivate()
        except AttributeError:
            pass

    def updateRestPose(self):
        """ Updates link rest pose.
        """
        try:
            self._linkSetup.onUpdateRestPose()
        except AttributeError:
            pass
    
    def reactivate(self):
        """ Activates the link again (if it was deactivated).
        """
        try:
            self._linkSetup.onReactivate()
        except AttributeError:
            pass
    
    @property
    def drivenItem(self):
        """ Gets item driven by the link (itemFrom).
        
        Returns
        -------
        modo.Item
        """
        return self._itemFrom
    
    @property
    def driverItem(self):
        """ Gets item that drives the link (itemTo).
        
        Returns
        -------
        modo.Item
        """
        return self._itemTo

    @property
    def setup(self):
        """
        Gets link transform setup object.

        Returns
        -------
        TransformLinkSetup
        """
        return self._linkSetup

    # -------- Private methods

    @classmethod
    def _getLinkType(self, modoItem):
        try:
            return modoItem.readTag(self.TAG_ID)
        except LookupError:
            pass
        return None

    def _getItemTo(self):
        """ Tests whether this item has its transforms linked.
        """
        itemFromGraph = self._itemFrom.itemGraph(self.GRAPH_NAME)
        try:
            return itemFromGraph.forward(0)
        except LookupError:
            return None
        return None

    def __init__(self, itemFrom):
        self._itemFrom = itemFrom
        self._itemTo = self._getItemTo()
        if self._itemTo is None:
            raise TypeError
        self._type = self._getLinkType(self._itemFrom)
        try:
            setupClass = service.systemComponent.get(c.SystemComponentType.XFRM_LINK_SETUP, self._type)
        except LookupError:
            raise TypeError
        self._linkSetup = setupClass(self._itemFrom, self._itemTo)


class DrawTransformLink(ItemLinkFeature):
    """
    This class implements feature that draws transform link if one is set up on an item.

    This is quickly put together and it simply inherits from draw item link feature.
    For now this feature will be hidden and set up from code only.
    It's not safe to use all its methods so be sure implement it properly before making it
    available from user interface.
    """

    # -------- Description attributes

    descIdentifier = c.ItemFeatureType.DRAW_XFRM_LINK
    descUsername = "Draw Transform Link"
    descPackages = ['rs.pkg.drawXfrmLink']
    descCategory = c.ItemFeatureCategory.DRAWING
    descListed = True

    # -------- Constants

    GRAPH_ITEM_LINK = 'rs.xfrmLink'
    CHAN_ENABLE = 'rsixEnable'

    _CHAN_PATTERN = "rsxlPattern";
    _CHAN_THICKNESS = "rsxlThickness";
    _CHAN_OPACITY = "rsxlOpacity";
    _CHAN_POINT_SIZE = "rsxlPointSize";
    _CHAN_COLOR_TYPE = "rsxlColorType";
    _CHAN_COLOR_R = "rsxlColor.R";
    _CHAN_COLOR_G = "rsxlColor.G";
    _CHAN_COLOR_B = "rsxlColor.B";
