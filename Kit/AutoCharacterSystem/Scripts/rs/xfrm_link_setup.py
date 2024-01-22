

from .sys_component import SystemComponent
from . import const as c


class TransformLinkSetup(SystemComponent):
    """ Implements a setup required to connect two rig items transforms.
    
    Parameters
    ----------
    itemFrom : modo.Item
    
    Methods
    -------
    onDeactivate()
        Method is called when the link needs to be temporarily deactivated.
        
    onUpdateRestPose()
        Method called when link rest pose needs to be updated.
        This happens when either one or both link items changed their transforms.
        Rest pose needs to be updated in such a way that when link is reactivated
        items rest pose stays the same as when link is not active.
    
    onReactivate()
        Reactive the link so it's constraining items again.
    """
    
    descIdentifier = ''
    descUsername = ''
    
    # -------- System Component
    
    @classmethod
    def sysType(cls):
        return c.SystemComponentType.XFRM_LINK_SETUP
    
    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
    
    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Transforms Link Setup'
    
    # -------- Properties
    
    @property
    def modoItem(self):
        """ Gets the item from which the link goes (the constrained item).
        """
        return self._itemFrom
    
    @property
    def targetModoItem(self):
        """ Gets an item to which the link goes.
        """
        return self._itemTo

    @property
    def setupItems(self):
        """ Gets a list of all items forming the transform link setup.
        """
        return []

    # -------- Public methods that need to be implemented
    
    def onNew(self, compensation=True):
        """ Called when new transform link needs to be created.
        
        Target item can be obtained using targetModoItem property.

        Parameters
        ----------
        compensation : bool
            When True the link will be created preserving linked item world transform.
        """
        pass
    
    def onRemove(self):
        """ Called when the link needs to be removed.
        
        This should clear all the setup from existing link.
        """
        pass

    def onAddToSetup(self):
        """ Gets a list of setup items that should be added to the item from assembly.
        
        It returns all setup items by default.
        """
        return self.setupItems

    def onAddToTargetSetup(self):
        """ Gets a list of setup items that should be added to the item to assembly.
        
        Returns empty list by default.
        """
        return []

    @classmethod
    def clearFromItemIfNotValid(cls, modoItem):
        """ Clears setup from given item if the setup is not fully there.
        """
        pass

    # -------- Private methods
    
    def __init__(self, itemFrom, itemTo):
        self._itemFrom = itemFrom
        self._itemTo = itemTo