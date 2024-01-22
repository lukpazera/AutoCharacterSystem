

import lx
import modo
import modox

import rs


class CmdItemFeaturesFCL(rs.Command):
    """ Generates command list with item features.
    
    This command is used to add/remove features to rig items.
    """

    ARG_CMD_LIST = 'cmdList'
    ARG_CATEGORY = 'category'

    def arguments(self):
        cmdList = rs.cmd.Argument(self.ARG_CMD_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFromCommandList
        cmdList.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST
        
        category = rs.cmd.Argument(self.ARG_CATEGORY, 'string')
        category.flags = 'optional'
        category.defaultValue = rs.c.ItemFeatureCategory.GENERAL
        
        return [cmdList, category]

    def execute(self, msg, flags):
        pass

    def query(self, argIndex):
        pass

    # -------- Private methods

    def _buildFromCommandList(self):
        """ Builds a list of features for an item.

        A feature needs to be listed and needs to past test
        on each item in selection in order to show up in properties.
        """
        category = self.getArgumentValue(self.ARG_CATEGORY)
        
        commandList = []
        selection = modox.ItemSelection().getRaw()
        for featureClass in rs.service.systemComponent.getOfType(rs.c.SystemComponentType.ITEM_FEATURE):
            if not featureClass.descListed:
                continue
            if featureClass.descCategory != category:
                continue
            result = True
            for rawItem in selection:
                try:
                    test = featureClass.test(modo.Item(rawItem))
                except AttributeError:
                    continue # we assume true test by default
                # Stop iterating on first item to which feature cannot
                # be applied
                if not test:
                    result = False
                    break
            if result:
                commandList.append("rs.item.feature ident:{%s} state:?" % (featureClass.descIdentifier))
        return commandList

rs.cmd.bless(CmdItemFeaturesFCL, 'rs.item.featuresFCL')