

import lx
import lxu
import modo
import modox

import rs


class CmdModuleProperty(rs.base_OnModuleCommand):
    """ Sets or queries custom module property.
    """

    ARG_MODULE_IDENT = 'modIdent'
    ARG_PROPERTY_IDENT = 'propIdent'
    ARG_VALUE = 'state'

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)

        moduleIdent = rs.cmd.Argument(self.ARG_MODULE_IDENT, 'string')
        moduleIdent.flags = ['reqforvariable']
        moduleIdent.defaultValue = ''
        
        propIdent = rs.cmd.Argument(self.ARG_PROPERTY_IDENT, 'string')
        propIdent.flags = ['reqforvariable']
        propIdent.defaultValue = ''

        value = rs.cmd.Argument(self.ARG_VALUE, 'integer')
        value.flags = ['query', 'variable']
        value.defaultValue = True

        return [moduleIdent, propIdent, value] + superArgs

    def uiHints(self, argument, hints):
        if argument == self.ARG_VALUE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def basic_ButtonName(self):
        """ Button name should be username of the property.
        """
        moduleIdent = self.getArgumentValue(self.ARG_MODULE_IDENT)
        propertyIdent = self.getArgumentValue(self.ARG_PROPERTY_IDENT)
        if not moduleIdent or not propertyIdent:
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.GENERIC, 'unknown')

        featuredModuleClass  = self._getFeaturedModuleClass()
        if featuredModuleClass is None:
            lx.notimpl()
            return

        username = featuredModuleClass.getPropertyClass(propertyIdent).descUsername
        try:
            username = modox.Message.getMessageTextFromTable(rs.c.MessageTable.MODLABEL, username)
        except LookupError:
            pass
        return username

    def basic_ArgType(self, index):
        if index == self.getArgument(self.ARG_VALUE):
            featuredModuleClass = self._getFeaturedModuleClass()
            if featuredModuleClass is not None:
                propertyIdent = self.getArgumentValue(self.ARG_PROPERTY_IDENT)
                datatype = featuredModuleClass.getPropertyClass(propertyIdent).descValueType
                return datatype
        return lx.symbol.sTYPE_BOOLEAN

    def cmd_Tooltip(self):
        featuredModuleClass = self._getFeaturedModuleClass()
        propertyIdent = self.getArgumentValue(self.ARG_PROPERTY_IDENT)
        propertyClass = featuredModuleClass.getPropertyClass(propertyIdent)
        tooltipKey = propertyClass.descTooltipMsgTableKey
        if tooltipKey is not None:
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.MODTOOLTIP, tooltipKey)

        return self.basic_ButtonName()

    def restoreItemSelection(self):
        return True

    def applyEditActionPre(self):
        return True
    
    def applyEditActionPost(self):
        return True

    def setupMode(self):
        featuredModuleClass = self._getFeaturedModuleClass()
        propertyIdent = self.getArgumentValue(self.ARG_PROPERTY_IDENT)
        propertyClass = featuredModuleClass.getPropertyClass(propertyIdent)
        return propertyClass.descSetupMode

    def execute(self, msg, flags):
        featuredModuleClass = self._getFeaturedModuleClass()
        if not featuredModuleClass:
            return

        rawModulesToUpdate = []
        propertyIdent = self.getArgumentValue(self.ARG_PROPERTY_IDENT)
        propClass = featuredModuleClass.getPropertyClass(propertyIdent)

        for module in self._getModulesToEdit(propClass.descSupportSymmetry):
            featuredModule = featuredModuleClass(module)

            value = self.getArgumentValue(self.ARG_VALUE)
            try:
                result = featuredModule.onSet(propertyIdent, value)
            except AttributeError:
                result = False
            if result:
                rawModulesToUpdate.append(featuredModule.module)
                rawModulesToUpdate.extend(featuredModule.module.submodules)

        if rawModulesToUpdate:
            propClass = featuredModule.getPropertyClass(propertyIdent)
            if propClass.descApplyGuide:
                guide = rs.Guide(rawModulesToUpdate[0].rigRootItem)
                guide.apply(rawModulesToUpdate)
            if propClass:
                rs.Scene().contexts.refreshCurrent()

    def query(self, argument):
        if argument == self.getArgument(self.ARG_VALUE):

            module = self.moduleToQuery
            if module is None:
                return

            featuredModuleClass = self._getFeaturedModuleClass()
            if featuredModuleClass is None:
                return
            featuredModule = featuredModuleClass(module)

            propertyIdent = self.getArgumentValue(self.ARG_PROPERTY_IDENT)
            try:
                return featuredModule.onQuery(propertyIdent)
            except AttributeError:
                pass

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

    def _getModulesToEdit(self, supportSymmetry=True):
        extraMods = []
        modulesToEdit = self.modulesToEdit
        for module in modulesToEdit:

            # Add symmetry linked modules
            # This adds modules from both link directions (reference and driven)
            if not supportSymmetry:
                continue

            symmetryLinkedModules = module.symmetryLinkedModules
            for symmod in symmetryLinkedModules:
                if symmod not in modulesToEdit and symmod not in extraMods:
                    extraMods.append(symmod)

        return modulesToEdit + extraMods

rs.cmd.bless(CmdModuleProperty, 'rs.module.property')


class CmdModuleCommand(rs.base_OnModuleCommand):
    """ Fires custom module command.
    """

    ARG_MODULE_IDENT = 'modIdent'
    ARG_COMMAND_IDENT = 'cmdIdent'
    ARG_COMMAND_ARGUMENTS = 'cmdArgs'

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)

        moduleIdent = rs.cmd.Argument(self.ARG_MODULE_IDENT, 'string')
        moduleIdent.defaultValue = ''
        
        cmdIdent = rs.cmd.Argument(self.ARG_COMMAND_IDENT, 'string')
        cmdIdent.defaultValue = ''

        args = rs.cmd.Argument(self.ARG_COMMAND_ARGUMENTS, 'string')
        args.defaultValue = ''

        return [moduleIdent, cmdIdent, args] + superArgs

    def basic_ButtonName(self):
        """ Button name should be username of the property.
        """
        moduleIdent = self.getArgumentValue(self.ARG_MODULE_IDENT)
        commandIdent = self.getArgumentValue(self.ARG_COMMAND_IDENT)
        if not moduleIdent or not commandIdent:
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.GENERIC, 'unknown')

        featuredModule = self._getFeaturedModuleClass()
        if featuredModule is None:
            lx.notimpl()
            return

        username = featuredModule.getCommandClass(commandIdent).descUsername
        try:
            username = modox.Message.getMessageTextFromTable(rs.c.MessageTable.MODLABEL, username)
        except LookupError:
            pass
        return username

    def cmd_Tooltip(self):
        featuredModuleClass = self._getFeaturedModuleClass()
        cmdIdent = self.getArgumentValue(self.ARG_COMMAND_IDENT)
        cmdClass = featuredModuleClass.getCommandClass(cmdIdent)
        tooltipKey = cmdClass.descTooltipMsgTableKey
        if tooltipKey is not None:
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.MODTOOLTIP, tooltipKey)
        return self.basic_ButtonName()

    def setupMode(self):
        featuredModuleClass = self._getFeaturedModuleClass()
        cmdIdent = self.getArgumentValue(self.ARG_COMMAND_IDENT)
        cmdClass = featuredModuleClass.getCommandClass(cmdIdent)
        return cmdClass.descSetupMode

    def execute(self, msg, flags):
        featuredModuleClass = self._getFeaturedModuleClass()
        if not featuredModuleClass:
            return

        commandIdent = self.getArgumentValue(self.ARG_COMMAND_IDENT)
        cmdClass = featuredModuleClass.getCommandClass(commandIdent)

        args = self.getArgumentValue(self.ARG_COMMAND_ARGUMENTS)
        if args:
            args = args.split(';')
        else:
            args = []

        rawModulesToUpdate = []

        for module in self._getModulesToEdit(cmdClass.descSupportSymmetry):
            featuredModule = featuredModuleClass(module)

            try:
                result = featuredModule.onRun(commandIdent, args)
            except AttributeError:
                result = False
            if result:
                rawModulesToUpdate.append(featuredModule.module)
                rawModulesToUpdate.extend(featuredModule.module.submodules)

        if rawModulesToUpdate:
            commandClass = featuredModule.getCommandClass(commandIdent)
            if commandClass.descApplyGuide:
                guide = rs.Guide(rawModulesToUpdate[0].rigRootItem)
                guide.apply(rawModulesToUpdate)
            if commandClass.descRefreshContext:
                rs.Scene().contexts.refreshCurrent()

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

    def _getModulesToEdit(self, supportSymmetry=True):
        extraMods = []
        modulesToEdit = self.modulesToEdit
        for module in modulesToEdit:

            # Add symmetry linked modules
            # This adds modules from both link directions (reference and driven)
            if not supportSymmetry:
                continue

            symmetryLinkedModules = module.symmetryLinkedModules
            for symmod in symmetryLinkedModules:
                if symmod not in modulesToEdit and symmod not in extraMods:
                    extraMods.append(symmod)

        return modulesToEdit + extraMods

rs.cmd.bless(CmdModuleCommand, 'rs.module.command')


class CmdModuleFeatureFCL(rs.Command):
    """ Generates module features command list.
    
    This command list shows all the properties and commands that
    accompany module asset.
    """

    ARG_CMD_LIST = 'cmdList'
    ARG_SCOPE = 'scope'

    SCOPE_HINTS = ((0, 'local'),
                   (1, 'global'))

    def arguments(self):
        cmdList = rs.cmd.Argument(self.ARG_CMD_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFromCommandList
        cmdList.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST

        scope = rs.cmd.Argument(self.ARG_SCOPE, 'integer')
        scope.flags = 'optional'
        scope.hints = self.SCOPE_HINTS
        scope.defaultValue = 0

        return [cmdList, scope]

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
        """ Builds form command list with module custom properties and input channels.
        """
        if self.getArgumentValue(self.ARG_SCOPE) == 1:  # Global scope here
            return self._buildGlobalCommandList()
        return self._buildLocalCommandList()

    def _buildGlobalCommandList(self):
        rigRoot = self._getRigRootItem()
        if rigRoot is None:
            return []

        commandList = []

        modules = rs.ModuleOperator(rigRoot).allModules
        for module in modules:
            preModuleCount = len(commandList)
            self._addModulePropertiesAndCommands(module, commandList, scope=rs.base_ModuleCommand.Scope.GLOBAL)
            # Add divider if a module that we went through had some features that
            # were added to command list.
            if len(commandList) > preModuleCount:
                commandList.append(modox.c.FormCommandList.DIVIDER)

        # Remove last item on the list if it's divider
        if commandList[-1] == modox.c.FormCommandList.DIVIDER:
            commandList.pop(-1)

        return commandList

    def _buildLocalCommandList(self):
        module = self._getModule()
        if module is None:
            return []
        
        commandList = []

        self._addModulePropertiesAndCommands(module, commandList, scope=rs.base_ModuleCommand.Scope.LOCAL)

        # Add divider before exposed assembly channels if any features were added.
        dividerAdded = self._addDividerBetweenFeaturesAndInputs(commandList)

        cmdCount = len(commandList)

        self._addAssemblyInputs(module, commandList)

        # Remove divider from form command list if there were no assembly channels to expose.
        if dividerAdded and len(commandList) == cmdCount:
            del commandList[-1]

        return commandList

    # -------- Private methods

    def _getRigRootItem(self):
        return rs.Scene.getFirstRigRootItemSelectionFast()

    def _getModule(self):
        for item in modo.Scene().selected:
            try:
                rigModule = rs.Module(item)
            except TypeError:
                continue
            return rigModule
        return None

    def _addModulePropertiesAndCommands(self, module, commandList, scope=rs.base_ModuleCommand.Scope.LOCAL):
        devContext = False
        if rs.ContextOperator.getContextIdentFast() == rs.c.Context.ASSEMBLY:
            if rs.Scene().contexts.current.subcontext == rs.c.AssemblySubcontexts.DEVELOP:
                devContext = True

        # Grab featured module class that is tied to selected module (if any).
        try:
            featuredModule = rs.service.systemComponent.get(rs.c.SystemComponentType.FEATURED_MODULE, module.identifier)
        except LookupError:
            featuredModule = None

        # Add custom properties and commands if module is registered as featured one.
        if featuredModule is not None:
            featuredModuleObject = featuredModule(module)
            for modProperty in featuredModuleObject.featuresList:
                # Test for string first, other tests will fail with string.
                # String means that the property is a special markup for command list such as divider.
                if isinstance(modProperty, str):
                    cmd = modProperty

                elif issubclass(modProperty, rs.base_ModuleProperty):
                    # Scope checking is needed for global scope only since all properties are always
                    # visible in local scope. Global scope makes properties visible in rig properties too.
                    if scope == rs.base_ModuleProperty.Scope.GLOBAL and modProperty.descScope != scope:
                        continue
                    if modProperty.descDeveloperAccess and not devContext:
                        continue
                    cmd = "rs.module.property {%s} {%s} ?" % (module.identifier, modProperty.descIdentifier)
                    # In global mode we have to be specific which module we display buttons for.
                    if scope == rs.base_ModuleProperty.Scope.GLOBAL:
                        cmd += " rootItem:{%s}" % module.rootModoItem.id

                elif issubclass(modProperty, rs.base_ModuleCommand):
                    # Same scope checking as above.
                    if scope == rs.base_ModuleProperty.Scope.GLOBAL and modProperty.descScope != scope:
                        continue
                    if modProperty.descDeveloperAccess and not devContext:
                        continue
                    cmd = "rs.module.command {%s} {%s} {%s}" % (module.identifier, modProperty.descIdentifier, '')
                    # In global mode we have to be specific which module we display buttons for.
                    if scope == rs.base_ModuleProperty.Scope.GLOBAL:
                        cmd += " rootItem:{%s}" % module.rootModoItem.id

                commandList.append(cmd)

    def _addDividerBetweenFeaturesAndInputs(self, commandList):
        if len(commandList) > 0:
            commandList.append(modox.c.FormCommandList.DIVIDER)
            return True
        return False

    def _addAssemblyInputs(self, module, commandList):
        moduleAssmItem = module.assemblyModoItem
        moduleAssmIdent = moduleAssmItem.id
        userChans = modox.Item(moduleAssmItem.internalItem).getUserChannels(sort=True)
        for chan in userChans:
            if chan.revCount > 0:
                continue # do not show driven channels
            cmd = "item.channel {%s} ? item:{%s}" % (chan.name, moduleAssmIdent)
            commandList.append(cmd)

rs.cmd.bless(CmdModuleFeatureFCL, 'rs.module.featureFCL')
