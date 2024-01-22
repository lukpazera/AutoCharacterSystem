

import lx
import modo
import modox

from .core import service
from .log import log as log
from . import const as c
from .component import Component
from .component_setups.rig import RigComponentSetup
from .xfrm_link import TransformLink
from .items.generic import GenericItem
from .item_utils import ItemUtils
from .item_feature_op import ItemFeatureOperator
from .item_features.item_link import ItemLinkFeature
from .util import run


class AttachmentSet(Component):
    """ Attachment set is a collection of items attached to the rig in common way.
    
    Items are attached using transform links.
    This is base class that inherits from Component.
    
    Parameters
    ----------
    initObject : ComponentSetup, modo.Item
        Attachment set can be initialised either with the component setup
        that represents it in the scene or with modo item that is the root
        of the component setup.
    """
    
    # -------- Attributes
    
    descTransformLinkType = c.TransformLinkType.DYNA_PARENT
    descMembersItemClass = None

    # -------- System component

    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Attachment Set Component'

    # -------- Public interface

    def onItemAttach(self, modoItem):
        """ Perform extra steps when item is attached to the rig.
        """
        pass
    
    def attachItem(self, modoItem, targetModoItem):
        """ Attaches an item or a list of items to the target item.
        
        NOTE: This should be called while in setup mode!
        
        Returns
        -------
        Item, None
            When item is attached it's converted to rig item if attachment
            set is defined to do so. In such case Item is returned, None
            otherwise.
        """
        # Test if passed modo item is already of required rig item type
        # if rig item type was defined for the attachment set.
        if self.descMembersItemClass is not None:
            try:
                rigItem = self.descMembersItemClass(modoItem)
            except TypeError:
                rigItem = self.descMembersItemClass.newFromExistingItem(modoItem)

        self._setAttachmentCenter(rigItem)

        # Add to setup when item type is already defined.
        # The item won't be recognised properly otherwise.
        self.setup.addItem(modoItem)

        # Initialise link after attachment item was added to setup.
        # Transform link setup items will not get added to correct component setup otherwise.
        # If link already exists - it will be removed.
        try:
            TransformLink.new(modoItem, targetModoItem, self.descTransformLinkType)
        except TypeError:
            return
        
        try:
            self.onItemAttach(modoItem)
        except AttributeError:
            pass

        self._setupItemLink(rigItem, targetModoItem)
        
        return rigItem

    def detachItem(self, modoItem):
        """ Detaches given item from the set.
        
        NOTE: Method should be called with setup mode on!
        """
    
        try:
            self.onItemDetach(modoItem)
        except AttributeError:
            pass

        try:
            xfrmLink = TransformLink(modoItem)
        except TypeError:
            return
        
        xfrmLink.remove()
        
        # If item is rig item type it needs to be standardized
        if self.descMembersItemClass is not None:
            try:
                rigItem = self.descMembersItemClass(modoItem)
            except TypeError:
                pass
            else:
                ItemUtils.standardize(rigItem)

        self.setup.removeItem(modoItem)

    def onItemDetach(self, modoItem):
        """ Any custom clean up that needs to be done when item is detached from rig.
        """
        pass

    @property
    def items(self):
        """ Returns all items in the set.
        
        Please note that if the set doesn't have descMembersItemClass set this will simply
        return modo items instead.
        
        Returns
        -------
        list of Item inherited objects, list of modo.Item
        """
        if self.descMembersItemClass is None:
            return self.modoItems

        rigItems = []
        for modoItem in self.modoItems:
            try:
                rigItem = self.descMembersItemClass(modoItem)
            except TypeError:
                continue
            rigItems.append(rigItem)
        return rigItems
        
    @property
    def modoItems(self):
        """ Returns all the items attached to the set.
        
        This really returns all the items that are under the attachment setup root item.
        It's really stupid, the items in the attachment set should be marked somehow and
        only these items should be returned so any other extra or accidental items are
        not returned.
        """
        return self.setup.hierarchyItems

    @property
    def transformLinks(self):
        """ Gets a list of all transform links objects used by the attachment set.
        """
        xfrmLinks = []
        for modoItem in self.modoItems:
            try:
                xfrmLink = TransformLink(modoItem)
            except TypeError:
                continue
            xfrmLinks.append(xfrmLink)
        return xfrmLinks

    # -------- Private methods
    
    def _setupItemLink(self, rigItemFrom, modoItemTo):
        itemFeatures = ItemFeatureOperator(rigItemFrom)
        if not itemFeatures.hasFeature(c.ItemFeatureType.ITEM_LINK):
            itemLink = itemFeatures.addFeature(c.ItemFeatureType.ITEM_LINK)
        else:
            itemLink = itemFeatures.getFeature(c.ItemFeatureType.ITEM_LINK)
            
        itemLink.linkedItem = modoItemTo
        itemLink.endPointsSize = 6
        itemLink.colorSource = ItemLinkFeature.ColorSource.CUSTOM
        itemLink.color = (0.6, 0.2, 0.7)
        itemLink.linePattern = ItemLinkFeature.LinePattern.DASH_LONG
        itemLink.lineThickness = 4
        itemLink.enable = True

    def _freezeScale(self, modoItem):
        """
        Freeze scale on the modo item. Attachments cannot have scaling because it breaks
        transforms on the link between attachment and rig.
        """
        if modox.LocatorUtils.hasLocalScale(modoItem):
            modox.LocatorUtils.freezeTransforms(modoItem, scale=True)

    def _setAttachmentCenter(self, rigItemFrom):
        if rigItemFrom.modoItem.type not in ('mesh', 'meshInst'):
            return
        rigItemFrom.modoItem.select(replace=True)
        run('!center.bbox center')