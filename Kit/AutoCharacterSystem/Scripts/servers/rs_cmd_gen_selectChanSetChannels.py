
import lx
import lxu
import modo
import modox

import rs


class CmdSelectChannelSetSourceItem(modox.Command):

    def enable(self, msg):
        try:
            chanSetItemId = lx.eval('group.current ? type:chanset')
        except RuntimeError:
            msg.set(rs.c.MessageTable.DISABLE, "chanSetSource")
            return False
        if not chanSetItemId:
            msg.set(rs.c.MessageTable.DISABLE, "chanSetSource")
            return False

        try:
            item = modo.Group(modox.SceneUtils.findItemFast(chanSetItemId))
        except LookupError:
            msg.set(rs.c.MessageTable.DISABLE, "chanSetSource")
            return False

        try:
            rs.ChannelSet(item)
        except TypeError:
            msg.set(rs.c.MessageTable.DISABLE, "chanSetSource")
            return False

        return True

    def execute(self, msg, flags):
        try:
            chanSetItemId = lx.eval('group.current ? type:chanset')
        except RuntimeError:
            return
        if not chanSetItemId:
            return
        chanSetItem = modox.SceneUtils.findItemFast(chanSetItemId)

        try:
            chanSet = rs.controller_ui.ChannelSet(modo.Group(chanSetItem))
        except TypeError:
            rs.log.out("Not a valid channel set item!", rs.log.MSG_ERROR)
            return

        panelItem = chanSet.channelsSourceModoItem
        modox.ItemSelection().set(panelItem, modox.SelectionMode.REPLACE)

    def notifiers(self):
        notifiers = []
        notifiers.append(modox.c.Notifier.GRAPH_CURRENT_GROUPS_DISABLE)
        return notifiers

rs.cmd.bless(CmdSelectChannelSetSourceItem, 'rs.chanSet.selectSourceItem')