
""" Event handler for deformers stack.
"""


import modo

from ..event_handler import EventHandler
from ..const import EventTypes as e
from ..log import log
from ..deform_stack import DeformStack


class DeformStackEventHandler(EventHandler):
    """ Handles events concerning deform stack.
    """

    descIdentifier = 'dfrmstack'
    descUsername = 'Deformers Stack'
  
    @property
    def eventCallbacks(self):
        return {e.MODULE_LOAD_POST: self.event_moduleLoadPost,
                e.MODULE_SAVE_PRE: self.event_moduleSavePre,
                e.MODULE_SAVE_POST: self.event_moduleSavePost
                }

    def event_moduleLoadPost(self, **kwargs):
        """ Called after module was loaded and added to rig.
        """
        try:
            module = kwargs['module']
        except KeyError:
            return

        deformFolders = module.getModoItemsOfType('deformFolder')
        if not deformFolders:
            return

        try:
            deformStack = DeformStack(module.rigRootItem)
        except TypeError:
            return
        
        deformStack.restoreStackOrder(deformFolders)
        
    def event_moduleSavePre(self, **kwargs):
        """ Called right before module preset is saved.
        """
        try:
            module = kwargs['module']
        except KeyError:
            return

        try:
            deformStack = DeformStack(module.rigRootItem)
        except TypeError:
            return
        
        deformStack.storeStackOrder()
    
    def event_moduleSavePost(self, **kwargs):
        """ Called right after module preset was saved.
        """
        try:
            module = kwargs['module']
        except KeyError:
            return
        
        try:
            deformStack = DeformStack(module.rigRootItem)
        except TypeError:
            return
        
        deformStack.clearStackOrder()

    # -------- Private methods