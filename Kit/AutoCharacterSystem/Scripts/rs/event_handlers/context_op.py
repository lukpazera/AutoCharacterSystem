

from ..event_handler import EventHandler
from ..const import EventTypes as e
from ..context_op import ContextOperator
from ..scene import Scene


class ContextOperatorEventHandler(EventHandler):
    """ Handles events concerning contexts.
    """

    descIdentifier = 'cxtop'
    descUsername = 'Context Operator'

    @property
    def eventCallbacks(self):
        return {e.EDIT_RIG_CHANGED: self.event_editRigChanged
                }

    def event_editRigChanged(self, **kwargs):
        contextOp = ContextOperator(Scene())
        if contextOp.current.edit:
            contextOp.refreshCurrent()