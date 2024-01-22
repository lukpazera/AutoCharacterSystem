

import lx
import lxu
import modo

import rs


class CmdSelectRigFromSceneItems(rs.Command):
    """ Selects rigs in scene from items selected in scene.
    """

    def execute(self, msg, flags):
        scene = rs.Scene()
        selectedItems = modo.Scene().selected
        
        rigRoots = []
        rigItems = []
        for modoItem in selectedItems:
            try:
                rigItem = rs.ItemUtils.getItemFromModoItem(modoItem)
            except TypeError:
                continue
            if isinstance(rigItem, rs.RootItem):
                rigRoots.append(rigItem)
            else:
                rigItems.append(rigItem)
        
        if not rigRoots:
            for rigItem in rigItems:
                rigRoots.append(rigItem.rigRootItem)
            scene.select(rigRoots)

        scene.select(rigRoots)
        rs.service.notify(rs.c.Notifier.RIG_SELECTION, rs.c.Notify.DATATYPE)
            
rs.cmd.bless(CmdSelectRigFromSceneItems, 'rs.rig.selectFromScene')


class CmdSelectRig(rs.RigCommand):
    """ Selects rigs in scene additively.
    
    Either select a rig directly if its root is selected
    or go through item selection and select all rigs selected items
    belong to.
    """

    ARG_STATE = 'state'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        stateArg = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        stateArg.flags = 'query'
        stateArg.defaultValue = False
        
        return [stateArg] + superArgs

    def execute(self, msg, flags):
        scene = rs.Scene()
        state = self.getArgumentValue(self.ARG_STATE)
 
        scene.select(self.rigsToEdit, state=state, replace=False)

        rs.service.notify(rs.c.Notifier.RIG_SELECTION, rs.c.Notify.DATATYPE)

    def query(self, argument):
        if argument == self.ARG_STATE:
            rig = self.rigToQuery
            if rig is None:
                return False
            return rig.selected

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers
        
rs.cmd.bless(CmdSelectRig, 'rs.rig.selected')