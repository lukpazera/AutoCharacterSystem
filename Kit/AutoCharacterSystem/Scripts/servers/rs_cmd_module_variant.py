

import lx
import lxu
import modo
import modox

import rs


class CmdApplyModuleVariant(rs.base_OnModuleCommand):
    """ Fires custom module command.
    """

    ARG_MODULE_IDENT = 'modIdent'
    ARG_VARIANT_IDENT = 'varIdent'

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)

        moduleIdent = rs.cmd.Argument(self.ARG_MODULE_IDENT, 'string')
        moduleIdent.defaultValue = ''

        variantIdent = rs.cmd.Argument(self.ARG_VARIANT_IDENT, 'string')
        variantIdent.defaultValue = ''

        return [moduleIdent, variantIdent] + superArgs

    def basic_ButtonName(self):
        """ Button name should be username of the property.
        """
        moduleIdent = self.getArgumentValue(self.ARG_MODULE_IDENT)
        variantIdent = self.getArgumentValue(self.ARG_VARIANT_IDENT)
        if not moduleIdent or not variantIdent:
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.GENERIC, 'unknown')

        featuredModule = self._getFeaturedModuleClass()
        if featuredModule is None:
            lx.notimpl()
            return

        variantName = featuredModule.getVariantClass(variantIdent).descUsername
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, 'modVariant', [variantName])

    def applyEditActionPre(self):
        return True

    def applyEditActionPost(self):
        return True

    def setupMode(self):
        return True

    def restoreItemSelection(self):
        return True

    def execute(self, msg, flags):
        module = self.firstModuleToEdit
        if module is None:
            return

        featuredModuleClass = self._getFeaturedModuleClass()
        if not featuredModuleClass:
            return

        featuredModule = featuredModuleClass(module)

        variantIdent = self.getArgumentValue(self.ARG_VARIANT_IDENT)
        fmodOperator = rs.FeaturedModuleOperator(module.rigRootItem)
        fmodOperator.applyVariant(featuredModule, variantIdent)

    # -------- Private methods

    def _getFeaturedModuleClass(self):
        """ Gets module feature class or None if feature cannot be found.
        """
        moduleIdent = self.getArgumentValue(self.ARG_MODULE_IDENT)
        if not moduleIdent:
            return None
        try:
            return rs.service.systemComponent.get(rs.c.SystemComponentType.FEATURED_MODULE, moduleIdent)
        except LookupError:
            pass
        return None

rs.cmd.bless(CmdApplyModuleVariant, 'rs.module.applyVariant')


class CmdModuleVariantsFCL(rs.base_OnModuleCommand):
    """ Generates module variants command list.

    A variant can be applied by clicking a button on a list.
    Once a variant is applied the list disappears.
    """

    ARG_CMD_LIST = 'cmdList'

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)

        cmdList = rs.cmd.Argument(self.ARG_CMD_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFromCommandList
        cmdList.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST
        return [cmdList] + superArgs

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
        """ Builds form command list with buttons to apply module variants.
        """
        module = self.moduleToQuery
        if module is None:
            return []

        commandList = []

        # Grab featured module class that is tied to selected module (if any).
        try:
            featuredModule = rs.service.systemComponent.get(rs.c.SystemComponentType.FEATURED_MODULE, module.identifier)
        except LookupError:
            return []

        for variantClass in featuredModule.descVariants:
            cmd = "rs.module.applyVariant {%s} {%s}" % (module.identifier, variantClass.descIdentifier)
            commandList.append(cmd)

        return commandList

rs.cmd.bless(CmdModuleVariantsFCL, 'rs.module.variantsFCL')
