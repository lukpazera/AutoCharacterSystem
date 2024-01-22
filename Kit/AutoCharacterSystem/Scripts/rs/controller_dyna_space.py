
import lx
import modo
import modox

from . import const as c
from .item import Item
from .util import run
from .log import log
from .event_handler import EventHandler
from .const import EventTypes as e
from .xfrm_link import TransformLink


class ControllerDynamicSpace(object):
    """ This class allows for setting and removing dynamic space setup for a controller.
    
    Active dynamic space setup should be polymorphic with the dyna parent transform link.
    This is because plugs need to be updated during guide application and transform link methods
    handle that.
    Note that this class should be used in setup mode.
    
    Parameters
    ----------
    initObject : Item, modo.Item, str
        Needs to reference the item that has the controller feature applied.
    """

    def remove(self):
        """ Removes dynamic space setup entirely.
        """
        try:
            xfrmLink = TransformLink(self._item.modoItem)
        except TypeError:
            return
        xfrmLink.remove()

    @property
    def isFullSetup(self):
        try:
            dynaParentSetup = modox.DynamicParentSetup(self._item.modoItem)
        except TypeError:
            return False
        return dynaParentSetup.isFullSetup
    
    @property
    def animatedChannels(self):
        """ Gets a list of animated channels in the controller's dynamic space setup.
        
        These are the channels that should be added to an actor.
        
        Returns
        -------
        list of modo.Channel
        """
        try:
            dynaParentSetup = modox.DynamicParentSetup(self._item.modoItem)
        except TypeError:
            return []
        return dynaParentSetup.animatedChannels
    
    @property
    def dynamicParentModifier(self):
        """ Gets the dynamic parenting modifier for the dynamic space setup on controller's side.
        
        Returns
        -------
        modo.Item, None
            Dynamic parent modifier item or None if none was found.
        """
        return modox.ItemUtils.getParentConstraintItem(self._item.modoItem)

    @property
    def isAnimated(self):
        """
        Tests whether dynamic space is animated.

        This is done by testing whether the parent channel on the dynamic modifier
        for the dynamic space setup is animated.

        Returns
        -------
        bool
        """
        dynaParent = self.dynamicParentModifier
        if dynaParent is None:
            return False
        parentChan = dynaParent.channel('parent')
        return parentChan.isAnimated

    @property
    def draw(self):
        dynaParent = self.dynamicParentModifier
        if dynaParent is None:
            return False

        # Note that when you get channel with hints you will get string hint
        # rather then the int value.
        draw = dynaParent.channel('draw').get()
        if draw == 'off':
            return False
        return True
    
    @draw.setter
    def draw(self, value):
        """ Toggle drawing for dynamic parenting links.
        
        Parameters
        ----------
        draw : boolean
        """
        dynaParent = self.dynamicParentModifier
        if dynaParent is None:
            return
    
        if not value:
            draw = 0
        else:
            draw = 2
        dynaParent.channel('draw').set(draw, 0.0, False, lx.symbol.s_ACTIONLAYER_SETUP)
        
    # -------- Private methods

    def __init__(self, initObject):
        try:
            self._item = Item.getFromOther(initObject)
        except TypeError:
            raise


class DynamicSpaceEventHandler(EventHandler):
    """ Dynamic space has to be updated when guide is applied to rig.
    """

    descIdentifier = 'dynaspace'
    descUsername = 'Dynamic Space'

    @property
    def eventCallbacks(self):
        return {e.GUIDE_APPLY_INIT: self.event_guideApplyInit,
                e.GUIDE_APPLY_PRE: self.event_guideApplyPre,
                e.GUIDE_APPLY_POST2: self.event_guideApplyPost}

    def event_guideApplyInit(self, **kwargs):
        """ Called in the beginning of the guide application process.
        """
        try:
            rig = kwargs['rig']
        except KeyError:
            return

        self._allLinks = []
        for modoItem in rig[c.ElementSetType.CONTROLLERS].elements:
            try:
                self._allLinks.append(TransformLink(modoItem))
            except TypeError:
                continue

    def event_guideApplyPre(self, **kwargs):
        for xfrmLink in self._allLinks:
            xfrmLink.deactivate()

    def event_guideApplyPost(self, **kwargs):
        for xfrmLink in self._allLinks:
            xfrmLink.updateRestPose()

        for xfrmLink in self._allLinks:
            xfrmLink.reactivate()

        del self._allLinks