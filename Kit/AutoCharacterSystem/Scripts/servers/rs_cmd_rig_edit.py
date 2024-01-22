

import lx
import lxu
import modo

import rs


class CmdEditRigPopup(rs.Command):
    """ Set or query the edit rig using popup list.
    """

    ARG_LIST = "list"

    def arguments(self):
        listArg = rs.cmd.Argument(self.ARG_LIST, "integer")
        listArg.flags = "query"
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        return [listArg]

    def query(self, argument):
        """ Query current edit rig index.
        
        Note that the list of rigs is not sorted in any way at this point.
        """
        if argument == self.ARG_LIST:
            roots = rs.Scene.getRigRootModoItemsFast()
            if not roots:
                return 0

            editRigRootItem = rs.Scene.getEditRigRootItemFast()
            if editRigRootItem is None:
                return 0
            
            rigIdents = [root.Ident() for root in roots]

            try:
                index = rigIdents.index(editRigRootItem.modoItem.id)
            except ValueError:
                rs.log.out("%s: Edit rig graph is corrupted!" % self.name, messageType=rs.log.MSG_ERROR)
                return 0 

            return index

    def execute(self, msg, flags):
        identIndex = self.getArgumentValue(self.ARG_LIST)
        if identIndex < 0:
            return
        rsScene = rs.Scene()
        rigIdents = [rig.sceneIdentifier for rig in rsScene.rigs]
        if identIndex < len(rigIdents):
            rigToEdit = rs.Rig(rigIdents[identIndex])
            rsScene.editRig = rigToEdit
            rigToEdit.rootModoItem.select(replace=True)
    
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

        return notifiers

    def _buildPopup(self):
        entries = []
        for rig in rs.Scene().rigs:
            entries.append((rig.sceneIdentifier, rig.name))
        return entries

rs.cmd.bless(CmdEditRigPopup, 'rs.rig.editPopup')


class CmdEditRig(rs.RigCommand):
    """ Sets edit rig directly using its root item identifier.
    """

    def execute(self, msg, flags):
        rig = self.rigToQuery
        if rig is None:
            
            return
        rsScene = rs.Scene()
        try:
            rsScene.editRig = rig #rootIdent
        except TypeError:
            pass

rs.cmd.bless(CmdEditRig, 'rs.rig.edit')