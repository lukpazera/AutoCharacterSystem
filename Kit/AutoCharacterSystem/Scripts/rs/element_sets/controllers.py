

import lx
import modo
import modox

from ..element_set import ElementSetFromMetaGroupItems
from ..item_features.controller import ControllerItemFeature as ControllerIF
from ..const import MetaGroupType
from ..const import ElementSetType
from ..const import ItemVisible


CHAN_IN_CONTEXT = 'rsacInContext'
IN_CONTEXT_VALUE = {ItemVisible.DEFAULT: False,
                    ItemVisible.YES: True,
                    ItemVisible.NO: False,
                    ItemVisible.NO_CHILDREN: False}


class ControllersElementSet(ElementSetFromMetaGroupItems):
    
    descIdentifier = ElementSetType.CONTROLLERS
    descUsername = 'Controllers'
    descMetaGroupIdentifier = MetaGroupType.CONTROLLERS

    def setVisible(self, state):
        """ Override set visible so it edits the in context channel as well.
        """
        val = IN_CONTEXT_VALUE[state]
        ElementSetFromMetaGroupItems.setVisible(self, state)
        for item in self._elementsWithFiltering:
            contextChan = item.channel(CHAN_IN_CONTEXT)
            if contextChan is not None:
                contextChan.set(val, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)


class ControllersFromSetElementSet(ElementSetFromMetaGroupItems):
    
    descIdentifier = ElementSetType.CONTROLLERS_SET
    descUsername = 'Controllers Selection Set'
    descMetaGroupIdentifier = MetaGroupType.CONTROLLERS

    @property
    def elements(self):
        # This gets elemetns from the controllers meta group
        elements = super(ControllersFromSetElementSet, self).elements
        filteredElements = []
        
        setName = self.rigRootItem.controllersSet
        if setName is None:
            # In default set all items that have visible in default set
            # set to True should be returned.
            filteredElements = []
            for modoItem in elements:
                try:
                    ctrl = ControllerIF(modoItem)
                except TypeError:
                    continue
                if ctrl.isVisibleInDefaultSet:
                    filteredElements.append(modoItem)
            return filteredElements
        
        filteredElements = []
        for modoItem in elements:
            if setName in modox.ItemUtils.getItemSelectionSets(modoItem):
                filteredElements.append(modoItem)
        
        return filteredElements

    def setVisible(self, state):
        """ Override set visible so it edits the in context channel as well.
        """
        val = IN_CONTEXT_VALUE[state]
        ElementSetFromMetaGroupItems.setVisible(self, state)
        for item in self._elementsWithFiltering:
            contextChan = item.channel(CHAN_IN_CONTEXT)
            if contextChan is not None:
                contextChan.set(val, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

    def resetVisible(self):
        """ Override standard reset visible as we need reset to work on ALL element set elements.
        
        Crappy implementation, needs to be reworked at some point.
        """
        contextVal = IN_CONTEXT_VALUE[self.descVisibleDefault]
        for item in super(ControllersFromSetElementSet, self).elements:
            visChan = item.channel('visible')
            if visChan is None:
                continue
            visChan.set(self.descVisibleDefault, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
            item.channel(CHAN_IN_CONTEXT).set(contextVal, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)