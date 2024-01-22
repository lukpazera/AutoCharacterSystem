

import lx
import lxu
import modo
import modox

import rs


CONTEXT = rs.base_Context.sysType()


class CmdSceneContext(rs.Command):
    """ Sets scene context.
    
    When button is pressed a context from ident argument is used.
    When button is de-pressed, a context from offIdent argument is used.
    When offIdent is not set it is not possible to de-press command's button
    once preset and the context from ident argument is on.
    """

    ARG_IDENT = 'ident'
    ARG_STATE = 'state'
    ARG_OFF_IDENT = 'offIdent'

    def arguments(self):
        ident = rs.cmd.Argument(self.ARG_IDENT, 'string')
        ident.defaultValue = None
        
        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = ['query', 'optional']
        state.defaultValue = False

        offIdent = rs.cmd.Argument(self.ARG_OFF_IDENT, 'string')
        offIdent.flags = 'optional'
        offIdent.defaultValue = None
        
        return [ident, state, offIdent]

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def applyEditActionPre(self):
        return True

    def dropToolPre(self):
        return True

    def enable(self, msg):
        """ Enables or disables the context button.
        
        The state is based on enable property of the context object.
        However, if this attribute is not implemented then the default
        rs.Command behaviour will be used (which makes context enabled
        if there's at least one rig in the scene).
        """
        if not rs.Command.enable(self, msg):
            return False

        contextIdentifier = self.getArgumentValue(self.ARG_IDENT)
        try:
            contextObj = rs.service.systemComponent.get(CONTEXT, contextIdentifier)
        except LookupError:
            return False
        
        try:
            contextEnable = contextObj.enable
        except AttributeError:
            contextEnable = True # Context is enabled by default if not set otherwise.

        if not contextEnable:
            msgKey = contextObj.descDisableMessageKey
            if msgKey is not None:
                msg.set(rs.c.MessageTable.DISABLE, msgKey)

        return contextEnable

    def execute(self, msg, flags):
        state = self.getArgumentValue(self.ARG_STATE)
        contextToSet = None
        if state:
            contextToSet = self.getArgumentValue(self.ARG_IDENT)
        else:
            contextToSet = self.getArgumentValue(self.ARG_OFF_IDENT)

        if contextToSet:
            rs.Scene().context = contextToSet
            modox.ItemSelection().clear()
            rs.service.notify(rs.c.Notifier.UI_GENERAL, rs.c.Notify.DATATYPE)
                
    def query(self, argument):
        """ Queries current context.
        """
        if argument == self.ARG_STATE:
            currentContextIdent = rs.Scene.getCurrentContextIdentifierFast()
            argContextIdent = self.getArgumentValue(self.ARG_IDENT)
            if argContextIdent == currentContextIdent:
                return True
            return False

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append((rs.c.Notifier.ACCESS_LEVEL, '+d'))
        return notifiers
    
rs.cmd.bless(CmdSceneContext, "rs.context")


class CmdSceneContextFormFilter(rs.Command):
    """ Filters out forms that should not be visible without proper scene context.
    
    Use this command as form filter for forms that need to be visible
    only in specific scene context.
    Pass context identifier as command's argument.
    If required context is not set the filter's enable method returns False.
    """

    ARG_IDENT = "ident"

    def arguments(self):
        ident = rs.cmd.Argument(self.ARG_IDENT, "string")
        ident.defaultValue = ""
        return [ident]

    def enable(self, msg):
        """ Filters form out if its context is not set.
        """
        ident = self.getArgumentValue(self.ARG_IDENT)
        if not ident:
            return False
        
        return ident == rs.Scene.getCurrentContextIdentifierFast()

rs.cmd.bless(CmdSceneContextFormFilter, 'rs.context.filter')