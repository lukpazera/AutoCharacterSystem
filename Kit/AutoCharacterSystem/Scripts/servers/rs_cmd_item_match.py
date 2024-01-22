

import lx
import lxu
import modo
import modox

import rs


def testItem(rawItem):
    """
    """
    return modox.Item(rawItem).isOfXfrmCoreSuperType


class ItemsListContent(rs.cmd.ArgumentItemsContent):
    def __init__(self):
        self.noneOption = True
        self.testOnRawItems = True
        self.itemTestFunction = testItem


class RSCmdMatchItemLink(rs.base_OnItemFeatureCommand):

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.MatchTransformItemFeature
    
    ARG_TO_ITEM = 'toItem'
    
    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
                
        toItemArg = rs.cmd.Argument(self.ARG_TO_ITEM, '&item')
        toItemArg.flags = 'query'
        toItemArg.valuesListUIType = rs.cmd.ArgumentValuesListType.ITEM_POPUP
        toItemArg.valuesList = ItemsListContent()
        
        return [toItemArg] + superArgs

    def notifiers(self):
        """ This command doesn't need to update its disable/enable state.
        By returning empty list we clear any default notifiers.
        """
        return []

    def enable(self, msg):
        return self.itemFeatureToQuery is not None

    def execute(self, msg, flags): 
        # itemid will be empty string if none option was chosen.
        itemid = self.getArgumentValue(self.ARG_TO_ITEM)
        matchFeatures = self.itemFeaturesToEdit
        scene = modo.Scene()
        toItem = None
            
        if itemid:
            try:
                toItem = modo.Item(modox.SceneUtils.findItemFast(itemid))
            except LookupError:
                pass

        for feature in matchFeatures:
            feature.referenceItem = toItem

    def query(self, argument):
        if argument == self.ARG_TO_ITEM:
            feature = self.itemFeatureToQuery
            if feature is not None:
                return feature.referenceItem
            
rs.cmd.bless(RSCmdMatchItemLink, 'rs.item.matchXfrmLink')
