

from .component import Component
from .component_setups.meshes import BindMeshesComponentSetup
from . import const as c


class BindMeshes(Component):
    
    descIdentifier = c.ComponentType.BIND_MESHES
    descUsername = 'Bind Meshes'
    descRootItemName = 'BindMeshes'
    descAssemblyItemName = 'BindMeshes'
    descComponentSetupClass = BindMeshesComponentSetup
    descLookupGraph = c.Graph.BIND_MESHES
    