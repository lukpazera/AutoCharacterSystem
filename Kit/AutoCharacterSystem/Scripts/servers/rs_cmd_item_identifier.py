

import lx
import lxu
import modo

import rs


class CmdItemIdentifier(rs.base_OnItemFeatureCommand):

    ARG_IDENTIFIER = 'identifier'

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.IdentifierFeature
    
    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
        
        argIdent = rs.cmd.Argument(self.ARG_IDENTIFIER, 'string')
        argIdent.flags = 'query'
        
        return [argIdent] + superArgs
        
    def execute(self, msg, flags):
        ident = self.getArgumentValue(self.ARG_IDENTIFIER)

        for feature in self.itemFeaturesToEdit:
            feature.identifier = ident

    def query(self, argument):
        if argument == self.ARG_IDENTIFIER:
            identifierFeature = self.itemFeatureToQuery
            if identifierFeature is None:
                return None

            return identifierFeature.identifier
        return None

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers

rs.cmd.bless(CmdItemIdentifier, 'rs.item.identifier')