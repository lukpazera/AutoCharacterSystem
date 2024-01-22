
import lx
import lxu
import modo
import modox

import rs


class CmdAnimKeyEdit(rs.AnimCommand):
    """ Sets or removes keys.
    
    Keys will be edited either for currently selected controllers
    or for all controllers of all selected rigs if there is no current
    selection.
    """

    ARG_MODE = 'mode'

    MODE_ADD = 'add'
    MODE_REMOVE = 'remove'

    ICON_KEY_RIG = 'rs.anim.keyChar'
    ICON_KEY_ITEM = 'rs.anim.key'
    ICON_KEY_CHAN = 'rs.anim.keyChan'
    
    ICON_UNKEY_RIG = 'rs.anim.unkeyChar'
    ICON_UNKEY_ITEM = 'rs.anim.unkey'
    ICON_UNKEY_CHAN = 'rs.anim.unkeyChan'

    Scope = rs.AnimCommand.Scope

    ICON_MAP = {
    MODE_ADD+Scope.RIG: ICON_KEY_RIG,
    MODE_ADD+Scope.ITEM: ICON_KEY_ITEM,
    MODE_ADD+Scope.CHANNEL: ICON_KEY_CHAN,
    MODE_REMOVE+Scope.RIG: ICON_UNKEY_RIG,
    MODE_REMOVE+Scope.ITEM: ICON_UNKEY_ITEM,
    MODE_REMOVE+Scope.CHANNEL: ICON_UNKEY_CHAN,
    }

    def arguments(self):
        baseArgs = rs.AnimCommand.arguments(self)

        mode = rs.cmd.Argument(self.ARG_MODE, 'string')
        mode.defaultValue = self.MODE_ADD
        
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

        for chan in self.channelsToEdit:
            chanString = "%s:%s" % (chan.item.id, chan.name)
            lx.eval('!channel.key mode:%s channel:{%s}' % (mode, chanString))

    # -------- Private methods

    def _getMsgKey(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        token1 = 'key'
        if mode == self.MODE_REMOVE:
            token1 = 'unkey'

        scope = self.scope
        if scope == self.Scope.CHANNEL:
            type = 'Chan'
        elif scope == self.Scope.ITEM:
            type = 'Sel'
        else:
            type = 'Rig'

        return token1+type

rs.cmd.bless(CmdAnimKeyEdit, "rs.anim.keyEdit")
