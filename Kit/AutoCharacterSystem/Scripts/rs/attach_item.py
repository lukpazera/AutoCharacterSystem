

from .xfrm_link import TransformLink
from .items.bind_loc import BindLocatorItem


class AttachItem(object):
    
    @property
    def attachedToModoItem(self):
        """ Gets the item this attachment is attached to.
        """
        try:
            xfrmLink = TransformLink(self._rigItem.modoItem)
        except TypeError:
            return None
        return xfrmLink.driverItem

    @property
    def attachedToBindLocator(self):
        """ Gets the bind locator this attachment is attached to.
        
        Returns
        -------
        BindLocatorItem, None
        """
        modoItem = self.attachedToModoItem
        if modoItem is None:
            return None
        try:
            return BindLocatorItem(modoItem)
        except TypeError:
            return None
    
    # -------- Private methods
    
    def __init__(self, rigItem):
        self._rigItem = rigItem