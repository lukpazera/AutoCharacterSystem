

import lx
import lxu
import modo
import modox

import rs


class RSCmdIKFKChain(rs.base_OnItemFeatureCommand):

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.IKFKSwitcherItemFeature

    ARG_TYPE = 'type'
    ARG_TO_ITEM = 'toItem'

    TYPE_HINTS = ((0, 'fk'),
                  (1, 'ik'),
                  (2, 'slvdrv'))

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)

        toItemArg = rs.cmd.Argument(self.ARG_TO_ITEM, 'integer')
        toItemArg.flags = 'query'
        toItemArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        toItemArg.valuesList = self._buildPopup

        typeArg = rs.cmd.Argument(self.ARG_TYPE, 'integer')
        typeArg.flags = 'optional'
        typeArg.defaultValue = 0
        typeArg.hints = self.TYPE_HINTS

        return [toItemArg, typeArg] + superArgs

    def notifiers(self):
        """ This command doesn't need to update its disable/enable state.
        By returning empty list we clear any default notifiers.
        """
        return []

    def enable(self, msg):
        return self.itemFeatureToQuery is not None

    def execute(self, msg, flags): 
        # itemid will be empty string if none option was chosen.
        listIndex = self.getArgumentValue(self.ARG_TO_ITEM)
        chainType = self.getArgumentValue(self.ARG_TYPE)
        features = self.itemFeaturesToEdit

        for feature in features:
            if listIndex == 0:
                if chainType == 0:  # fk
                    feature.fkChain = None
                elif chainType == 1:  # ik
                    feature.ikChain = None
                elif chainType == 2:  # solver driver items
                    feature.ikSolverDriver = None
            else:
                modRoot = feature.item.moduleRootItem
                ikfkOp = rs.ikfk.IKFKChainOperator(modRoot)
                allChainGroups = ikfkOp.chainItemGroups
                listIndex -= 1 # To compensate for the None option

                if listIndex >= len(allChainGroups):
                    return

                if chainType == 0:  # fk
                    feature.fkChain = allChainGroups[listIndex]
                elif chainType == 1:  # ik
                    feature.ikChain = allChainGroups[listIndex]
                elif chainType == 2:  # solver driver items
                    feature.ikSolverDriver = allChainGroups[listIndex]

    def query(self, argument):
        if argument == self.ARG_TO_ITEM:
            feature = self.itemFeatureToQuery
            if feature is None:
                return 0 # None option
            
            chainGroupItem = self._getChainGroupItem(feature)
            if chainGroupItem is None:
                return 0 # None option
            
            modRoot = feature.item.moduleRootItem
            ikfkOp = rs.ikfk.IKFKChainOperator(modRoot)
            allChains = ikfkOp.chainItemGroups
            index = 0
            for item in allChains:
                index += 1
                if item == chainGroupItem:
                    return index
            return 0

    # -------- Private methods

    def _getChainGroupItem(self, feature):
        tp = self.getArgumentValue(self.ARG_TYPE)
        if tp == 0:  # fk
            return feature.fkChain
        elif tp == 1:  # ik
            return feature.ikChain
        elif tp == 2:  # solver drivers
            return feature.ikSolverDriver
        return None

    def _buildPopup(self):
        content = rs.cmd.ArgumentPopupContent()

        noneEntry = rs.cmd.ArgumentPopupEntry("$none$", "(none)")
        content.addEntry(noneEntry)

        feature = self.itemFeatureToQuery
        if feature is None:
            return []

        modRoot = feature.item.moduleRootItem
        ikfkOp = rs.ikfk.IKFKChainOperator(modRoot)

        allChainGroups = ikfkOp.chainItemGroups
        
        for chainItem in allChainGroups:
            username = chainItem.name

            entry = rs.cmd.ArgumentPopupEntry(chainItem.modoItem.id, username)
            content.addEntry(entry)
        return content

rs.cmd.bless(RSCmdIKFKChain, 'rs.ikfk.chainGroup')


def testIKFKBlendItem(rawItem):
    """ Accept rig items only.
    """
    if not modox.Item(rawItem).isOfXfrmCoreSuperType:
        return False
    try:
        rigItem = rs.Item.getFromOther(rawItem)
    except TypeError:
        return False
    return True


class IKBlendItemsListContent(rs.cmd.ArgumentItemsContent):
    def __init__(self):
        self.noneOption = True
        self.testOnRawItems = True
        self.itemTestFunction = testIKFKBlendItem


class RSCmdIKFKBlendCtrl(rs.base_OnItemFeatureCommand):

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.IKFKSwitcherItemFeature
    
    ARG_TO_ITEM = 'toItem'
    
    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
                
        toItemArg = rs.cmd.Argument(self.ARG_TO_ITEM, '&item')
        toItemArg.flags = 'query'
        toItemArg.valuesListUIType = rs.cmd.ArgumentValuesListType.ITEM_POPUP
        toItemArg.valuesList = IKBlendItemsListContent()
        
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
        features = self.itemFeaturesToEdit
        scene = modo.Scene()
        toItem = None
            
        if itemid:
            try:
                toItem = modo.Item(modox.SceneUtils.findItemFast(itemid))
            except LookupError:
                pass

        for feature in features:
            feature.ikfkBlendController = toItem

    def query(self, argument):
        if argument == self.ARG_TO_ITEM:
            feature = self.itemFeatureToQuery
            if feature is not None:
                return feature.ikfkBlendControllerModoItem

rs.cmd.bless(RSCmdIKFKBlendCtrl, 'rs.ikfk.blendCtrl')


class RSCmdIKFKBlendChannel(rs.base_OnItemFeatureCommand):
    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.IKFKSwitcherItemFeature

    ARG_INDEX = 'index'

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)

        toItemArg = rs.cmd.Argument(self.ARG_INDEX, 'integer')
        toItemArg.flags = 'query'
        toItemArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        toItemArg.valuesList = self._buildPopup

        return [toItemArg] + superArgs

    def enable(self, msg):
        return self.itemFeatureToQuery is not None

    def execute(self, msg, flags):
        index = self.getArgumentValue(self.ARG_INDEX)
        features = self.itemFeaturesToEdit

        index -= 1 # to account for None option.

        for feature in features:
            if index < 0:
                feature.blendingChannel = None
                continue

            blendCtrl = feature.ikfkBlendControllerModoItem
            if blendCtrl is None:
                continue
            userChans = modox.Item(blendCtrl.internalItem).getUserChannelsNames(sort=True)
            try:
                chanName = userChans[index]
            except ValueError:
                chanName = None

            feature.blendingChannel = chanName

    def query(self, argument):
        if argument == self.ARG_INDEX:
            feature = self.itemFeatureToQuery
            if feature is None:
                return 0 # None option
            try:
                blendChan = feature.blendingChannel
            except LookupError:
                return 0 # None option

            userChanNames = modox.Item(blendChan.item.internalItem).getUserChannelsNames(sort=True)

            try:
                index = userChanNames.index(blendChan.name)
            except ValueError:
                index = -1

            if index < 0:
                return 0 # None option
            return index + 1 # Account for the (none) option

    def _buildPopup(self):
        entries = [('none', '(None)')]
        feature = self.itemFeatureToQuery

        blendCtrl = feature.ikfkBlendControllerModoItem
        if blendCtrl is None:
            return entries

        userChannels = modox.Item(blendCtrl.internalItem).getUserChannels(sort=True)

        for channel in userChannels:
            entries.append((channel.name, modox.ChannelUtils.getChannelUsername(channel)))
        return entries

rs.cmd.bless(RSCmdIKFKBlendChannel, 'rs.ikfk.blendChannel')