

import lx
import modo
import modox

import rs


c = rs.base_Controller
s = rs.Controller.ChannelState


class CmdControllerChannelsPreset(rs.base_CmdControllerChannelsPreset):
    
    descControllerClass = rs.Controller
    descXfrmChannelsStates = {True : s.ANIMATED,
                              False : s.LOCKED}
    descUserChannelsStates = {'anim': s.ANIMATED,
                      'static': s.STATIC,
                      'ignore': s.IGNORE}
    descUserPresetsLabels = {'anim': 'All Animated',
                             'static': 'All Static',
                             'ignore': 'All Ignored'}
            
rs.cmd.bless(CmdControllerChannelsPreset, 'rs.controller.chanPreset')