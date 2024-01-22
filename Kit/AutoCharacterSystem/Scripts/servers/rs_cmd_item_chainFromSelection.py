

import lx
import lxu
import modo
import modox

import rs


class CmdItemChainFromSelection(rs.Command):
    """ Creates a chain of items of a given type from selection.
    """

    ARG_TYPE = 'type'

    def arguments(self):
        typeArg = rs.cmd.Argument(self.ARG_TYPE, 'string')
        typeArg.defaultValue = ''

        return [typeArg]

    def setupMode(self):
        return True

    def enable(self, msg):
        return self._testSelection()
    
    def execute(self, msg, flags):
        rigItemType = self.getArgumentValue(self.ARG_TYPE)
        if not rigItemType:
            return 

        rsScene = rs.Scene()
        editRig = rsScene.editRig
        if editRig is None:
            return
        
        editModule = editRig.modules.editModule
        if editModule is None:
            return
        
        modoItems = self._getItems()
        if not modoItems:
            return
        
        if rigItemType == rs.c.RigItemType.BIND_LOCATOR:
            self._buildBindLocatorsChainFromList(modoItems, editModule)
        elif rigItemType == rs.c.RigItemType.GUIDE:
            self._buildGuidesChainFromList(modoItems, editModule)
        else:
            chainRigItems = self._buildChainFromList(modoItems, rigItemType, editModule)

    # -------- Private methods
    
    def _testSelection(self):
        items = lxu.select.ItemSelection().current()
        if not items:
            return False
        return len(items) > 0
    
    def _getItems(self):
        items = lxu.select.ItemSelection().current()
        
        selected = []
        for item in items:
            if modox.Item(item).isOfXfrmCoreSuperType:
                selected.append(modo.Item(item))
        
        return selected

    def _buildBindLocatorsChainFromList(self, itemList, module):
        bindLocators = self._buildChainFromList(itemList, rs.c.RigItemType.BIND_LOCATOR, module)
        
        for x in range(len(bindLocators)):
            modox.TransformUtils.linkWorldTransforms(itemList[x], bindLocators[x].modoItem)

        return bindLocators

    def _buildGuidesChainFromList(self, itemList, module):
        """ This will work fully only on items that have rig properties added.
        """
        guides = self._buildChainFromList(itemList, rs.c.RigItemType.GUIDE, module)
       
        # We want to set guide for every item from the list.
        # Item needs to be rig item already.
        for x in range(len(itemList)):
            try:
                rigItem = rs.ItemUtils.getItemFromModoItem(itemList[x])
            except TypeError:
                continue
            
            features = rs.ItemFeatures(rigItem)
            if features.hasFeature(rs.c.ItemFeatureType.GUIDE):
                guideFeature = features.getFeature(rs.c.ItemFeatureType.GUIDE)
            else:
                guideFeature = features.addFeature(rs.c.ItemFeatureType.GUIDE)
            guideFeature.guide = guides[x]

        return guides

    def _buildChainFromList(self, itemList, itemType, module):
        """ Builds a chain of rig items of given type from a list of modo items.
        
        Parameters
        ----------
        itemList : list of modo.Item
            Items need to be of xfrmcore super type.
        
        itemType : str
        
        module : Module
            module to add new items to.
        
        Returns
        -------
        list of Item
        """
    
        newItems = []
        for item in itemList:
            try:
                rigItem = rs.ItemUtils.getItemFromModoItem(item)
            except TypeError:
                name = item.name
            else:
                name = rigItem.name
            newModoItem = module.newItem(itemType, name=name)
            newItems.append(newModoItem)
    
        # Parenting
        if len(newItems) > 1:
            for x in range(1, len(newItems)):
                newItems[x].modoItem.setParent(newItems[x - 1].modoItem)
    
        # Transform matching
        for x in range(len(newItems)):
            rs.run('!item.match item pos average:false item:{%s} itemTo:{%s}' % (newItems[x].modoItem.id, itemList[x].id))
            rs.run('!item.match item rot average:false item:{%s} itemTo:{%s}' % (newItems[x].modoItem.id, itemList[x].id))
            rs.run('!item.match item scl average:false item:{%s} itemTo:{%s}' % (newItems[x].modoItem.id, itemList[x].id))
    
        return newItems

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+d'))
        return notifiers

rs.cmd.bless(CmdItemChainFromSelection, 'rs.item.chainFromSelection')