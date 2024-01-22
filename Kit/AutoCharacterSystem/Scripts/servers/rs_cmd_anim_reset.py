
import lx
import modo
import modox

import rs


class CmdResetAnimation(rs.AnimCommand):
    """ Resets either selected controls or entire character.
    
    Reset is done by restoring default value to user channels.
    Transform channels get their value set to 0 or 1 (for scaling)
    but it might be better to change it to retrieve setup values
    for transform channels to support controllers that do not get
    their rest values zeroed - if there will be case for that.
    """

    ICON_RESET_RIG = 'rs.anim.resetChar'
    ICON_RESET_ITEM = 'rs.anim.reset'
    ICON_RESET_CHAN = 'rs.anim.resetChan'

    Scope = rs.AnimCommand.Scope

    ICON_MAP = {
    Scope.RIG: ICON_RESET_RIG,
    Scope.ITEM: ICON_RESET_ITEM,
    Scope.CHANNEL: ICON_RESET_CHAN}

    def cmd_Icon(self):
        return self.ICON_MAP[self.scope]

    def basic_ButtonName(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)

    def cmd_Tooltip(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDTOOLTIP, key)

    def execute(self, msg, flags):
        modox.ChannelUtils.resetChannelsToDefault(self.channelsToEdit)

    # -------- Private methods

    def _getMsgKey(self):
        scope = self.scope
        if scope == self.Scope.CHANNEL:
            type = 'Chan'
        elif scope == self.Scope.ITEM:
            type = 'Sel'
        else:
            type = 'Rig'

        return 'reset' + type

rs.cmd.bless(CmdResetAnimation, 'rs.anim.reset')