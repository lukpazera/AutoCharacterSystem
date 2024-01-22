

import lx
import modo
import rs


class CmdContextElementsVisibility(rs.Command):

    ARG_CONTEXT = 'context'
    ARG_SUBCONTEXT = 'subcontext'
    ARG_ELEMENT_SET = 'elementSet'
    ARG_STATE = 'state'
    
    def arguments(self):
        context = rs.cmd.Argument(self.ARG_CONTEXT, 'string')

        elementSet = rs.cmd.Argument(self.ARG_ELEMENT_SET, 'string')

        subcontext = rs.cmd.Argument(self.ARG_SUBCONTEXT, 'string')
        subcontext.flags = 'optional'
        subcontext.defaultValue = None

        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = ['query', 'optional']
        state.defaultValue = False

        return [context, elementSet, subcontext, state]

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def execute(self, msg, flags):
        elementSetIds = self._getElementSetIdentifiers()
        state = self.getArgumentValue(self.ARG_STATE)
        
        context = self._getContext()
        subcontext = self.getArgumentValue(self.ARG_SUBCONTEXT)
        for elementSetId in elementSetIds:
            context.setElementSetVisibility(elementSetId, state, subcontext=subcontext)
        rs.Scene().contexts.refreshCurrent()
        
    def query(self, argument):
        if argument == self.ARG_STATE:
            elementSetId = self._getFirstElementSetIdentifier()
            context = self._getContext()
            subcontext = self.getArgumentValue(self.ARG_SUBCONTEXT)
            return context.getElementSetVisibility(elementSetId, subcontext)
    
    # -------- Private methods
    
    def _getContext(self):
        contextIdentifier = self.getArgumentValue(self.ARG_CONTEXT)
        return rs.service.systemComponent.get(rs.c.SystemComponentType.CONTEXT, contextIdentifier)

    def _getElementSetIdentifiers(self):
        return self.getArgumentValue(self.ARG_ELEMENT_SET).split(';')
    
    def _getFirstElementSetIdentifier(self):
        return self._getElementSetIdentifiers()[0]
        
rs.cmd.bless(CmdContextElementsVisibility, 'rs.context.elementsVisibility')