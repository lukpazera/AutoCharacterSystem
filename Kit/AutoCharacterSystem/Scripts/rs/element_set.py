

import lx
import modox

from . import const as c
from .sys_component import SystemComponent
from .meta_rig import MetaRig
from .item import Item
from .log import log as log
from .debug import debug


class ElementSet(SystemComponent):
    """ Element set is a collection of items or channels of a rig.
    
    Parameters
    ----------
    rigRoot : RootItem

    Properties
    ----------
    elements
         This property has to be implemented and it needs to return
         a list of elements that this set includes.
         Items should be returned as modo.Item objects.
    
    Methods
    -------
    getElementsFilteredByModule
        Needs to return a list of elements filtered by a module passed
        as an argument.
    """

    descIdentifier = ''
    descUsername = ''

    # -------- Interface
    
    @property
    def elements(self):
        return []

    def getElementsFilteredByModule(self, module):
        return []

    @property
    def rigRootItem(self):
        return self._root

    def setModuleFilter(self, module):
        """ Sets filtering for the element set.
        
        Basically when filtering is on element set methods
        should return content that's limited to the module passed
        as parameter.
        """
        self._moduleFilter = module

    # -------- System Component
    
    @classmethod
    def sysType(cls):
        return c.SystemComponentType.ELEMENT_SET
    
    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
    
    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Element Set'

    # -------- Private methods
    
    @property
    def _elementsWithFiltering(self):
        """ Gets list of elements considering module filtering.
        
        This should be used in every operation on elements that should
        take module filtering into account.

        Returns
        -------
        [modo.Item]
        """
        if self._moduleFilter is not None:
            return self.getElementsFilteredByModule(self._moduleFilter)
        else:
            return self.elements

    def __init__(self, rigRoot):
        self._root = rigRoot
        try:
            self.init()
        except AttributeError:
            pass
        self._moduleFilter = None


class ItemsElementSet(ElementSet):
    """ Item elements set contains items only.
    
    This class offers a few extra methods that allow for dealing
    with item properties: visibility and selectability.
    """

    descVisibleDefault = c.ItemVisible.DEFAULT
    descSelectableDefault = c.TriState.DEFAULT
    descLockedDefault = c.TriState.DEFAULT

    def getElementsFilteredByModule(self, module):
        """ Gets list of elements filtered by module.
        """
        filtered = []
        for el in self.elements:
            try:
                rigItem = Item.getFromModoItem(el)
            except TypeError:
                continue
            if module == rigItem.moduleRootItem:
                filtered.append(el)
        return filtered

    def setVisible(self, state):
        """ Sets all set items visibility to a given state.
        
        The default implementation is that visibility is changed on each
        item directly in its properties.

        Parameters
        ----------
        state : const.ItemVisible
            One of four possible visibility values.
        """
        for item in self._elementsWithFiltering:
            visChan = item.channel('visible')
            if visChan is not None:

                # If state is to show an item and the item is set to hidden in rig properties
                # we skip this item (we assume it has default vis state and is not visible).
                if state == c.ItemVisible.YES and Item.isHiddenFast(item):
                    continue

                visChan.set(state, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

            else:
                if debug.output:
                    log.out('%s item has no "visible" channel!' % item.name, log.MSG_ERROR)

    def resetVisible(self):
        """ Resets all items visibility to default set in descVisibleDefault.
        """
        self.setVisible(self.descVisibleDefault)
    
    def setSelectable(self, state):
        """ Sets all set items selectability to a given state.
        
        The default implementation is that selectability is changed on each
        item directly in its properties.

        Parameters
        ----------
        state : const.TriState
            One of three possible constants.
        """
        for item in self._elementsWithFiltering:
            item.channel('select').set(state, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

    def resetSelectable(self):
        """ Resets all items selectability to default set in descSelectableDefault.
        """
        self.setSelectable(self.descSelectableDefault)


class ElementSetFromMetaGroupItems(ItemsElementSet):
    """ Element set that takes elements from meta group items.
    
    This class has the elements method pre-implemented. All you
    need is provide meta group identifier as attribute.
    
    Raises
    ------
    TypeError
        If meta group tied to this set does not exist.
    """

    descMetaGroupIdentifier = ''

    @property
    def descVisibleDefault(self):
        """ Default visibility value is taken from meta group.
        
        Implementing this as property overrides class level attribute.
        """
        return self._metaGroup.descVisibleDefault

    @property
    def descSelectableDefault(self):
        """ Default selectability value is taken from meta group.
        
        Implementing this as property overrides class level attribute.
        """
        return self._metaGroup.descSelectableDefault

    def init(self):
        self._metaRig = MetaRig(self.rigRootItem)
        try:
            self._metaGroup = self._metaRig.getGroup(self.descMetaGroupIdentifier)
        except LookupError:
            raise TypeError

    @property
    def elements(self):
        return self._metaGroup.items

    def setSelectable(self, state):
        """ Sets element set items selectable state.
        
        In element set based on meta group this changes the selectable
        property of the group rather then its individual items.
        
        Parameters
        ----------
        state : const.TriState
        """
        self._metaGroup.membersSelectable = state

    def resetSelectable(self):
        """ Resets all items selectability to default set in the meta group.
        """
        self._metaGroup.membersSelectable = self._metaGroup.descSelectableDefault

    def setRender(self, state):
        self._metaGroup.membersRender = state

    def resetRender(self):
        self._metaGroup.membersRender= self._metaGroup.descRenderDefault

    def setLocked(self, state):
        self._metaGroup.membersLocked = state
    
    def resetLocked(self):
        self._metaGroup.membersLocked = self._metaGroup.descLockedDefault
