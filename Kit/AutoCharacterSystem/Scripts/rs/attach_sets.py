

from .attach_set import AttachmentSet
from .component_setups.meshes import RigidMeshesComponentSetup
from .component_setups.meshes import BindProxiesComponentSetup
from .items.rigid_mesh import RigidMeshItem
from .items.bind_proxy import BindProxyItem
from .resolutions import Resolutions
from . import const as c


class RigidMeshesAttachmentSet(AttachmentSet):

    descIdentifier = c.ComponentType.RIGID_MESHES
    descUsername = 'Rigid Meshes'
    descRootItemName = 'RigidMeshes'
    descAssemblyItemName = 'RigidMeshes'
    descComponentSetupClass = RigidMeshesComponentSetup
    descLookupGraph = c.Graph.ATTACHMENTS

    descTransformLinkType = c.TransformLinkType.DYNA_PARENT
    descMembersItemClass = RigidMeshItem

    def onItemAttach(self, modoItem):
        """ Attached rigid mesh should be added to all resolutions by default.
        """
        try:
            rigidMesh = RigidMeshItem(modoItem)
        except TypeError:
            return
        
        resolutions = Resolutions(self.rigRootItem)
        for res in resolutions:
            rigidMesh.addToResolution(res)


class BindProxiesAttachmentSet(AttachmentSet):

    descIdentifier = c.ComponentType.BIND_PROXIES
    descUsername = 'Bind Proxies'
    descRootItemName = 'BindProxies'
    descAssemblyItemName = 'BindProxies'
    descComponentSetupClass = BindProxiesComponentSetup
    descLookupGraph = c.Graph.ATTACHMENTS
    
    descTransformLinkType = c.TransformLinkType.DYNA_PARENT
    descMembersItemClass = BindProxyItem

    def onItemAttach(self, modoItem):
        """ Attached bind proxy should be added to current resolution by default.
        """
        try:
            proxyMesh = BindProxyItem(modoItem)
        except TypeError:
            return
        
        resolutions = Resolutions(self.rigRootItem)
        currentResolution = resolutions.currentResolution
        if currentResolution:
            proxyMesh.addToResolution(currentResolution)