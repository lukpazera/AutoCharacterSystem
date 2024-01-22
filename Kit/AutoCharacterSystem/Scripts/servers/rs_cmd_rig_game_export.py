

import os

import lx
import lxu
import modo
import modox

import rs


class CmdRigGameExportSet(rs.RigCommand):

    ARG_IDENT = 'identifier'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        ident = rs.cmd.Argument(self.ARG_IDENT, 'integer')
        ident.flags = 'query'
        ident.valuesList = self._buildPopup
        ident.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        return [ident] + superArgs

    def applyEditActionPre(self):
        return True

    def execute(self, msg, flags):
        editRig = self.firstRigToEdit
        identIndex = self.getArgumentValue(self.ARG_IDENT)

        sets = self._getSortedExportSets()

        try:
            ident = sets[identIndex].descIdentifier
        except IndexError:
            return

        rs.base_GameExportSet.setGameExportSetOnRig(editRig, ident)

    def query(self, argument):
        if argument == self.ARG_IDENT:
            rigToQuery = self.rigToQuery
            if rigToQuery is None:
                return 0

            rigIdent = rs.base_GameExportSet.getGameExportSetFromRig(rigToQuery)
            if not rigIdent:
                return 0

            sets = self._getSortedExportSets()
            idents = [exset.descIdentifier for exset in sets]
            try:
                return idents.index(rigIdent)
            except ValueError:
                return 0
        return 0

    # -------- Private methods

    def _buildPopup(self):
        setsList = self._getSortedExportSets()
        entries = []
        for exportSet in setsList:
            entries.append((exportSet.descIdentifier, exportSet.descUsername))
        return entries

    def _getSortedExportSets(self):
        return rs.service.systemComponent.getOfTypeSortedByIdentifier(rs.c.SystemComponentType.GAME_EXPORT_SET)

rs.cmd.bless(CmdRigGameExportSet, "rs.rig.gameExportSet")


class CmdRigGameExportCommand(rs.RigCommand):

    ARG_CMD_IDENT = 'cmdIdent'

    BUTTON_LABELS = {
        rs.game_export.GameExportCommandId.ALL_SINGLE_FILE: 'gmexAllSingle',
        rs.game_export.GameExportCommandId.ALL_MULTIPLE_FILES: 'gmexAllMulti',
        rs.game_export.GameExportCommandId.SKELETAL_MESH: 'gmexSkelMesh',
        rs.game_export.GameExportCommandId.CURRENT_ACTION: 'gmexCurAction',
        rs.game_export.GameExportCommandId.ALL_ACTIONS: 'gmexAllActions',
    }

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        cmdIdentArg = rs.cmd.Argument(self.ARG_CMD_IDENT, 'string')

        return [cmdIdentArg] + superArgs

    def basic_ButtonName(self):
        ident = self.getArgumentValue(self.ARG_CMD_IDENT)
        try:
            msgKey = self.BUTTON_LABELS[ident]
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, msgKey)
        except KeyError:
            pass
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.GENERIC, rs.c.MessageKey.UNKNOWN)

    def applyEditActionPre(self):
        return True

    def flags(self):
        return lx.symbol.fCMD_UNDO | lx.symbol.fCMD_UNDO_AFTER_EXEC

    def enable(self, msg):
        """
        Make sure export path exists before attempting to export.

        Note that this is not fast, takes 1 milisecond on m.2 SSD
        but there are only a few buttons and even with excessive calls to enable()
        method (about 10 times) that should not affect UI performance overall.
        """
        if not rs.RigCommand.enable(self, msg):
            return False

        rig = self.firstRigToEdit
        result = rs.game_export.GameExportOperator.testExportPath(rig)
        if not result:
            msg.set(rs.c.MessageTable.DISABLE, 'gameexInvalidPath')
        return result

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        gameExId = rs.base_GameExportSet.getGameExportSetFromRig(rig)

        try:
            gameExportSet = rs.service.systemComponent.get(rs.c.SystemComponentType.GAME_EXPORT_SET, gameExId)
        except LookupError:
            return

        cmdId = self.getArgumentValue(self.ARG_CMD_IDENT)
        try:
            cmdClass = gameExportSet.descExportCommands[cmdId]
        except KeyError:
            rs.log.out("Unknown game export command!", rs.log.MSG_ERROR)
            return

        ticksCount = 1000.0
        monitor = modox.Monitor(ticksCount=ticksCount, title="Game Export")

        gameExportOp = rs.game_export.GameExportOperator(rig)
        gameExportOp.do(cmdClass, monitor, ticksCount)

        monitor.release()

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append((rs.c.Notifier.GAME_EXPORT, '+d'))
        return notifiers

rs.cmd.bless(CmdRigGameExportCommand, "rs.rig.gameExportCmd")


class CmdRigGameExportSetPath(rs.RigCommand):

    def interact(self):
        rig = self.rigToQuery
        if rig is None:
            return False

        currentPath = rig.rootItem.getChannelProperty(rig.rootItem.PropertyChannels.CHAN_GAME_EXPORT_FOLDER)
        self._path = modo.dialogs.dirBrowse(title='Set Rig Game Export Path',
                                            path=currentPath)
        if self._path is None:
            return False

        return True

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        rig.rootItem.setChannelProperty(rig.rootItem.PropertyChannels.CHAN_GAME_EXPORT_FOLDER, self._path)

        rs.service.notify(rs.c.Notifier.GAME_EXPORT, lx.symbol.fCMDNOTIFY_VALUE | lx.symbol.fCMDNOTIFY_DISABLE)

rs.cmd.bless(CmdRigGameExportSetPath, "rs.rig.gameExportSetPath")


class CmdRigGameExportEditPath(rs.RigCommand):

    ARG_PATH = 'path'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argPath = rs.cmd.Argument(self.ARG_PATH, 'string')
        argPath.flags = 'query'

        return [argPath] + superArgs

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        path = self.getArgumentValue(self.ARG_PATH)
        rig.rootItem.setChannelProperty(rig.rootItem.PropertyChannels.CHAN_GAME_EXPORT_FOLDER, path)

        rs.service.notify(rs.c.Notifier.GAME_EXPORT, lx.symbol.fCMDNOTIFY_VALUE | lx.symbol.fCMDNOTIFY_DISABLE)

    def query(self, argument):
        if argument == self.ARG_PATH:
            rig = self.rigToQuery
            if rig is None:
                path = ''
            else:
                rootItem = rig.rootItem
                path = rootItem.getChannelProperty(rootItem.PropertyChannels.CHAN_GAME_EXPORT_FOLDER)
            return path
        return ''

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append((rs.c.Notifier.GAME_EXPORT, '+vd'))
        return notifiers

rs.cmd.bless(CmdRigGameExportEditPath, "rs.rig.gameExportEditPath")


class CmdRigGameExportSupportStretching(rs.RigCommand):

    ARG_STRETCH = 'stretch'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argStretch = rs.cmd.Argument(self.ARG_STRETCH, 'boolean')
        argStretch.defaultValue = False
        argStretch.flags = 'query'

        return [argStretch] + superArgs

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        stretch = self.getArgumentValue(self.ARG_STRETCH)
        rig.rootItem.settings.set(rs.RootItem.SETTING_STRETCH, stretch)

        rs.service.notify(rs.c.Notifier.GAME_EXPORT, lx.symbol.fCMDNOTIFY_VALUE | lx.symbol.fCMDNOTIFY_DISABLE)

    def query(self, argument):
        if argument == self.ARG_STRETCH:
            rig = self.rigToQuery
            if rig is None:
                stretch = False
            else:
                rootItem = rig.rootItem
                stretch = rootItem.settings.get(rootItem.SETTING_STRETCH, False)
            return stretch
        return False

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append((rs.c.Notifier.GAME_EXPORT, '+vd'))
        return notifiers

rs.cmd.bless(CmdRigGameExportSupportStretching, "rs.rig.gameExportStretch")
