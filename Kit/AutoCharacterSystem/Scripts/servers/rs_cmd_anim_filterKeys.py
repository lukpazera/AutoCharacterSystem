

import lx
import lxu
import modo
import modox

import rs

from modox import channel_lxe


class CmdAnimFilterKeys(rs.AnimCommand):

    ARG_REMOVE_ENVELOPES = 'removeEnv'

    ICON_FILTER_KEY_RIG = 'rs.anim.filterKeyChar'
    ICON_FILTER_KEY_ITEM = 'rs.anim.filterKey'
    ICON_FILTER_KEY_CHAN = 'rs.anim.filterKeyChan'

    ICON_FILTER_ENV_RIG = 'rs.anim.filterEnvChar'
    ICON_FILTER_ENV_ITEM = 'rs.anim.filterEnv'
    ICON_FILTER_ENV_CHAN = 'rs.anim.filterEnvChan'

    Scope = rs.AnimCommand.Scope

    ICON_MAP = {
        'False' + Scope.RIG: ICON_FILTER_KEY_RIG,
        'False' + Scope.ITEM: ICON_FILTER_KEY_ITEM,
        'False' + Scope.CHANNEL: ICON_FILTER_KEY_CHAN,
        'True' + Scope.RIG: ICON_FILTER_ENV_RIG,
        'True' + Scope.ITEM: ICON_FILTER_ENV_ITEM,
        'True' + Scope.CHANNEL: ICON_FILTER_ENV_CHAN,
    }

    def arguments(self):
        baseArgs = rs.AnimCommand.arguments(self)

        mode = rs.cmd.Argument(self.ARG_REMOVE_ENVELOPES, 'boolean')
        mode.defaultValue = True

        args = [mode]
        args.extend(baseArgs)
        return args

    def cmd_Icon(self):
        removeEnvs = str(self.getArgumentValue(self.ARG_REMOVE_ENVELOPES))
        return self.ICON_MAP[removeEnvs + self.scope]

    def basic_ButtonName(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)

    def cmd_Tooltip(self):
        key = self._getMsgKey()
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDTOOLTIP, key)

    def applyEditActionPost(self):
        return True

    def execute(self, msg, flags):
        """
        Note that this command is using old ACS2 code
        that is placed into modox (channel_lxe).
        """
        removeEnvs = self.getArgumentValue(self.ARG_REMOVE_ENVELOPES)

        scene = lx.object.Scene(lxu.select.SceneSelection().current())
        selection_service = lx.service.Selection()

        chanUtils = channel_lxe.ChannelUtils()
        chanRead = lx.object.ChannelRead(scene.Channels(lx.symbol.s_ACTIONLAYER_EDIT, selection_service.GetTime()))
        chanWrite = lx.object.ChannelWrite(scene.Channels(lx.symbol.s_ACTIONLAYER_EDIT, selection_service.GetTime()))

        deletedKeys = 0
        deletedEnvelopes = 0

        for channel in self.channelsToEdit:
            r = chanUtils.FilterStaticKeys(chanRead, chanWrite, channel.item.internalItem, channel.index, removeEnvs)
            # result -1 means that entire envelope was deleted
            if r >= 0:
                deletedKeys += r
            else:
                deletedEnvelopes += 1

        if removeEnvs:
            title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.DIALOG, 'envfilterTitle')
            msg = modox.Message.getMessageTextFromTable(rs.c.MessageTable.DIALOG, 'envfilterMsg', [deletedEnvelopes, deletedKeys])
        else:
            title = modox.Message.getMessageTextFromTable(rs.c.MessageTable.DIALOG, 'keyfilterTitle')
            msg = modox.Message.getMessageTextFromTable(rs.c.MessageTable.DIALOG, 'keyfilterMsg', [deletedKeys])

        modo.dialogs.alert(title, msg, 'info')

    # -------- Private methods

    def _getMsgKey(self):
        removeEnv = self.getArgumentValue(self.ARG_REMOVE_ENVELOPES)
        if removeEnv:
            envToken = 'Env'
        else:
            envToken = 'Key'

        scope = self.scope
        if scope == self.Scope.CHANNEL:
            type = 'Chan'
        elif scope == self.Scope.ITEM:
            type = 'Sel'
        else:
            type = 'Rig'

        return 'filter' + envToken + type

rs.cmd.bless(CmdAnimFilterKeys, "rs.anim.keyFilter")
