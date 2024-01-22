

import lx

from ..element_set import ElementSetFromMetaGroupItems
from ..const import MetaGroupType
from ..const import ElementSetType
from ..item_utils import ItemUtils
from ..resolutions import Resolutions


class RigidMeshesElementSet(ElementSetFromMetaGroupItems):
    
    descIdentifier = ElementSetType.RIGID_MESHES
    descUsername = 'Rigid Meshes'
    descMetaGroupIdentifier = MetaGroupType.RIGID_MESHES


class ResolutionRigidMeshesElementSet(ElementSetFromMetaGroupItems):
    """ Rigid meshes belonging to a current resolution only.

    This is a dynamic set, it may change at any point.
    Therefore it's crucial that the resetVisible() resets all the meshes
    but setVisible only works on ones from current resolution.

    """

    descIdentifier = ElementSetType.RESOLUTION_RIGID_MESHES
    descUsername = 'Resolution Rigid Meshes'
    descMetaGroupIdentifier = MetaGroupType.RIGID_MESHES

    @property
    def elements(self):
        elements = super(ResolutionRigidMeshesElementSet, self).elements
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
        for item in super(ResolutionRigidMeshesElementSet, self).elements:
            item.channel('visible').set(self.descVisibleDefault, time=0.0, key=False,
                                        action=lx.symbol.s_ACTIONLAYER_SETUP)


class BindProxiesElementSet(ElementSetFromMetaGroupItems):
    
    descIdentifier = ElementSetType.BIND_PROXIES
    descUsername = 'Bind Proxies'
    descMetaGroupIdentifier = MetaGroupType.BIND_PROXIES


class ResolutionBindProxiesElementSet(ElementSetFromMetaGroupItems):
    """ Bind proxies belonging to a current resolution only.
    
    This is a dynamic set, it may change at any point.
    Therefore it's crucial that the resetVisible() resets all the meshes
    but setVisible only works on ones from current resolution.
    
    """

    descIdentifier = ElementSetType.RESOLUTION_BIND_PROXIES
    descUsername = 'Resolution Bind Proxies'
    descMetaGroupIdentifier = MetaGroupType.BIND_PROXIES

    @property
    def elements(self):
        elements = super(ResolutionBindProxiesElementSet, self).elements
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
        for item in super(ResolutionBindProxiesElementSet, self).elements:
            item.channel('visible').set(self.descVisibleDefault, time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
