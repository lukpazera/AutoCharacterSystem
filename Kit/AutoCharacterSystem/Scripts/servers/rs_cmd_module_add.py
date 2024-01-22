

import lx
import lxu
import modo
import modox

import rs


class CmdAddModule(rs.Command):
    """ Adds an existing module to the rig.

    Arguments
    ---------
    ARG_ROOT_ITEM
        root item of the module or module set to add.
    """

    ARG_ROOT_ITEM = 'rootItem'
    ARG_DROP_ACTION = 'dropAction'
    ARG_TYPE = 'type'

    TYPE_HINTS = ((0, 'module'),
                  (1, 'moduleset'))

    def arguments(self):
        rootItem = rs.cmd.Argument(self.ARG_ROOT_ITEM, '&item')
        
        underMouse = rs.cmd.Argument(self.ARG_DROP_ACTION, 'boolean')
        underMouse.flags = 'optional'
        underMouse.defaultValue = True

        argType = rs.cmd.Argument(self.ARG_TYPE, 'integer')
        argType.hints = self.TYPE_HINTS
        argType.flags = 'optional'
        argType.defaultValue = 0

        return [rootItem, underMouse, argType]

    def enable(self, msg):
        """ This command should always be enabled.
        """
        return True

    def setupMode(self):
        return True

    def applyEditActionPost(self):
        return True

    def execute(self, msg, flags):
        # Take the viewport position ASAP because user can move mouse pointer
        # during the execution of a command. It's still too late though.
        # TODO: Need to figure out how to grab mouse position right after the preset
        # is dropped into viewport and not when its drop script command is being launched.
        # This eventually may need to be part of the drop server!
        enableDropAction = self.getArgumentValue(self.ARG_DROP_ACTION)
        if enableDropAction:
            viewportPosition = modox.ViewUtils.get3DPositionFromMouseOver3DView()

        rsScene = rs.Scene()
        editRig = rsScene.editRig
        if editRig is None:
            rs.run('rs.rig.new empty:false')
            rsScene.scan()
            editRig = rsScene.editRig
            if editRig is None:
                return

        assetType = self.getArgumentValue(self.ARG_TYPE)
        rootItemIdent = self.getArgumentValue(self.ARG_ROOT_ITEM)

        try:
            rootModoItem = modo.Scene().item(rootItemIdent)
        except LookupError:
            return

        mod = None

        # First, add modules or module set to rig
        if assetType == 0: # module
            try:
                mod = rs.Module(rootModoItem)
            except TypeError:
                return
            editRig.modules.addModule(mod)
        else:
            # TODO: Handling module sets is clunky, improve that sometime.
            # Note that we add modules from moduleset correctly here
            # but later down the line after these are added we resize main module
            # and its submodules. This is fine as long as module set is main module + its submodules.
            # When module sets are more robust this code needs to be updated.
            try:
                modset = rs.ModuleSet(rootModoItem)
            except TypeError:
                return

            # Get first module from module set before module set gets added to rig.
            # This is because modules from the set will be added to rig directly
            # and the set will be empty afterwards.
            modSetModules = modset.modules
            if modSetModules:
                mod = modSetModules[0]

            editRig.modules.addModuleSet(modset)

        # If silent drop is set to True on Module Operator we do not perform drop action
        # and we do not refresh the context.
        if rs.service.globalState.ControlledDrop:
            return

        # Peform drop action
        if enableDropAction:
            # Add single module
            self._applyDropAction(mod, viewportPosition)
            modulesToUpdateGuideFor = [mod]

            # Resize all submodules.
            submodules = mod.submodules
            for submodule in submodules:
                # Don't pass viewport position to submodules here so they don't get
                # repositioned under the mouse and preserve their relative positions to main module.
                self._applyDropAction(submodule, None)
            modulesToUpdateGuideFor += submodules

            guide = rs.Guide(editRig)
            guide.apply(modulesToUpdateGuideFor)

        # Dropping module needs to switch to assembly context by default
        # unless assembly, dev or guide context is already on.
        if rsScene.context in [rs.c.Context.ASSEMBLY, rs.c.Context.GUIDE]:
            rsScene.refreshContext()
        else:
            rsScene.context = rs.c.Context.ASSEMBLY

        if mod:
            editRig.modules.editModule = mod
            modo.Scene().select(mod.rootModoItem)
            modox.Item(mod.rootModoItem.internalItem).autoFocusInItemList()

    # -------- Private methods
    
    def _applyDropAction(self, module, viewportPosition):
        """ Applies drop action on a given module.
        
        Parameters
        ----------
        viewportPosition : modo.Vector3, None
            None is passed if module is simply loaded and not dragged and dropped.
        """
        modGuide = rs.ModuleGuide(module)
        dropAction = module.dropAction
        dropActionPerformed = False

        rs.service.events.send(rs.c.EventTypes.MODULE_DROP_ACTION_PRE,
                               module=module,
                               action=dropAction,
                               position=viewportPosition)

        # Snap guide to mouse position.
        if dropAction == rs.c.ModuleDropAction.SNAP_TO_MOUSE:
            if viewportPosition is None:
                return
            modGuide.setToPosition(viewportPosition)
            dropActionPerformed = True
        
        # Snap to group
        elif dropAction == rs.c.ModuleDropAction.REST_ON_GROUND:
            # Offset the guide so it rests on ground.
            modGuide.snapToGround()
            
        # Snap to mouse and scale guide so it rests on ground
        elif dropAction == rs.c.ModuleDropAction.MOUSE_AND_GROUND:
            modGuide.setToPositionAndFitToGround(viewportPosition)
            dropActionPerformed = True
        
        if dropActionPerformed:
            rs.service.events.send(rs.c.EventTypes.MODULE_DROP_ACTION_POST,
                                   module=module,
                                   action=dropAction,
                                   position=viewportPosition)

        return dropActionPerformed

rs.cmd.bless(CmdAddModule, 'rs.module.add')