
""" Temporary folder component implementation module.

    Temporary folder is a folder in rig hierarchy under which temporary
    rig items can be placed. Items in internal folder can be removed at any time
    without any harm to the rig.
    
    The folder item itself is always visible and is also used to perform any extra drawing
    that the rig may need to do.
"""


from .component_op import ComponentOperator
from .component import Component
from .component_setup import ComponentSetup
from . import const as c


class TemporaryFolderSetup(ComponentSetup):
    
    descIdentifier = c.ComponentSetupType.TEMPORARY
    descUsername = 'Temporary'
    descPresetDescription = 'ACS Temporary Content'
    descSelfDestroyWhenEmpty = True


class TemporaryFolder(Component):
    
    descIdentifier = c.ComponentType.TEMPORARY
    descUsername = 'Temporary'
    descRootItemName = 'Temporary'
    descAssemblyItemName = 'Temporary'
    descComponentSetupClass = TemporaryFolderSetup


class TemporaryFolderOperator(ComponentOperator):
    
    descComponentClass = TemporaryFolder
