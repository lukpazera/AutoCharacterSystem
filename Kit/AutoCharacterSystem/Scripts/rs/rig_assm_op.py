

import modo
import modox
from .util import run


class RigAssemblyOperator(object):
    """ Allows for performing operations on rig assemblies directly.
    """
    
    def clearAll(self):
        """ Clears all rig assemblies from their content.
        
        Assemblies themselves are left intact since they may have inputs//outputs
        that connect rig items.
        
        This makes the rig invisible in schematic but much lighter at the same time.
        The rig has to be locked from editing (apart from animation) afterwards or bad things will happen.
        """
        rootAssmModoItem = self._rig.setup.rootAssembly
        allAssms = modox.Assembly.getSubassemblies(rootAssmModoItem)

        # Clear all assemblies contents
        for assmModoItem in allAssms:
            run('group.edit mode:clr type:all item:{%s}' % assmModoItem.id)

    # -------- Private methods

    def __init__(self, rig):
        self._rig = rig
