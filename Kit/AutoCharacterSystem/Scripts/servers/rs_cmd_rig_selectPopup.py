

import lx
import lxu
import modo

import rs


class CmdSelectRigPopup(rs.Command):
    """ Set or query selected rigs using popup.
    """

    ARG_LIST = "list"

    def arguments(self):
        listArg = rs.cmd.Argument(self.ARG_LIST, "integer")
        listArg.flags = "query"
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        return [listArg]

    def query(self, argument):
        """ Query selected rig index.
        
        Can also set special option (All) and (Multiple)
        """
        if argument == self.ARG_LIST:
            
            rigRootItems = rs.Scene.getRigRootItemsFast()
            rigsCount = len(rigRootItems)
            selectedRigIdents = []
            for root in rigRootItems:
                if root.selected:
                    selectedRigIdents.append(root.modoItem.id)
            selectedCount = len(selectedRigIdents)
            
            if rigsCount > 1: # Multiple rigs in scene
                # All selected
                if selectedCount == 0:
                    return 0
                elif selectedCount > 1:
                    if selectedCount < rigsCount:
                        return 1 # Multiple
                    else:
                        return 0 # All rigs are selected
            
            if not selectedRigIdents:
                return 0
            
            rigIdents = [root.modoItem.id for root in rigRootItems]
            pickRigIdent = selectedRigIdents[0]

            try:
                index = rigIdents.index(pickRigIdent)
            except ValueError:
                rs.log.out("Cannot determine selected rig properly!", messageType=rs.log.MSG_ERROR)
                return 0 

            return index + 1 # Account for the (all) option that's always there.

    def execute(self, msg, flags):
        identIndex = self.getArgumentValue(self.ARG_LIST)
        if identIndex < 0:
            return
        
        rsScene = rs.Scene()
        rigs = rsScene.rigs

        if identIndex == 0: # All rigs so clear all rigs selected.
            for rig in rigs:
                rig.selected = False
            rs.service.notify(rs.c.Notifier.RIG_SELECTION, rs.c.Notify.DATATYPE)
            return
        
        selectedCount = rsScene.directlySelectedRigsCount
        hasMultiple = False
        if selectedCount > 1 and selectedCount < len(rigs): # Multiple selection available
            hasMultiple = True
        
        # Multiple is selected, don't do anything
        if hasMultiple and identIndex == 1:
            return
        
        indexOffset = -1
        if hasMultiple:
            indexOffset = -2

        indexToSelect = identIndex + indexOffset
        if indexToSelect < 0 or indexToSelect >= len(rigs):
            return
        
        for rig in rigs:
            rig.selected = False
        rigs[indexToSelect].selected = True
        rs.service.notify(rs.c.Notifier.RIG_SELECTION, rs.c.Notify.DATATYPE)

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)

        # For the popup to refresh command needs to react to
        # datatype change when new rig root item is added or removed
        notifiers.append(('item.event', "add[%s] +t" % rs.c.RigItemType.ROOT_ITEM))
        notifiers.append(('item.event', "remove[%s] +t" % rs.c.RigItemType.ROOT_ITEM))
        
        # We also need to react when root item name changes.
        notifiers.append(('item.event', "name[%s] +t" % rs.c.RigItemType.ROOT_ITEM))

        # React to changes to current Rig graph as well
        # this changes current selection.
        notifiers.append(('graphs.event', '%s +t' % rs.Scene.GRAPH_EDIT_RIG))

        # React to scene selection change with datatype flag.
        # Popup contents won't be rebuilt on scene selection change otherwise.
        notifiers.append(('select.event', 'cinema +dt'))

        notifiers.append((rs.c.Notifier.RIG_SELECTION, '+t'))

        return notifiers

    def _buildPopup(self):
        """ Builds the popup with rigs to select.
        
        The popup has the (all) entry for when no rigs are selected = all rigs are selected.
        
        When multiple rigs are selected an extra (Multiple) entry needs to be added.
        This is only when multiple rigs selection does not include all rigs in scene.
        """
        entries = []
            
        scene = rs.Scene()
        selectedCount = scene.directlySelectedRigsCount
        rigs = scene.rigs
        
        #if scene.rigsCount > 1:
        entries.append(('all', '(All)'))

        if selectedCount > 1 and selectedCount < len(rigs):
            entries.append(('multi', '(Multiple)'))

        for rig in rigs:
            entries.append((rig.sceneIdentifier, rig.name))
        return entries

rs.cmd.bless(CmdSelectRigPopup, 'rs.rig.selectPopup')