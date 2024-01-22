

import lx
import modo
import modox

from ..item_feature import LocatorSuperTypeItemFeature
from ..items.guide import GuideItem
from ..items.guide import ReferenceGuideItem
from ..element_sets.guides import GuidesElementSet
from ..module import Module
from ..module_guide import ModuleGuide
from .. import const as c
from ..core import service


class GuideMode(object):
    REFERENCE = 'reference'
    BUFFER = 'buffer'


class GuideItemFeature(LocatorSuperTypeItemFeature):
    """ Sets relation of an item to the guide.
    """

    GRAPH_NAME = 'rs.guideItem'
    _CHAN_GUIDE_MODE = 'rsgdMode'
    CHAN_ZERO_TRANSFORMS = 'rsgdZeroTransforms'

    Mode = GuideMode
    
    # -------- Description attributes
    
    descIdentifier = c.ItemFeatureType.GUIDE
    descUsername = 'Reference Guide'
    descPackages = ['rs.pkg.guideIF']

    # -------- Interface implementation
    
    @classmethod
    def test(cls, modoItem):
        """ Tests whether feature should be listed on a given item.
        
        Guide item feature is restricted to locator type items
        with the exception of guides - these obviously should be skipped.
        """
        if not LocatorSuperTypeItemFeature.test(modoItem):
            return False
        if GuideItem.testModoItem(modoItem):
            return False
        return True

    def onAdd(self):
        """ Actions performed when the feature is added to an item.
        
        * Zero transforms property will be set to True by default if any
        zero transforms have been found on an item.
        """
        locu = modox.LocatorUtils()
        if locu.hasAnyZeroTransforms(self.modoItem):
            self.zeroTransforms = True
    
    # -------- Custom methods
    
    @property
    def guide(self):
        """ Gets a guide item for an item.
        
        Returns
        -------
        GuideItem or None
        """
        graph = self.modoItem.itemGraph(self.GRAPH_NAME)
        try:
            return ReferenceGuideItem(graph.reverse(0))
        except LookupError:
            return None
        except TypeError:
            return None

    @guide.setter
    def guide(self, guideItem):
        """ Sets a guide for an item.
        
        Parameters
        ----------
        guideItem : GuideItem, modo.Item, None
            When None is passed the guide item association (if any) will be cleared.
        """
        if isinstance(guideItem, modo.Item):
            try:
                guideItem = ReferenceGuideItem(guideItem)
            except TypeError:
                return
        if not isinstance(guideItem, ReferenceGuideItem) and guideItem is not None:
            return

        self._removeConnections()

        if guideItem is None:
            return

        self._setConnection(guideItem.modoItem)

    @property
    def zeroTransforms(self):
        """ Returns zero transforms property value.

        Returns
        -------
        bool
        """
        return self.item.getChannelProperty(self.CHAN_ZERO_TRANSFORMS)

    @zeroTransforms.setter
    def zeroTransforms(self, state):
        """ Sets zero transforms property value.
        
        When True item's transforms will be zeroed each time the guide
        is applied to an item.
        Note that each time this property is set to False the zeroed
        transforms will be merged with primary ones and cleared out zero
        transform items will be removed from scene.

        Parameters
        ----------
        state : bool
        """
        self.item.setChannelProperty(self.CHAN_ZERO_TRANSFORMS, state)
        
        if state is False:
            # We're going to remove zeroed transforms but for this to work
            # all transform channels need to be unlocked.
            # We're sending an event first to ask for getting channels ready,
            # this really means that meta rig should unlock the channels.
            service.events.send(c.EventTypes.ITEM_CHAN_EDIT_BATCH_PRE, rig=self.item.rigRootItem)
            locu = modox.LocatorUtils()
            locu.mergeAllZeroTransforms(self.modoItem, removeZeroXfrmItems=True)
            service.events.send(c.EventTypes.ITEM_CHAN_EDIT_BATCH_POST)

    @property
    def availableGuides(self):
        """ Gets a list of available reference guides for an item.
        
        Returns
        -------
        list of GuideItem
        """
        rigRoot = self.item.rigRootItem
        moduleRoot = self.item.moduleRootItem
        modGuide = ModuleGuide(moduleRoot)
        
        return modGuide.referenceGuides
    
    def onRemove(self):
        """ Clear any graph links on remove.
        """
        self._removeConnections()

    # -------- Private methods

    def _removeConnections(self):
        """ Clears all connections to any guides from an item.
        """
        modox.ItemUtils.clearReverseGraphConnections(self.modoItem, self.GRAPH_NAME)

    def _setConnection(self, guideItem):
        """ Sets new connection from an item to the guide.
        """
        modox.ItemUtils.addForwardGraphConnections(guideItem, self.modoItem, self.GRAPH_NAME)