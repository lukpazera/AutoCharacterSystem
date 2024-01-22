

import lx

from ..element_set import ElementSetFromMetaGroupItems
from ..const import MetaGroupType
from ..const import ElementSetType
from ..item_utils import ItemUtils
from ..resolutions import Resolutions
from ..log import log


class BindMeshesElementSet(ElementSetFromMetaGroupItems):
    
    descIdentifier = ElementSetType.BIND_MESHES
    descUsername = 'Bind Meshes'
    descMetaGroupIdentifier = MetaGroupType.BIND_MESHES


class ResolutionBindMeshesElementSet(ElementSetFromMetaGroupItems):
    """ Bind meshes belonging to a current resolution only.
    
    This is a dynamic set, it may change at any point.
    Therefore it's crucial that the resetVisible() resets all the bindmeshes
    but setVisible only works on ones from current resolution.
    
    """

    descIdentifier = ElementSetType.RESOLUTION_BIND_MESHES
    descUsername = 'Resolution Bind Meshes'
    descMetaGroupIdentifier = MetaGroupType.BIND_MESHES

    @property
    def elements(self):
        elements = super(ResolutionBindMeshesElementSet, self).elements
        filteredElements = []
        resop = Resolutions(self.rigRootItem)
        currentRes = resop.currentResolution
        if not currentRes:
            return elements
        
        for modoItem in elements:
            try:
                rigItem = ItemUtils.getItemFromModoItem(modoItem)
            except TypeError:
                continue
            try:
                result = rigItem.isInResolution(currentRes)
            except AttributeError:
                result = False
            
            if result:
                filteredElements.append(modoItem)
        
        return filteredElements

    def resetVisible(self):
        for item in super(ResolutionBindMeshesElementSet, self).elements:
            item.channel('visible').set(self.descVisibleDefault, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)