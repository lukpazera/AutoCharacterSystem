
import lx
import modo

import rs


class CmdControllerChannels(rs.base_CmdControllerChannels):
    """ Sets a set of guide channels that will be editable via controller.
    
    These will be either transform or user channels of an item.
    """

    descControllerClass = rs.ControllerGuide

rs.cmd.bless(CmdControllerChannels, 'rs.controllerGuide.controlledChannels')


class CmdControllerGuideChannelState(rs.base_CmdControllerChannelState):

    descControllerClass = rs.ControllerGuide
    
rs.cmd.bless(CmdControllerGuideChannelState, 'rs.controllerGuide.channelState')


class CmdControllerGuideChannelsFCL(rs.base_CmdControllerChannelsFCL):
    """ Generate command list with all the channels that a controller can drive.
    """

    descControllerClass = rs.ControllerGuide
    descChannelStateCommand = 'rs.controllerGuide.channelState'

rs.cmd.bless(CmdControllerGuideChannelsFCL, 'rs.controllerGuide.channelsFCL')


class CmdControllerChanPresetChoice(rs.base_CmdControllerChanPresetChoice):
    
    descControllerClass = rs.ControllerGuide
    descFormIdentifier = 'rs.guideControllerChannelStatePresets:sheet'

rs.cmd.bless(CmdControllerChanPresetChoice, 'rs.controllerGuide.chanPresetChoice')


class CmdControllerChannelsPreset(rs.base_CmdControllerChannelsPreset):
    
    s = rs.ControllerGuide.ChannelState
    
    descControllerClass = rs.ControllerGuide
    descXfrmChannelsStates = {True : s.EDIT,
                              False : s.LOCKED}
    descUserChannelsStates = {'edit': s.EDIT,
                              'ignore': s.IGNORE}
    descUserPresetsLabels = {'edit': 'All Editable',
                             'ignore': 'All Ignored'}
            
rs.cmd.bless(CmdControllerChannelsPreset, 'rs.controllerGuide.chanPreset')