
from ..component_setup import ComponentSetup
from ..const import ComponentType


class ModuleComponentSetup(ComponentSetup):
    
    descIdentifier = ComponentType.MODULE
    descUsername = 'Module'
    descPresetDescription = 'ACS Module'
    descOnCreateDropScript = 'rs_drop_module'