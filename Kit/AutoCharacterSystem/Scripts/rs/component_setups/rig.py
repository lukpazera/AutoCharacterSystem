
import rs.component_setup
from ..const import ComponentSetupType


class RigComponentSetup(rs.component_setup.ComponentSetup):
    
    descIdentifier = ComponentSetupType.RIG
    descUsername = 'Rig'
    descPresetDescription = 'ACS Rig'
    descOnCreateDropScript = 'rs_drop_rig'
