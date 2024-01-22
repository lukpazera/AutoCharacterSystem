

import lx
import modo
from modox import TransformToolsUtils
from modox import ChannelUtils

from ..const import ItemFeatureType
from ..const import EventTypes as e
from ..core import service
from ..controller_if import Controller
from .. import const as c


class ControllerChannelState(object):
    EDIT = 'e'
    LOCKED = 'l'
    IGNORE = 'i'
    

class ControllerGuideItemFeature(Controller):
    """ Feature for guides that are editable by user.
    """

    ChannelState = ControllerChannelState

    # -------- Description attributes
    
    descIdentifier = ItemFeatureType.CONTROLLER_GUIDE
    descUsername = 'Guide Controller'
    descExclusiveItemType = c.RigItemType.GUIDE
    
    descDefaultChannelState = ChannelState.IGNORE
    descChannelStatesClass = ControllerChannelState
    descChannelStatesUsernames = {ChannelState.EDIT: 'Editable',
                                  ChannelState.LOCKED: 'Locked',
                                  ChannelState.IGNORE: 'Ignore'}
    descChannelStatesUIOrder = [ChannelState.IGNORE,
                                ChannelState.EDIT,
                                ChannelState.LOCKED]

    # -------- Public methods
    
    @property
    def editChannels(self):
        """ Gets list of channels that can be edited by user.

        Returns
        -------
        list : modo.Channel
        """
        return self._getChannelsWithState(self.ChannelState.EDIT)

    @property
    def editChannelNames(self):
        """ Gets list of names of channels that can be edited by user.

        Returns
        -------
        list : str
        """
        return [channel.name for channel in self.editChannels]

    @property
    def lockedChannels(self):
        """ Gets list of channels that should be locked.

        Returns
        -------
        list : modo.Channel
        """
        return self._getChannelsWithState(self.ChannelState.LOCKED)

    @property
    def channelSetChannels(self):
        return self.editChannels