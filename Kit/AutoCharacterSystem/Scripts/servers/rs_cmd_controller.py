
import lx
import modo

import rs


class CmdControllerChannels(rs.base_CmdControllerChannels):
    """ Sets a set of guide channels that will be editable via controller.
    
    These will be either transform or user channels of an item.
    """

    descControllerClass = rs.Controller

rs.cmd.bless(CmdControllerChannels, 'rs.controller.controlledChannels')


class CmdControllerGuideChannelState(rs.base_CmdControllerChannelState):

    descControllerClass = rs.Controller
    
rs.cmd.bless(CmdControllerGuideChannelState, 'rs.controller.channelState')


class CmdControllerGuideChannelsFCL(rs.base_CmdControllerChannelsFCL):
    """ Generate command list with all the channels that a controller can drive.
    """

    descControllerClass = rs.Controller
    descChannelStateCommand = 'rs.controller.channelState'

rs.cmd.bless(CmdControllerGuideChannelsFCL, 'rs.controller.channelsFCL')
