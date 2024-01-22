

import lx
import lxu
import modo
import modox

import rs


def testItem(rawItem):
    """ Accept rig items only.
    """
    if not modox.Item(rawItem).isOfXfrmCoreSuperType:
        return False
    try:
        rigItem = rs.Item.getFromOther(rawItem)
    except TypeError:
        return False
    return True


class ItemsListContent(rs.cmd.ArgumentItemsContent):
    def __init__(self):
        self.noneOption = True
        self.testOnRawItems = True
        self.itemTestFunction = testItem


class RSCmdFKIKMatchTarget(rs.base_OnItemFeatureCommand):
    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.ikfk.IKSolverMatchExtras

    ARG_TARGET_ITEM = 'toItem'

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)

        targetItemArg = rs.cmd.Argument(self.ARG_TARGET_ITEM, '&item')
        targetItemArg.flags = 'query'
        targetItemArg.valuesListUIType = rs.cmd.ArgumentValuesListType.ITEM_POPUP
        targetItemArg.valuesList = ItemsListContent()

        return [targetItemArg] + superArgs

    def notifiers(self):
        """ This command doesn't need to update its disable/enable state.
        By returning empty list we clear any default notifiers.
        """
        return []

    def enable(self, msg):
        return self.itemFeatureToQuery is not None

    def execute(self, msg, flags):
        # itemid will be empty string if none option was chosen.
        itemid = self.getArgumentValue(self.ARG_TARGET_ITEM)
        features = self.itemFeaturesToEdit

        targetItem = None

        if itemid:
            try:
                targetItem = modo.Item(modox.SceneUtils.findItemFast(itemid))
            except LookupError:
                pass

        for feature in features:
            feature.ikMatchTargetItem = targetItem

    def query(self, argument):
        if argument == self.ARG_TARGET_ITEM:
            feature = self.itemFeatureToQuery
            if feature is not None:
                return feature.ikMatchTargetItem

rs.cmd.bless(RSCmdFKIKMatchTarget, 'rs.ikfk.matchTarget')


class RSCmdFKIKMatchReference(rs.base_OnItemFeatureCommand):
    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.ikfk.IKSolverMatchExtras

    ARG_TARGET_ITEM = 'toItem'

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)

        targetItemArg = rs.cmd.Argument(self.ARG_TARGET_ITEM, '&item')
        targetItemArg.flags = 'query'
        targetItemArg.valuesListUIType = rs.cmd.ArgumentValuesListType.ITEM_POPUP
        targetItemArg.valuesList = ItemsListContent()

        return [targetItemArg] + superArgs

    def notifiers(self):
        """ This command doesn't need to update its disable/enable state.
        By returning empty list we clear any default notifiers.
        """
        return []

    def enable(self, msg):
        return self.itemFeatureToQuery is not None

    def execute(self, msg, flags):
        # itemid will be empty string if none option was chosen.
        itemid = self.getArgumentValue(self.ARG_TARGET_ITEM)
        features = self.itemFeaturesToEdit

        targetItem = None

        if itemid:
            try:
                targetItem = modo.Item(modox.SceneUtils.findItemFast(itemid))
            except LookupError:
                pass

        for feature in features:
            feature.ikMatchTargetReferenceItem = targetItem

    def query(self, argument):
        if argument == self.ARG_TARGET_ITEM:
            feature = self.itemFeatureToQuery
            if feature is not None:
                return feature.ikMatchTargetReferenceItem

rs.cmd.bless(RSCmdFKIKMatchReference, 'rs.ikfk.matchTargetRef')


class RSCmdFKIKMatchGoalReference(rs.base_OnItemFeatureCommand):
    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.ikfk.IKSolverMatchExtras

    ARG_TARGET_ITEM = 'toItem'

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)

        targetItemArg = rs.cmd.Argument(self.ARG_TARGET_ITEM, '&item')
        targetItemArg.flags = 'query'
        targetItemArg.valuesListUIType = rs.cmd.ArgumentValuesListType.ITEM_POPUP
        targetItemArg.valuesList = ItemsListContent()

        return [targetItemArg] + superArgs

    def notifiers(self):
        """ This command doesn't need to update its disable/enable state.
        By returning empty list we clear any default notifiers.
        """
        return []

    def enable(self, msg):
        return self.itemFeatureToQuery is not None

    def execute(self, msg, flags):
        # itemid will be empty string if none option was chosen.
        itemid = self.getArgumentValue(self.ARG_TARGET_ITEM)
        features = self.itemFeaturesToEdit

        targetItem = None

        if itemid:
            try:
                targetItem = modo.Item(modox.SceneUtils.findItemFast(itemid))
            except LookupError:
                pass

        for feature in features:
            feature.ikMatchGoalReference = targetItem

    def query(self, argument):
        if argument == self.ARG_TARGET_ITEM:
            feature = self.itemFeatureToQuery
            if feature is not None:
                return feature.ikMatchGoalReference

rs.cmd.bless(RSCmdFKIKMatchGoalReference, 'rs.ikfk.matchGoalRef')
