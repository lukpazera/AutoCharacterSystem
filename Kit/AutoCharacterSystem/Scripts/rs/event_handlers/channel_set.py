

import lx

from ..event_handler import EventHandler
from ..controller_op import ControllerOperator
from ..const import EventTypes as e


class ChannelSetEventHandler(EventHandler):
    """ Handles events that affect channel sets UI.
    """

    descIdentifier = 'chanset'
    descUsername = 'Channel Sets'

    @property
    def eventCallbacks(self):
        return {e.RIG_DROPPED: self.event_rigDropped,
                e.RIG_NAME_CHANGED: self.event_rigNameChanged,
                e.MODULE_LOAD_POST: self.event_moduleLoadPost,
                e.MODULE_DELETE_PRE: self.event_moduleDeletePre,
                e.MODULE_NAME_CHANGED: self.event_moduleNameChanged,
                e.MODULE_SIDE_CHANGED: self.event_moduleNameChanged}

    def event_rigDropped(self, **kwargs):
        try:
            rig = kwargs['rig']
        except KeyError:
            return

        ctrlOp = ControllerOperator(rig)
        ctrlOp.createAllChannelSets(makeIndependent=False)

    def event_rigNameChanged(self, **kwargs):
        try:
            rig = kwargs['rig']
        except KeyError:
            return

        ctrlOp = ControllerOperator(rig)
        ctrlOp.updateAllChannelSetNames()

    def event_moduleNameChanged(self, **kwargs):
        try:
            module = kwargs['module']
        except KeyError:
            return

        ctrlOp = ControllerOperator(module.rigRootItem)
        ctrlOp.updateModuleChannelSetNames(module)

    def event_moduleLoadPost(self, **kwargs):
        try:
            module = kwargs['module']
        except KeyError:
            return

        ctrlOp = ControllerOperator(module.rigRootItem)
        ctrlOp.createModuleChannelSets(module)

    def event_moduleDeletePre(self, **kwargs):
        try:
            module = kwargs['module']
        except KeyError:
            return

        ctrlOp = ControllerOperator(module.rigRootItem)
        ctrlOp.deleteModuleChannelSets(module)