
import lx
import modo

import rs


class CmdActorContent(rs.base_OnItemFeatureCommand):
    """ Sets or queries actor content type: items or channels.
    """

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.Controller
    
    ARG_CONTENT = "content"
    ARG_STATE = "state"
    
    CONTENT_HINT = (
        (0, "item"),
        (1, "chans")
    )

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
                
        content = rs.cmd.Argument(self.ARG_CONTENT, "integer")
        content.hints = self.CONTENT_HINT

        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = 'query'
        state.defaultValue = False
        
        return [content, state] + superArgs
    
    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def execute(self, msg, flags):
        content = self.getArgumentValue(self.ARG_CONTENT)
        state = self.getArgumentValue(self.ARG_STATE)

        for ctrl in self.itemFeaturesToEdit:
            if content == 0:
                ctrl.addItemToActor = state
            elif content == 1:
                ctrl.addChannelsToActor = state
    
    def query(self, argument):
        if argument == self.ARG_STATE:
            ctrl = self.itemFeatureToQuery
            if ctrl is not None:
                # Getting argument with hint gets the underlying integer.
                content = self.getArgumentValue(self.ARG_CONTENT)
                if content == 0:
                    return ctrl.addItemToActor
                elif content == 1:
                    return ctrl.addChannelsToActor
                else:
                    return None

rs.cmd.bless(CmdActorContent, 'rs.controller.actorContent')

