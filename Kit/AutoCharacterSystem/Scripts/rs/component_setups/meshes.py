
from ..component_setup import ComponentSetup
from ..const import ComponentSetupType
from ..const import Graph


class BindMeshesComponentSetup(ComponentSetup):
    
    descIdentifier = ComponentSetupType.BIND_MESHES
    descUsername = 'Bind Meshes'
    descPresetDescription = 'ACS Bind Meshes'
    descSelfDestroyWhenEmpty = True


class BindProxiesComponentSetup(ComponentSetup):
    
    descIdentifier = ComponentSetupType.BIND_PROXIES
    descUsername = 'Bind Proxies'
    descPresetDescription = 'ACS Bind Proxies'
    descSelfDestroyWhenEmpty = True


class RigidMeshesComponentSetup(ComponentSetup):
    
    descIdentifier = ComponentSetupType.RIGID_MESHES
    descUsername = 'Rigid Meshes'
    descPresetDescription = 'ACS Rigid Meshes'
    descSelfDestroyWhenEmpty = True
