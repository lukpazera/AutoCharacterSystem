

import lx
import modo
import modox

from ..xfrm_link_setup import TransformLinkSetup
from ..const import TransformLinkType as t
from ..log import log
from ..item import Item


class DynaParentTransformLinkSetup(TransformLinkSetup):
    """
    Dynamic parenting transform link setup.

    This setup is used to establish a transform link between two items.
    Transform link is based on the dynamic parent modifier.

    Although this setup is using dynamic parent modifier it's not meant to be animated.
    Dynamic parent is on fixed index of 1.

    To make the link work with guide updates parent is switched to 0 (world) before guide update.
    Then when new guide position is applied the link is set to 1 again.
    """
    # -------- Attribute channels
    
    descIdentifier = t.DYNA_PARENT
    descUsername = 'Dynamic Parent'
    descInheritScale = True

    # -------- Custom methods

    @property
    def dynamicParentSetup(self):
        """
        Gets dynamic parenting setup object for this transform link.

        Returns
        -------
        modox.DynamicParentSetup
        """
        return modox.DynamicParentSetup(self.modoItem)

    # -------- Public methods

    def onNew(self, compensation=True):
        dynaParentSetup = modox.DynamicParentSetup.new(self.modoItem,
                                                       self.targetModoItem,
                                                       name=self._generateName()+"_XfrmLink",
                                                       compensation=compensation,
                                                       ignoreScale=not self.descInheritScale)
        dynaParentSetup.draw = False

    def onRemove(self):
        dynaParentSetup = modox.DynamicParentSetup(self.modoItem)
        dynaParentSetup.setParent(0, action=lx.symbol.s_ACTIONLAYER_SETUP)
        dynaParentSetup.selfDelete()

    def onAddToSetup(self):
        dynaParentSetup = modox.DynamicParentSetup(self.modoItem)
        return [dynaParentSetup.dynamicParentModifier]
    
    def onAddToTargetSetup(self):
        dynaParentSetup = modox.DynamicParentSetup(self.modoItem)
        return dynaParentSetup.matrixComposerModifiers
        
    @property
    def setupItems(self):
        dynaParentSetup = modox.DynamicParentSetup(self.modoItem)
        return dynaParentSetup.setupItems

    def onDeactivate(self):
        """
        Deactivating the transform link switches parent to world space.
        The assumption is that the transform linked item is in world space when not linked.
        """
        dynaParentSetup = modox.DynamicParentSetup(self.modoItem)
        dynaParentSetup.setParent(0, action=lx.symbol.s_ACTIONLAYER_SETUP)
    
    def onReactivate(self):
        """
        Reactivting the link switches its parent back to index of 1 (with compensation).
        """
        dynaParentSetup = modox.DynamicParentSetup(self.modoItem)
        dynaParentSetup.setParent(1, action=lx.symbol.s_ACTIONLAYER_SETUP)
    
    @classmethod
    def clearFromItemIfNotValid(cls, modoItem):
        """ Clears setup from given item if the setup is not fully there.
        """
        dynaParentSetup = modox.DynamicParentSetup(modoItem)
        if not dynaParentSetup.isFullSetup:
            dynaParentSetup.selfDelete()

    # -------- Private methods

    def _generateName(self):
        try:
            rigItem = Item.getFromModoItem(self.modoItem)
        except TypeError:
            return self.modoItem.name.replace(' ', '_')

        try:
            return rigItem.referenceUserName.replace(' ', '_')
        except TypeError:
            pass
        return self.modoItem.name.replace(' ', '_')


class DynaParentNoScaleTransformLinkSetup(DynaParentTransformLinkSetup):

    descIdentifier = t.DYNA_PARENT_NO_SCALE
    descUsername = 'Dynamic Parent No Scale'
    descInheritScale = False

