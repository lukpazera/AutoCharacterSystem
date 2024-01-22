
import lx
import lxu
import modo
import modox

import rs


class CmdRigCommand(rs.Command):
    """ Fires custom rig command.
    """

    ARG_RIG_IDENT = 'rigIdent'
    ARG_COMMAND_IDENT = 'cmdIdent'
    ARG_COMMAND_ARGUMENTS = 'cmdArgs'

    def arguments(self):
        rigIdent = rs.cmd.Argument(self.ARG_RIG_IDENT, 'string')
        rigIdent.defaultValue = ''

        cmdIdent = rs.cmd.Argument(self.ARG_COMMAND_IDENT, 'string')
        cmdIdent.defaultValue = ''

        args = rs.cmd.Argument(self.ARG_COMMAND_ARGUMENTS, 'string')
        args.defaultValue = ''

        return [rigIdent, cmdIdent, args]

    def setupMode(self):
        return True

    def basic_ButtonName(self):
        """ Button name should be username of the property.
        """
        rigIdent = self.getArgumentValue(self.ARG_RIG_IDENT)
        commandIdent = self.getArgumentValue(self.ARG_COMMAND_IDENT)
        if not rigIdent or not commandIdent:
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.GENERIC, 'unknown')

        featuredModule = self._getFeaturedRigClass()
        if featuredModule is None:
            lx.notimpl()
            return

        return featuredModule.getCommandClass(commandIdent).descUsername

    def execute(self, msg, flags):
        rig = self._getRig()
        if rig is None:
            return

        featuredRigClass = self._getFeaturedRigClass()
        if not featuredRigClass:
            return

        featuredRig = featuredRigClass(rig)

        commandIdent = self.getArgumentValue(self.ARG_COMMAND_IDENT)
        args = self.getArgumentValue(self.ARG_COMMAND_ARGUMENTS)
        args = args.split(';')
        try:
            featuredRig.onRun(commandIdent, args)
        except AttributeError:
            pass

    # -------- Private methods

    def _getFeaturedRigClass(self):
        rigIdent = self.getArgumentValue(self.ARG_RIG_IDENT)
        if not rigIdent:
            return None
        try:
            return rs.service.systemComponent.get(rs.c.SystemComponentType.FEATURED_RIG, rigIdent)
        except LookupError:
            pass
        return None

    def _getRig(self):
        ident = self.getArgumentValue(self.ARG_RIG_IDENT)
        for item in modo.Scene().selected:
            try:
                rig = rs.Rig(item)
            except TypeError:
                continue
            if rig.identifier == ident:
                return rig
        return None

rs.cmd.bless(CmdRigCommand, 'rs.rig.command')


class CmdRigFeatureFCL(rs.Command):
    """ Generates module features command list.

    This command list shows all the properties and commands that
    accompany rig asset.
    """

    ARG_CMD_LIST = 'cmdList'

    def arguments(self):
        cmdList = rs.cmd.Argument(self.ARG_CMD_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFromCommandList
        cmdList.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST
        return [cmdList]

    def execute(self, msg, flags):
        pass

    def query(self, argIndex):
        pass

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+t'))
        return notifiers

    # -------- Private methods

    def _buildFromCommandList(self):
        """ Builds form command list with rig custom properties.
        """
        rig = self._getRig()
        if rig is None:
            return []

        commandList = []

        # Grab featured rig class that is tied to selected rig (if any).
        try:
            featuredRig = rs.service.systemComponent.get(rs.c.SystemComponentType.FEATURED_RIG, rig.identifier)
        except LookupError:
            featuredRig = None

        # Add custom properties and commands if rig is registered as featured one.
        if featuredRig is not None:
            for rigProperty in featuredRig.descFeatures:
                # Test for string first, other tests will fail with string.
                # String means that the property is a special markup for command list such as divider.
                if isinstance(rigProperty, str):
                    cmd = rigProperty
                elif issubclass(rigProperty, rs.base_RigCommand):
                    cmd = "rs.rig.command {%s} {%s} {%s}" % (rig.identifier, rigProperty.descIdentifier, '')

                commandList.append(cmd)

        if len(commandList) > 0:
            commandList.append(modox.c.FormCommandList.DIVIDER)

        return commandList

    # -------- Private methods

    def _getRig(self):
        for item in modo.Scene().selected:
            try:
                rig = rs.Rig(item)
            except TypeError:
                continue
            return rig
        return None

rs.cmd.bless(CmdRigFeatureFCL, 'rs.rig.featureFCL')
