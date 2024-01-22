
""" Decorators are items that need to be visible in certain context.

    Decorators do not need to be of any particular type, they are defined
    via decorator item feature.
"""


import lx
import modo
import modox

from . import const as c
from .const import EventTypes as e
from .meta_group import MetaGroup
from .item_feature import LocatorSuperTypeItemFeature
from .element_set import ElementSetFromMetaGroupItems
from .event_handler import EventHandler
from .log import log


class DecoratorIF(LocatorSuperTypeItemFeature):

    CONTEXTS_SETTING = 'deccxt'

    # -------- Description attributes
    
    descIdentifier = c.ItemFeatureType.DECORATOR
    descUsername = 'Decorator'

    # -------- Public methods
    
    def onAdd(self):
        pass
    
    def onRemove(self):
        self.clearContexts()
    
    def addContext(self, context):
        contextNames = self.item.settings.get(self.CONTEXTS_SETTING, [])
        if context in contextNames:
            return
        contextNames.append(context)
        self.item.settings.set(self.CONTEXTS_SETTING, contextNames)
    
    def removeContext(self, context):
        contextNames = self.item.settings.get(self.CONTEXTS_SETTING, [])
        try:
            contextNames.remove(context)
        except ValueError:
            return
        if contextNames:
            self.item.settings.set(self.CONTEXTS_SETTING, contextNames)
        else:
            self.clearContexts()
        
    def clearContexts(self):
        self.item.settings.delete(self.CONTEXTS_SETTING)

    @property
    def contexts(self):
        """ Gets a list of contexts that this decorator should be visible in.

        Returns
        -------
        list of str
            The list will be empty if decorator is not enabled in any of the contexts.
        """
        return self.item.settings.get(self.CONTEXTS_SETTING, [])


class DecoratorMG(MetaGroup):
    
    descIdentifier = c.MetaGroupType.DECORATORS
    descUsername = 'Decorators'
    descModoGroupType = '' # standard group
    
    def onItemAdded(self, modoItem):
        try:
            decor = DecoratorIF(modoItem)
        except TypeError:
            return

        self.modoGroupItem.addItems(modoItem)

    def onItemChanged(self, modoItem):
        try:
            decor = DecoratorIF(modoItem)
        except TypeError:
            self.modoGroupItem.removeItems(modoItem)
            return

        self.modoGroupItem.addItems(modoItem)


class DecoratorsElementSet(ElementSetFromMetaGroupItems):
    """ Decorators element set.
    """

    descIdentifier = c.ElementSetType.DECORATORS
    descUsername = 'Decorators'
    descMetaGroupIdentifier = c.MetaGroupType.DECORATORS

    def setVisibleForContext(self, state, contextObject):
        """ Extra function.
        """
        for item in self._elementsWithFiltering:
            visChan = item.channel('visible')
            if visChan is None:
                continue
            
            try:
                decoratorIF = DecoratorIF(item)
            except TypeError:
                continue
            
            if contextObject.descIdentifier in decoratorIF.contexts and not decoratorIF.item.hidden:
                visChan.set(state, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)


class DecoratorEventHandler(EventHandler):

    descIdentifier = 'decor'
    descUsername = 'Decorators'
  
    @property
    def eventCallbacks(self):
        return {e.CONTEXT_RIG_VIS_RESET: self.event_VisibilityReset,
                e.CONTEXT_RIG_VIS_SET: self.event_VisibilitySet,
                }

    def event_VisibilityReset(self, **kwargs):
        try:
            context = kwargs['context']
        except KeyError:
            return
        try:
            rig = kwargs['rig']
        except KeyError:
            return
        
        decoratorsSet = rig[c.ElementSetType.DECORATORS]
        decoratorsSet.resetVisible()

    def event_VisibilitySet(self, **kwargs):
        try:
            context = kwargs['context']
        except KeyError:
            return
        try:
            rig = kwargs['rig']
        except KeyError:
            return

        decoratorsSet = rig[c.ElementSetType.DECORATORS]
        decoratorsSet.setVisibleForContext(c.ItemVisible.YES, context)
        