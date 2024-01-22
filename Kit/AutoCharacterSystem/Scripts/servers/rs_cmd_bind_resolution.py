
import lx
import modo
import modox
import rs


class CmdAddBindResolution(rs.RigCommand):
    
    ARG_NAME = 'name'
    
    def arguments(self):
        argName = rs.cmd.Argument(self.ARG_NAME, 'string')
        argName.defaultValue = 'New'
        return [argName] + rs.RigCommand.arguments(self)

    def execute(self, msg, flags):
        editRig = self.firstRigToEdit
        resolutionName = self.getArgumentValue(self.ARG_NAME)
        if not resolutionName:
            return
        
        res = rs.Resolutions(editRig.rootItem)
        result = res.addResolution(resolutionName)
        if not result:
            msg.set(rs.c.MessageTable.CMDABORT, 'newMResExists')
            return False
        else:
            # Notify UI.
            # TODO: This is excessive, need to optimise later.
            rs.service.notify(rs.c.Notifier.UI_GENERAL, lx.symbol.fCMDNOTIFY_DATATYPE)
            # Reset the bind context
            rs.Scene().contexts.refreshCurrent()

lx.bless(CmdAddBindResolution, 'rs.bind.addResolution')


class CmdRemoveBindResolution(rs.RigCommand):
    
    ARG_NAME = 'name'
    
    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argName = rs.cmd.Argument(self.ARG_NAME, 'string')
        argName.flags = 'optional'
        argName.defaultValue = ''

        return [argName] + superArgs

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        rig = self.rigToQuery
        if rig is None:
            return False

        res = rs.Resolutions(rig.rootItem)
        if res.resolutionsCount > 1:
            return True
        msg.set(rs.c.MessageTable.CMDABORT, 'delMResOne')
        return False

    def interact(self):
        res = rs.Resolutions(self.rigToQuery.rootItem)
        resName = self._getResolutionToDeleteName(res)
        if not resName:
            return False
        result = modo.dialogs.okCancel("Delete Mesh Resolution", "Are you sure you want to delete %s mesh resolution?" % resName)
        if result == 'cancel':
            return False
        return True

    def execute(self, msg, flags):
        editRig = self.firstRigToEdit
        res = rs.Resolutions(editRig.rootItem)

        resolutionName = self._getResolutionToDeleteName(res)
        if not resolutionName:
            return

        result = res.removeResolution(resolutionName)
        if not result:
            rs.log.out('Resolution cannot be removed', rs.log.MSG_ERROR)
        else:
            # Notify UI.
            # TODO: This is excessive, need to optimise later.
            rs.service.notify(rs.c.Notifier.UI_GENERAL, lx.symbol.fCMDNOTIFY_DATATYPE)
            # Reset the bind context
            rs.Scene().contexts.refreshCurrent()

    # -------- Private methods

    def _getResolutionToDeleteName(self, res):
        resolutionName = self.getArgumentValue(self.ARG_NAME)
        if not resolutionName:
            resolutionName = res.currentResolution
        return resolutionName

lx.bless(CmdRemoveBindResolution, 'rs.bind.removeResolution')


class CmdRenameBindResolution(rs.RigCommand):

    ARG_NEW_NAME = 'newName'    
    ARG_NAME = 'name'
    
    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        argNewName = rs.cmd.Argument(self.ARG_NEW_NAME, 'string')
        argNewName.defaultValue = self._getDefaultResolutionName
        
        argName = rs.cmd.Argument(self.ARG_NAME, 'string')
        argName.flags = ['optional', 'hidden']
        
        return [argNewName, argName] + superArgs

    def execute(self, msg, flags):
        editRig = self.firstRigToEdit
        
        res = rs.Resolutions(editRig.rootItem)
        resolutionName = self._getResolutionToRename(res)
        if not resolutionName:
            return
        
        newName = self.getArgumentValue(self.ARG_NEW_NAME)
        try:
            res.renameResolution(resolutionName, newName)
        except LookupError:
            return
        except ValueError:
            msg.set(rs.c.MessageTable.CMDABORT, 'renameMResExists')
            return False

        rs.service.notify(rs.c.Notifier.UI_GENERAL, lx.symbol.fCMDNOTIFY_DATATYPE)
    
    # -------- Private methods

    def _getResolutionToRename(self, res):
        resolutionName = self.getArgumentValue(self.ARG_NAME)
        if not resolutionName:
            resolutionName = res.currentResolution
        return resolutionName

    def _getDefaultResolutionName(self):
        editRig = self.firstRigToEdit
        if editRig is None:
            return ""

        res = rs.Resolutions(editRig.rootItem)        
        return self._getResolutionToRename(res)
        
lx.bless(CmdRenameBindResolution, 'rs.bind.renameResolution')


class CmdShiftBindResolutionOrder(rs.RigCommand):

    ARG_DIRECTION = 'direction'    
    ARG_NAME = 'name'
    
    ORDER_HINTS = ((0, "up"),
                   (1, "down"))
    
    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        argDirection = rs.cmd.Argument(self.ARG_DIRECTION, 'integer')
        argDirection.defaultValue = 0
        argDirection.hints = self.ORDER_HINTS

        argName = rs.cmd.Argument(self.ARG_NAME, 'string')
        argName.flags = ['optional', 'hidden']
        
        return [argDirection, argName] + superArgs

    def execute(self, msg, flags):
        editRig = self.firstRigToEdit

        res = rs.Resolutions(editRig.rootItem)        
        
        order = self.getArgumentValue(self.ARG_DIRECTION) # will get int here, not a hint!!!
        resolutionName = self._getResolutionToShift(res)

        updated = False
        if order == 0:
            updated = res.moveOrderUp(resolutionName)
        elif order == 1:
            updated = res.moveOrderDown(resolutionName)

        if updated:
            rs.service.notify(rs.c.Notifier.UI_GENERAL, lx.symbol.fCMDNOTIFY_DATATYPE)
    
    # -------- Private methods

    def _getResolutionToShift(self, res):
        resolutionName = self.getArgumentValue(self.ARG_NAME)
        if not resolutionName:
            resolutionName = res.currentResolution
        return resolutionName
        
lx.bless(CmdShiftBindResolutionOrder, 'rs.bind.shiftResolutionOrder')


class CmdSwitchResolution(rs.Command):
    
    ARG_DIRECTION = 'direction'
    
    HINT_DIR_NEXT = 'next'
    HINT_DIR_PREVIOUS = 'prev'

    DIR_NEXT = 1
    DIR_PREVIOUS = 2
    
    DIRECTION_HINTS = ((DIR_NEXT, HINT_DIR_NEXT),
                       (DIR_PREVIOUS, HINT_DIR_PREVIOUS))

    def arguments(self):
        argDir = rs.cmd.Argument(self.ARG_DIRECTION, 'integer')
        argDir.hints = self.DIRECTION_HINTS
        return [argDir]

    def basic_ButtonName(self):
        dir = self.getArgumentValue(self.ARG_DIRECTION)
        if dir == 1:
            key = 'nextRes'
        else:
            key = 'prevRes'
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)

    def cmd_Tooltip(self):
        dir = self.getArgumentValue(self.ARG_DIRECTION)
        if dir == 1:
            key = 'nextRes'
        else:
            key = 'prevRes'
        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDTOOLTIP, key)

    def execute(self, msg, flags):
        rsScene = rs.Scene()
        editRig = rsScene.editRig
        if editRig is None:
            return
        
        direction = self.getArgumentValue(self.ARG_DIRECTION)
        resop = rs.Resolutions(editRig.rootItem)
        
        if direction == self.DIR_NEXT:
            resop.setNext()
        elif direction == self.DIR_PREVIOUS:
            resop.setPrevious()
        else:
            return

        rs.service.notify(rs.c.Notifier.UI_GENERAL, lx.symbol.fCMDNOTIFY_DATATYPE)
        rsScene.contexts.refreshCurrent()

lx.bless(CmdSwitchResolution, 'rs.bind.switchResolution')


class CmdBindResolutionPopup(rs.Command):
    """ Set or query bind mesh resolution set using popup list.
    """

    ARG_LIST = 'list'

    def arguments(self):
        listArg = rs.cmd.Argument(self.ARG_LIST, 'integer')
        listArg.flags = 'query'
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        return [listArg]

    def query(self, argument):
        if argument == self.ARG_LIST:
            editRigRootItem = rs.Scene.getEditRigRootItemFast()
            if editRigRootItem is None:
                return 0
            
            res = rs.Resolutions(editRigRootItem)
            resolutions = res.allResolutions
            current = res.currentResolution

            if not current or not resolutions:
                return 0
            
            try:
                index = resolutions.index(current)
            except ValueError:
                index = 0
            return index

    def execute(self, msg, flags):
        resIndex = self.getArgumentValue(self.ARG_LIST)

        rsScene = rs.Scene()
        editRig = rsScene.editRig
        if editRig is None:
            return
        
        resop = rs.Resolutions(editRig.rootItem)
        resolutions = resop.allResolutions
        if not resolutions or len(resolutions) == 0:
            return
        
        try:
            resolutionName = resolutions[resIndex]
        except IndexError:
            return
        
        resop.currentResolution = resolutionName

        rs.service.notify(rs.c.Notifier.UI_GENERAL, lx.symbol.fCMDNOTIFY_DATATYPE)
        rsScene.contexts.refreshCurrent()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)

        # React to changes to current Rig graph
        notifiers.append(('graphs.event', '%s +t' % rs.c.Graph.EDIT_RIG))

        return notifiers

    # -------- Private methods

    def _buildPopup(self):
        entries = []
        editRig = rs.Scene().editRig
        if editRig is not None:
            resop = rs.Resolutions(editRig.rootItem)
            resolutions = resop.allResolutions
            if resolutions and len(resolutions) > 0:
                entries = resolutions
        return entries

rs.cmd.bless(CmdBindResolutionPopup, 'rs.bind.resolutionPopup')


class CmdMeshResolution(rs.RigCommand):
    """ Gets/sets current resolution.
    """

    ARG_RESOLUTION = 'res'
    ARG_STATE = 'state'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        resLayer = rs.cmd.Argument(self.ARG_RESOLUTION, 'string')
        resLayer.defaultValue = ''

        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = 'query'
        state.defaultValue = False

        return [resLayer, state] + superArgs

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def basic_ButtonName(self):
        """ Button name should be name of the resolution.
        """
        return self.getArgumentValue(self.ARG_RESOLUTION)
           
    def execute(self, msg, flags):
        resName = self.getArgumentValue(self.ARG_RESOLUTION)
        
        rootItem = rs.Scene.getEditRigRootItemFast()
        resolutions = rs.Resolutions(rootItem)
        
        resolutions.currentResolution = resName

        rs.service.notify(rs.c.Notifier.UI_GENERAL, lx.symbol.fCMDNOTIFY_DATATYPE)
        rs.Scene().contexts.refreshCurrent()
        
    def query(self, argument):       
        if argument == self.ARG_STATE:
            resName = self.getArgumentValue(self.ARG_RESOLUTION)
            if not resName:
                return False
    
            rootItem = rs.Scene.getEditRigRootItemFast()
            resolutions = rs.Resolutions(rootItem)
            
            return resName == resolutions.currentResolution
        return False

rs.cmd.bless(CmdMeshResolution, 'rs.bind.resolution')


class CmdResolutionsFCL(rs.RigCommand):

    ARG_RESOLUTIONS_LIST = 'resolutionsList'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        cmdList = rs.cmd.Argument(self.ARG_RESOLUTIONS_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFormCommandList
        cmdList.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST
        return [cmdList] + superArgs

    def execute(self, msg, flags):
        pass

    def query(self, argIndex):
        pass

    def _buildFormCommandList(self):
        rootItem = rs.Scene.getEditRigRootItemFast()
        if rootItem is None:
            return []
        commandList = []
        resolutions = rs.Resolutions(rootItem)

        cmd = "rs.bind.resolution {%s} ?"
        for resolutionName in resolutions:
            commandList.append(cmd % (resolutionName))
        return commandList

rs.cmd.bless(CmdResolutionsFCL, 'rs.bind.resolutionsFCL')


class CmdBindMeshToggle(rs.Command):
    """ Toggles bind mesh included/excluded state for a current resolution layer.
    """

    ARG_MESH = 'mesh'
    ARG_RESOLUTION = 'res'
    ARG_STATE = 'state'

    def arguments(self):
        mesh = rs.cmd.Argument(self.ARG_MESH, '&item')
        mesh.defaultValue = ''
        
        resLayer = rs.cmd.Argument(self.ARG_RESOLUTION, 'string')
        resLayer.defaultValue = ''

        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = 'query'
        state.defaultValue = False

        return [mesh, resLayer, state]

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def basic_ButtonName(self):
        """ Button name should be name of bind mesh item.
        """
        meshItem = modo.Scene().item(self.getArgumentValue(self.ARG_MESH))
        return meshItem.name
    
    def icon(self):
        return 'prim.cube'
        
    def enable(self, msg):
        editRigRootItem = rs.Scene.getEditRigRootItemFast()
        if editRigRootItem is None:
            return False
        resop = rs.Resolutions(editRigRootItem)
        return resop.currentResolution is not None

    def execute(self, msg, flags):
        resName = self.getArgumentValue(self.ARG_RESOLUTION)
        if not resName:
            return

        meshIdent = self.getArgumentValue(self.ARG_MESH)
        meshItem = modo.Scene().item(meshIdent)
        
        try:
            rigItem = rs.ItemUtils.getItemFromModoItem(meshItem)
        except TypeError:
            return
        
        state = self.getArgumentValue(self.ARG_STATE)
        result = False
        if state:
            try:
                rigItem.addToResolution(resName)
            except AttributeError:
                pass
            else:
                result = True
        else:
            try:
                rigItem.removeFromResolution(resName)
            except AttributeError:
                pass
            else:
                result = True

        # Reset the bind context
        if result:
            rs.Scene().contexts.refreshCurrent()

    def query(self, argument):       
        if argument == self.ARG_STATE:
            resName = self.getArgumentValue(self.ARG_RESOLUTION)
            if not resName:
                return False
    
            meshIdent = self.getArgumentValue(self.ARG_MESH)
            try:
                meshItem = modox.SceneUtils.findItemFast(meshIdent)
            except LookupError:
                return False
            
            try:
                rigItem = rs.ItemUtils.getItemFromModoItem(modo.Item(meshItem))
            except TypeError:
                return False
            
            try:
                return rigItem.isInResolution(resName)
            except AttributeError:
                return False
        return False

rs.cmd.bless(CmdBindMeshToggle, 'rs.bind.meshResolution')


class CmdResolutionMeshesFCL(rs.Command):

    ARG_ELEMENT_SET = 'elementSet'
    ARG_MESHES_LIST = 'meshesList'

    def arguments(self):
        elset = rs.cmd.Argument(self.ARG_ELEMENT_SET, 'string')

        cmdList = rs.cmd.Argument(self.ARG_MESHES_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFormCommandList
        cmdList.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST
        return [elset, cmdList]

    def execute(self, msg, flags):
        pass

    def query(self, argIndex):
        pass

    def _buildFormCommandList(self):
        commandList = []
        rsScene = rs.Scene()
        editRig = rsScene.editRig
        if editRig is not None:
            elementSet = self.getArgumentValue(self.ARG_ELEMENT_SET)
            resop = rs.Resolutions(editRig.rootItem)
            currentRes = resop.currentResolution
            if currentRes is None:
                currentRes = ''
            for mesh in editRig[elementSet].elements:
                commandList.append("%s {%s} {%s} state:?" % ('rs.bind.meshResolution', mesh.id, currentRes))
        return commandList

rs.cmd.bless(CmdResolutionMeshesFCL, 'rs.bind.resolutionMeshesFCL')