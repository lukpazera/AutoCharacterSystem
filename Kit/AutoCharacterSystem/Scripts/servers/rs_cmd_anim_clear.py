

import lx
import modo
import modox

import rs


class CmdClearAnimation(rs.AnimCommand):
    """ Clears animation from selected controllers or entire rig.
    """

    ARG_MODE = 'mode'

    MODE_REMOVE = 'remove'
    MODE_CLEAR = 'clear'

    ICON_REMOVE_RIG = 'rs.anim.removeChar'
    ICON_REMOVE_ITEM = 'rs.anim.remove'
    ICON_REMOVE_CHAN = 'rs.anim.removeChan'
    
    ICON_CLEAR_RIG = 'rs.anim.clearChar'
    ICON_CLEAR_ITEM = 'rs.anim.clear'
    ICON_CLEAR_CHAN = 'rs.anim.clearChan'
    
    Scope = rs.AnimCommand.Scope

    ICON_MAP = {
    MODE_REMOVE+Scope.RIG: ICON_REMOVE_RIG,
    MODE_REMOVE+Scope.ITEM: ICON_REMOVE_ITEM,
    MODE_REMOVE+Scope.CHANNEL: ICON_REMOVE_CHAN,
    MODE_CLEAR+Scope.RIG: ICON_CLEAR_RIG,
    MODE_CLEAR+Scope.ITEM: ICON_CLEAR_ITEM,
    MODE_CLEAR+Scope.CHANNEL: ICON_CLEAR_CHAN,
    }

    def arguments(self):
        baseArgs = rs.AnimCommand.arguments(self)
    
        mode = rs.cmd.Argument(self.ARG_MODE, 'string')
        mode.defaultValue = self.MODE_CLEAR

        args = [mode]
        args.extend(baseArgs)
        return args

    def cmd_Icon(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        return self.ICON_MAP[mode+self.scope]

    def basic_ButtonName(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)

    def cmd_Tooltip(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDTOOLTIP, key)

    def execute(self, msg, flags):
        mode = self.getArgumentValue(self.ARG_MODE)

        if mode == self.MODE_CLEAR:
            channels = self.channelsToEdit
            modox.ChannelUtils.removeAnimation(channels)
            modox.ChannelUtils.resetChannelsToDefault(channels)
        elif mode == self.MODE_REMOVE:
            modox.ChannelUtils.removeAnimation(self.channelsToEdit)

    # -------- Private methods

    def _getMsgKey(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        token1 = 'clear'
        if mode == self.MODE_REMOVE:
            token1 = 'rem'

        scope = self.scope
        if scope == self.Scope.CHANNEL:
            type = 'Chan'
        elif scope == self.Scope.ITEM:
            type = 'Sel'
        else:
            type = 'Rig'

        return token1+type

rs.cmd.bless(CmdClearAnimation, 'rs.anim.clear')