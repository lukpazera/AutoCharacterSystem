
import lx
import modo

import rs


class CmdControllerChanPresetChoice(rs.base_CmdControllerChanPresetChoice):

    descControllerClass = rs.Controller
    descFormIdentifier = 'rs.controllerChannelStatePresets:sheet'

rs.cmd.bless(CmdControllerChanPresetChoice, 'rs.controller.chanPresetChoice')

