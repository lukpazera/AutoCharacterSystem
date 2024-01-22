

import lx
import lxu
import modo
import modox

import rs


class CmdItemFeature(rs.base_OnItemFeatureCommand):
    """ Adds or removes item feature to/from an item.
    """

    ARG_IDENT = 'ident'
    ARG_STATE = 'state'

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
        
        ident = rs.cmd.Argument(self.ARG_IDENT, 'string')
        ident.defaultValue = ''

        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = 'query'
        state.defaultValue = False

        return [ident, state] + superArgs

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def restoreItemSelection(self):
        # Restore item selection only when removing a feature.
        return not self.getArgumentValue(self.ARG_STATE)

    def basic_ButtonName(self):
        """ Button name should be username of the feature.
        If command is querying an argument then the argument's label
        will override button name apparently.
        """
        featureIdent = self.getArgumentValue(self.ARG_IDENT)
        if not featureIdent:
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.GENERIC, 'none')

        try:
            featureClass = rs.service.systemComponent.get(rs.c.SystemComponentType.ITEM_FEATURE, featureIdent)
        except LookupError:
            return modox.Message.getMessageTextFromTable(rs.c.MessageTable.GENERIC, 'none')
        
        return featureClass.descUsername
        
    def execute(self, msg, flags):
        ident = self.getArgumentValue(self.ARG_IDENT)
        if not ident:
            return
        state = self.getArgumentValue(self.ARG_STATE)

        change = False
        
        rawItems = modox.ItemSelection().getRaw()
        for rawItem in rawItems:
            try:
                itemFeatures = rs.ItemFeatures(rawItem)
            except TypeError:
                continue
            
            if state:
                itemFeatures.addFeature(ident)
            else:
                itemFeatures.removeFeature(ident)
            
            change = True
        
        if change:
            # This helps with keeping rig properties tab visible.
            # MODO will switch away from the tab otherwise.
            modox.ItemUtils.autoFocusItemListOnSelection()
            
            rs.service.notify(rs.c.Notifier.ITEM_FEATURES_ADDREM, lx.symbol.fCMDNOTIFY_DISABLE)

            
    def query(self, argument):
        ident = self.getArgumentValue(self.ARG_IDENT)
        if not ident:
            return False

        if argument == self.ARG_STATE:
            featureOp = self.itemFeatureOperatorToQuery
            if featureOp is None:
                return False
            return featureOp.hasFeature(ident)
        return False

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers

rs.cmd.bless(CmdItemFeature, 'rs.item.feature')
