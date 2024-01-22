import lx
import modo
import modox

import rs


class CmdKeyframeInfo(rs.AnimCommand):

    ICON_RIG = 'rs.anim.infoChar'
    ICON_ITEM = 'rs.anim.info'
    ICON_CHAN = 'rs.anim.infoChan'

    Scope = rs.AnimCommand.Scope

    ICON_MAP = {
        Scope.RIG: ICON_RIG,
        Scope.ITEM: ICON_ITEM,
        Scope.CHANNEL: ICON_CHAN}

    def cmd_Icon(self):
        return self.ICON_MAP[self.scope]

    def basic_ButtonName(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)

    def cmd_Tooltip(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDTOOLTIP, key)

    def execute(self, msg, flags):
        envCount = 0
        keyCount = 0

        for channel in self.channelsToEdit:
            try:
                envelope = channel.envelope
            except LookupError:
                continue
            envCount += 1
            keyCount += envelope.keyframes.numKeys

        if self.scope == self.Scope.RIG:
            scopeMsgKey = 'keyinfoScopeRig'
        elif self.scope == self.Scope.ITEM:
            scopeMsgKey = 'keyinfoScopeItem'
        elif self.scope == self.Scope.CHANNEL:
            scopeMsgKey = 'keyinfoScopeChannel'
        else:
            scopeMsgKey = 'keyinfoScopeRig'

        scopeMsg = modox.Message.getMessageTextFromTable(rs.c.MessageTable.DIALOG, scopeMsgKey)
        msg = modox.Message.getMessageTextFromTable(rs.c.MessageTable.DIALOG, 'keyinfoMsg', [keyCount, envCount, scopeMsg])
        title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.DIALOG, 'keyinfoTitle')
        modo.dialogs.alert(title, msg, 'info')

    # -------- Private methods

    def _getMsgKey(self):
        scope = self.scope
        if scope == self.Scope.CHANNEL:
            type = 'Chan'
        elif scope == self.Scope.ITEM:
            type = 'Sel'
        else:
            type = 'Rig'

        return 'keyInfo'+type

rs.cmd.bless(CmdKeyframeInfo, 'rs.anim.keyInfo')