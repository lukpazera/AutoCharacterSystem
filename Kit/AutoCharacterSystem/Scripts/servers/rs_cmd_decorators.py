

import lx
import modo
import modox
import rs


class CmdSetDecoratorContext(rs.base_OnItemFeatureCommand):

    descIFClassOrIdentifier = rs.DecoratorIF
    
    ARG_IDENT = 'ident'
    ARG_STATE = 'state'

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
                
        argIdent = rs.cmd.Argument(self.ARG_IDENT, 'string')
        argIdent.defaultValue = None
        
        argState = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        argState.defaultValue = False
        argState.flags = 'query'
        
        return [argIdent, argState] + superArgs

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def basic_ButtonName(self):
        """ Display name of the context.
        """
        contextIdent = self.getArgumentValue(self.ARG_IDENT)

        try:
            context = rs.service.systemComponent.get(rs.c.SystemComponentType.CONTEXT, contextIdent)
        except LookupError:
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.GENERIC, 'unknown')
        
        return context.descUsername

    def execute(self, msg, flags):
        contextIdent = self.getArgumentValue(self.ARG_IDENT)
        state = self.getArgumentValue(self.ARG_STATE)
        
        for decoratorIF in self.itemFeaturesToEdit:
            if state:
                decoratorIF.addContext(contextIdent)
            else:
                decoratorIF.removeContext(contextIdent)

    def query(self, argIndex):
        if argIndex == self.ARG_STATE:
            decoratorIF = self.itemFeatureToQuery
            if decoratorIF is None:
                return False
            contextIdent = self.getArgumentValue(self.ARG_IDENT)
            if contextIdent in decoratorIF.contexts:
                return True
            return False

rs.cmd.bless(CmdSetDecoratorContext, 'rs.decorator.setContext')


class CmdDecoratorContextsFCL(rs.base_OnItemFeatureCommand):

    descIFClassOrIdentifier = rs.DecoratorIF
    
    ARG_CMD_LIST = 'cmdList'

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
            
        cmdList = rs.cmd.Argument(self.ARG_CMD_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFromCommandList
        cmdList.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST
        
        return [cmdList] + superArgs

    def execute(self, msg, flags):
        pass

    def query(self, argIndex):
        pass

    # -------- Private methods

    def _buildFromCommandList(self):
        """ Builds a list of contexts to toggle for decorator.
        """
        decoratorIF = self.itemFeatureToQuery
        
        if decoratorIF is None:
            return []

        commandList = []
        contexts = rs.service.systemComponent.getOfType(rs.c.SystemComponentType.CONTEXT)

        for context in contexts:
            commandList.append("rs.decorator.setContext ident:{%s} state:?" % (context.descIdentifier))

        return commandList

rs.cmd.bless(CmdDecoratorContextsFCL, 'rs.decorator.contextsFCL')