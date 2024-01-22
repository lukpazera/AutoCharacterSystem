

import lx
import lxu
import modo
import modox

import rs


class CmdMirrorModule(rs.base_OnModuleCommand):
    """ Mirrors module with symmetry or not.
    
    This command works with current edit module or all modules from edit rig.
    This command doesn't mirror modules that are at center.
    """

    ARG_SYMMETRY = "symmetry"
    ARG_ALL = "all"

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)
        
        argSymmetry = rs.command.Argument(self.ARG_SYMMETRY, 'boolean')
        argSymmetry.flags = 'optional'
        argSymmetry.defaultValue = False

        argAll = rs.command.Argument(self.ARG_ALL, 'boolean')
        argAll.flags = 'optional'
        argAll.defaultValue = False

        return [argSymmetry, argAll] + superArgs

    def setupMode(self):
        return True

    def applyEditActionPre(self):
        return True
    
    def applyEditActionPost(self):
        return True

    def enable(self, msg):
        """
        Command should not be enabled when center module is edit one.
        """
        if not rs.base_OnModuleCommand.enable(self, msg):
            return False

        result = True
        mirrorAll = self.getArgumentValue(self.ARG_ALL)
        if mirrorAll:
            try:
                result = self._anyModuleToMirrorInRig(rs.Rig(rs.Scene.getEditRigRootItemFast()))
            except TypeError:  # Exception will happen when there are no rigs in scene
                result = False
                
            if not result:
                msg.set(rs.c.MessageTable.DISABLE, 'mirrorAllModule')
        else:
            queryModule = self.moduleToQuery
            if not queryModule or queryModule.side == rs.c.Side.CENTER:
                result = False
                msg.set(rs.c.MessageTable.DISABLE, 'mirrorModule')
        return result

    def basic_ButtonName(self):
        sym = self.getArgumentValue(self.ARG_SYMMETRY)
        all = self.getArgumentValue(self.ARG_ALL)

        if all:
            key = 'modMirrorAll'
        else:
            key = 'modMirror'

        if sym:
            key += 'Sym'

        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, key)

    def cmd_Tooltip(self):
        sym = self.getArgumentValue(self.ARG_SYMMETRY)
        all = self.getArgumentValue(self.ARG_ALL)

        if all:
            key = 'modAutoMirror'
        else:
            key = 'modMirror'

        if sym:
            key += 'Sym'

        return modox.Message.getMessageTextFromTable(rs.c.MessageTable.CMDTOOLTIP, key)

    def execute(self, msg, flags):
        mirrorAll = self.getArgumentValue(self.ARG_ALL)
        modulesToMirror = []
        mirroredModules = []
        editRig = None

        if mirrorAll:
            # get all side modules that do not have equivalent on the other side
            editRig = rs.Scene().editRig
            modulesToMirror = self._getAllModulesToMirror(editRig)
        else:
            # grab current edit module.
            moduleToMirror = self.moduleToQuery
            if moduleToMirror is None:
                return
            try:
                editRig = rs.Rig(moduleToMirror.rigRootItem)
            except TypeError:
                return
            modulesToMirror = [moduleToMirror]

        if editRig is None or not modulesToMirror:
            return

        # Monitor
        perModuleMonitorTicks = 100
        extraTicks = 100
        totalMonitorTicks = len(modulesToMirror) * perModuleMonitorTicks + extraTicks
        monitor = modox.Monitor(totalMonitorTicks, 'Mirror Module(s)')
        moduleCount = 0

        for moduleToMirror in modulesToMirror:
            moduleCount += 1
            monitor.progress = perModuleMonitorTicks * (moduleCount - 1)

            sideFrom = moduleToMirror.side
            if sideFrom == rs.c.Side.CENTER:
                continue

            mainMirroredModule = editRig.modules.duplicateModule(moduleToMirror)
            mirroredModules.append(mainMirroredModule)

            monitor.tick(perModuleMonitorTicks * 0.4)

            sourcePlugs = moduleToMirror.plugs
            mirroredPlugs = mainMirroredModule.plugs

            # TODO: This is hard coded crap.
            # We use module side command to mirror the module after it's duplicated.
            # This command uses popup to choose side (integer value)
            # and operates on currently selected module.
            # So we need to prepare all that correctly before firing the command.
            if sideFrom == rs.c.Side.RIGHT:
                sideTo = 1 # Fixed index for the module side command, sooo bad!!!
            elif sideFrom == rs.c.Side.LEFT:
                sideTo = 2 # Same as above, shame on you!

            # Module side command works off item selection.
            # Need to select module root item.
            mainMirroredModule.rootModoItem.select(replace=True)
            lx.eval('!rs.module.side %d applyGuide:0' % (sideTo))

            monitor.tick(perModuleMonitorTicks * 0.4)

            # Auto connect plugs on the mirrored module.
            # We want plugs to either connect to the same socket if the socket
            # is on center or to equivalent socket from the other side if
            # it's in the scene.
            sourcePlugsByIdents = {}
            for plug in sourcePlugs:
                sourcePlugsByIdents[plug.getReferenceName(side=False)] = plug

            baseModule = editRig.modules.baseModule

            # Iterate through mirrored plugs and guess their sockets.
            for plug in mirroredPlugs:
                try:
                    equivalentPlug = sourcePlugsByIdents[plug.getReferenceName(side=False)]
                except KeyError:
                    # Can't find equivalent plug, disconnect.
                    plug.disconnectFromSocket()
                    continue
                socket = equivalentPlug.socket
                if socket is None:
                    continue

                # If socket is a base module socket - skip connecting as it will already
                # be connected to base by default after dropping the module to the scene
                # during module duplication command.
                if baseModule is not None:
                    socketModuleRoot = socket.moduleRootItem
                    if baseModule == socketModuleRoot:
                        continue

                plug.connectToSocket(socket)

            # Use module operator to set up symmetry.
            if self.getArgumentValue(self.ARG_SYMMETRY):
                editRig.modules.setSymmetry(mainMirroredModule, moduleToMirror)

                # Symmetry needs to support submodules.
                subModsToMirror = moduleToMirror.submodules
                mirroredSubmods = mainMirroredModule.submodules
                if subModsToMirror and mirroredSubmods and len(subModsToMirror) == len(mirroredSubmods):
                    for x in range(len(mirroredSubmods)):
                        editRig.modules.setSymmetry(mirroredSubmods[x], subModsToMirror[x])

            monitor.tick(perModuleMonitorTicks * 0.2)

        monitor.progress = len(modulesToMirror) * perModuleMonitorTicks
        monitor.tick(extraTicks * 0.5)

        # Apply Guide
        lx.eval('!rs.guide.apply')

        monitor.tick(extraTicks * 0.5)

        rsScene = rs.Scene()

        # Refresh the context.
        assmContext = rs.ContextAssembly()
        rsScene.contexts.current = assmContext
        assmContext.subcontext = rs.c.AssemblySubcontexts.ASSEMBLY

        rsScene.contexts.refreshCurrent()

        mainMirroredModule = mirroredModules[-1]
        editRig.modules.editModule = mainMirroredModule
        modo.Scene().select(mainMirroredModule.rootModoItem)
        modox.Item(mainMirroredModule.rootModoItem.internalItem).autoFocusInItemList()

        monitor.release()

    def notifiers(self):
        notifiers = rs.base_OnModuleCommand.notifiers(self)
        notifiers.extend(rs.NotifierSet.EDIT_MODULE_CHANGED)
        return notifiers

    # -------- Private methods

    def _getAllModulesToMirror(self, rig):
        sidedModules = self._getAllSidedModulesFromRig(rig)

        modulesToMirror = []
        # now find modules that have no mirror on the other side.
        for key in list(sidedModules.keys()):
            if key.startswith(rs.c.Side.RIGHT):
                oppositeKey = key.replace(rs.c.Side.RIGHT, rs.c.Side.LEFT)
            elif key.startswith(rs.c.Side.LEFT):
                oppositeKey = key.replace(rs.c.Side.LEFT, rs.c.Side.RIGHT)
            if oppositeKey not in sidedModules:
                modulesToMirror.append(sidedModules[key])

        return modulesToMirror

    def _anyModuleToMirrorInRig(self, rig):
        """
        Gets first module to mirror in a rig.

        This is first sided module that doesn't have mirror on the other side yet.
        """
        sidedModules = self._getAllSidedModulesFromRig(rig)

        modulesToMirror = []
        # now find first module that has no mirror on the other side.
        for key in list(sidedModules.keys()):
            if key.startswith(rs.c.Side.RIGHT):
                oppositeKey = key.replace(rs.c.Side.RIGHT, rs.c.Side.LEFT)
            elif key.startswith(rs.c.Side.LEFT):
                oppositeKey = key.replace(rs.c.Side.LEFT, rs.c.Side.RIGHT)
            if oppositeKey not in sidedModules:
                return True

        return False

    def _getAllSidedModulesFromRig(self, rig):
        sidedModules = {}
        for module in rig.modules.allModules:
            if module.side == rs.c.Side.CENTER:
                continue
            # We're not going to consider submodules as they will be handled by mirroring main module.
            if module.isSubmodule:
                continue
            sidedModules[module.side + module.name] = module
        return sidedModules

rs.cmd.bless(CmdMirrorModule, 'rs.module.mirror')