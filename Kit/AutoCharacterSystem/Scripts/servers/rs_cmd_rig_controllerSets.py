

import lx
import lxu
import modo
import modox

import rs


class CmdControllersSetsPopup(rs.Command):
    """ Allows for choosing rig controller's set from a popup.
    """

    ARG_LIST = "list"

    def arguments(self):
        listArg = rs.cmd.Argument(self.ARG_LIST, "integer")
        listArg.flags = "query"
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        return [listArg]

    def query(self, argument):
        """
        """
        if argument == self.ARG_LIST:
            rig = rs.Scene().editRig
            if rig is None:
                return 0

            allSets = self._getRigItemSelectionSets(rig)
            if not allSets:
                return 0

            currentSet = rig.rootItem.controllersSet
            if currentSet is None:
                return 0

            try:
                index = allSets.index(currentSet) + 1 # Compensate for the 'None' option
            except ValueError:
                if rs.debug.output:
                    rs.log.out("%s: bad controllers selection set name store in settings!" % currentSet, messageType=rs.log.MSG_ERROR)
                return 0 

            return index

    def execute(self, msg, flags):
        identIndex = self.getArgumentValue(self.ARG_LIST)
        if identIndex < 0:
            return
        
        scene = rs.Scene()
        rig = scene.editRig
        if rig is None:
            return

        if identIndex == 0:
            newSet = None
        else:
            allSets = self._getRigItemSelectionSets(rig)
            newSet = allSets[identIndex - 1]
    
        currentSet = rig.rootItem.controllersSet
        if currentSet == newSet:
            return
        
        rig.rootItem.controllersSet = newSet
        scene.contexts.refreshCurrent()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)

        # React to changes to current Rig graph as well
        # this changes current selection.
        notifiers.append(('graphs.event', '%s +t' % rs.Scene.GRAPH_EDIT_RIG))

        return notifiers

    # -------- Private methods

    def _getRigItemSelectionSets(self, rig):
        ctrls = rig[rs.c.ElementSetType.CONTROLLERS].elements
        allSets = modox.ItemUtils.getItemSelectionSets(ctrls)
        filteredSets = [setName for setName in allSets if setName.startswith('acsctrl')]
        return filteredSets

    def _buildPopup(self):
        rig = rs.Scene().editRig
        if rig is None:
            return []

        allSets = self._getRigItemSelectionSets(rig)
        entries = []
        entries.append(('none', '(None)'))
        for iset in allSets:
            entries.append((iset, iset))
        return entries

rs.cmd.bless(CmdControllersSetsPopup, 'rs.rig.controllersSetPopup')


class CmdControllersSetsFCL(rs.Command):

    ARG_CMD_LIST = 'cmdList'

    def arguments(self):
        cmdListArg = rs.cmd.Argument(self.ARG_CMD_LIST, 'integer')
        cmdListArg.flags = 'query'
        cmdListArg.valuesList = self._buildFormCommandList
        cmdListArg.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST
        return [cmdListArg]

    def query(self, argument):
        pass

    def execute(self, msg, flags):
        pass

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)

        # React to changes to current Rig graph as well
        # this changes current selection.
        notifiers.append(('graphs.event', '%s +t' % rs.Scene.GRAPH_EDIT_RIG))

        return notifiers

    # -------- Private methods

    def _getRigItemSelectionSets(self, rig):
        ctrls = rig[rs.c.ElementSetType.CONTROLLERS].elements
        allSets = modox.ItemUtils.getItemSelectionSets(ctrls)
        filteredSets = [setName for setName in allSets if setName.startswith('acsctrl')]
        return filteredSets

    def _buildFormCommandList(self):
        rig = rs.Scene().editRig
        if rig is None:
            return []

        commandList = []
        cmd = 'rs.rig.controllersSet'
        allSets = self._getRigItemSelectionSets(rig)
        allSets.sort()
        
        for iset in allSets:
            commandList.append('%s {%s} ?' % (cmd, iset))
        return commandList

rs.cmd.bless(CmdControllersSetsFCL, 'rs.rig.controllersSetFCL')


class CmdControllersSet(rs.Command):
    """ Query/set controllers set for edit rig directly.
    """

    ARG_NAME = 'name'
    ARG_STATE = 'state'

    def arguments(self):
        nameArg = rs.cmd.Argument(self.ARG_NAME, 'string')
        nameArg.defaultValue = None

        stateArg = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        stateArg.flags = 'query'
        stateArg.defaultValue = False

        return [nameArg, stateArg]

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def query(self, argument):
        if argument == self.ARG_STATE:
            rig = rs.Scene().editRig
            if rig is None:
                return False

            querySet = self.getArgumentValue(self.ARG_NAME)
            if querySet == 'none':
                querySet = None

            currentSet = rig.rootItem.controllersSet
            if currentSet == querySet:
                return True
            
            return False

    def execute(self, msg, flags):
        state = self.getArgumentValue(self.ARG_STATE)
        if state:
            newSet = self.getArgumentValue(self.ARG_NAME)
            if not newSet:
                newSet = None
        else:
            newSet = None
                
        scene = rs.Scene()
        rig = scene.editRig
        if rig is None:
            return
    
        currentSet = rig.rootItem.controllersSet
        if currentSet == newSet:
            return
        
        rig.rootItem.controllersSet = newSet
        scene.contexts.refreshCurrent()
        rs.service.notify(rs.c.Notifier.CONTROLLER, lx.symbol.fCMDNOTIFY_VALUE)

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append((rs.c.Notifier.CONTROLLER, '+v'))
        return notifiers

rs.cmd.bless(CmdControllersSet, 'rs.rig.controllersSet')