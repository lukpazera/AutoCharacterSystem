
import lx
import lxu
import modo
import modox

import rs


class CmdInitializeRetargeting(rs.RigCommand):

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        rig = self.rigToQuery
        if not rs.Retargeting.isRetargetingRig(rig):
            return False

        if self._getFirstLocator() is None:
            msg.set(rs.c.MessageTable.DISABLE, "retargetSelectRoot")
            return False
        
        return True

    def setupMode(self):
        return True

    def applyEditActionPost(self):
        return True

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        retargeting = rs.Retargeting(rig)

        sourceRootItem = self._getFirstLocator()
        if not sourceRootItem:
            return

        retargeting.initialize(sourceRootItem, overrideDialogs=True)
        retargeting.setLinks()

        # This is to update baking command so it gets enabled.
        rs.service.notify(rs.c.Notifier.UI_GENERAL, lx.symbol.fCMDNOTIFY_DISABLE)

        rs.Scene().contexts.refreshCurrent()

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getFirstLocator(self):
        for modoItem in modo.Scene().selected:
            if modoItem.Type() == modo.c.LOCATOR_TYPE:
                return modoItem
        return None

rs.cmd.bless(CmdInitializeRetargeting, 'rs.rig.retargetInit')


class CmdRetargetAddLinks(rs.RigCommand):

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        rig = self.rigToQuery

        if not rs.Retargeting.isRetargetingRig(rig):
            msg.set(rs.c.MessageTable.DISABLE, "retargetInitFirst")
            return False

        try:
            retargeting = rs.Retargeting(rig)
        except TypeError:
            msg.set(rs.c.MessageTable.DISABLE, "retargetInitFirst")
            return False

        enable = retargeting.sourceSkeletonRoot is not None
        if not enable:
            msg.set(rs.c.MessageTable.DISABLE, "retargetInitFirst")
        return enable

    def setupMode(self):
        return True

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        retargeting = rs.Retargeting(rig)
        retargeting.setLinks()

rs.cmd.bless(CmdRetargetAddLinks, 'rs.rig.retargetAddLinks')


class CmdRetargetClearLinks(rs.RigCommand):

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        rig = self.rigToQuery

        if not rs.Retargeting.isRetargetingRig(rig):
            msg.set(rs.c.MessageTable.DISABLE, "retargetInitFirst")
            return False

        try:
            retargeting = rs.Retargeting(rig)
        except TypeError:
            msg.set(rs.c.MessageTable.DISABLE, "retargetInitFirst")
            return False

        enable = retargeting.sourceSkeletonRoot is not None
        if not enable:
            msg.set(rs.c.MessageTable.DISABLE, "retargetInitFirst")
        return enable

    def setupMode(self):
        return True

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        retargeting = rs.Retargeting(rig)
        retargeting.clearMapping()

rs.cmd.bless(CmdRetargetClearLinks, 'rs.rig.retargetClearLinks')


class CmdBakeRetargeting(rs.RigCommand):

    ARG_ACTION_NAME = 'action'
    ARG_FIRST_FRAME = 'firstFrame'
    ARG_LAST_FRAME = 'lastFrame'

    def arguments(self):
        argAction = rs.command.Argument(self.ARG_ACTION_NAME, 'string')
        argAction.defaultValue = 'Retargeted Motion'

        argFirst = rs.command.Argument(self.ARG_FIRST_FRAME, 'integer')
        argFirst.defaultValue = self._getFirstFrame
        argLast = rs.command.Argument(self.ARG_LAST_FRAME, 'integer')
        argLast.defaultValue = self._getLastFrame

        return [argAction, argFirst, argLast] + rs.RigCommand.arguments(self)

    def setupMode(self):
        return False

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        rig = self.rigToQuery

        if not rs.Retargeting.isRetargetingRig(rig):
            msg.set(rs.c.MessageTable.DISABLE, "retargetBake")
            return False

        try:
            retargeting = rs.Retargeting(rig)
        except TypeError:
            msg.set(rs.c.MessageTable.DISABLE, "retargetBake")
            return False

        enable = retargeting.sourceSkeletonRoot is not None
        if not enable:
            msg.set(rs.c.MessageTable.DISABLE, "retargetBake")
        return enable

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        retargeting = rs.Retargeting(rig)

        firstFrame = self.getArgumentValue(self.ARG_FIRST_FRAME)
        lastFrame = self.getArgumentValue(self.ARG_LAST_FRAME)
        actionName = self.getArgumentValue(self.ARG_ACTION_NAME)
        retargeting.bake(firstFrame, lastFrame, actionName)

    # -------- Private methods

    def _getFirstLastFrames(self):
        setup = modox.SetupMode()

        # If we are in setup mode we need to scan scene action.
        # This is assuming imported action is not on scene level.
        #
        if setup.state:
            action = lx.symbol.s_ACTIONLAYER_ANIM
        else:
            action = lx.symbol.s_ACTIONLAYER_EDIT

        rig = self.rigToQuery

        defaultFirst, defaultLast = modox.TimeUtils.getSceneFrameRange(modox.TimeUtils.FrameRange.CURRENT)

        try:
            retargeting = rs.Retargeting(rig)
        except TypeError:
            return defaultFirst, defaultLast

        sourceRoot = retargeting.sourceSkeletonRoot

        if sourceRoot is None:  # no source skeleton is plugged.
            return defaultFirst, defaultLast

        channelsToScan = modox.LocatorUtils.getItemPositionChannels(sourceRoot)
        channelsToScan.extend(modox.LocatorUtils.getItemRotationChannels(sourceRoot))

        try:
            return modox.TimeUtils.getChannelsFrameRange(channelsToScan, action=action)
        except ValueError:
            return defaultFirst, defaultLast

    def _getFirstFrame(self):
        f, l = self._getFirstLastFrames()
        return f

    def _getLastFrame(self):
        f, l = self._getFirstLastFrames()
        return l

rs.cmd.bless(CmdBakeRetargeting, 'rs.rig.retargetBake')


class CmdReduceRetargetedKeys(rs.RigCommand):

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        rig = self.rigToQuery
        if not rs.Retargeting.isRetargetingRig(rig):
            return False

        try:
            retargeting = rs.Retargeting(rig)
        except TypeError:
            msg.set(rs.c.MessageTable.DISABLE, "retargetReduce")
            return False

        enable = retargeting.retargetSkeletonRoot is not None

        if not enable:
            msg.set(rs.c.MessageTable.DISABLE, "retargetReduce")
        return enable

    def setupMode(self):
        return False

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        retargeting = rs.Retargeting(rig)
        retargeting.reduceKeys()

rs.cmd.bless(CmdReduceRetargetedKeys, 'rs.rig.retargetReduceKeys')


class CmdRetargetCleanUp(rs.RigCommand):

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        rig = self.rigToQuery
        if not rs.Retargeting.isRetargetingRig(rig):
            return False

        try:
            retargeting = rs.Retargeting(rig)
        except TypeError:
            msg.set(rs.c.MessageTable.DISABLE, "retargetReduce")
            return False

        enable = retargeting.retargetSkeletonRoot is not None

        if not enable:
            msg.set(rs.c.MessageTable.DISABLE, "retargetReduce")
        return enable

    def setupMode(self):
        return True

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        retargeting = rs.Retargeting(rig)
        retargeting.cleanUp()

rs.cmd.bless(CmdRetargetCleanUp, 'rs.rig.retargetCleanUp')


class CmdToggleRetargetSkeleton(rs.RigCommand):

    ARG_STATE = 'state'

    def arguments(self):
        argState = rs.command.Argument(self.ARG_STATE, 'boolean')
        argState.flags = 'query'
        argState.defaultValue = True

        return [argState] + rs.RigCommand.arguments(self)

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        rig = self.rigToQuery
        if not rig:
            return False
        if not rs.Retargeting.isRetargetingRig(rig):
            return False
        return True

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        retargeting = rs.Retargeting(rig)
        vis = self.getArgumentValue(self.ARG_STATE)
        retargeting.skeletonVisibility = vis

        rs.Scene().contexts.refreshCurrent()

    def query(self, argument):
        if argument == self.ARG_STATE:
            rigToQuery = self.rigToQuery
            retargeting = rs.Retargeting(rigToQuery)
            return retargeting.skeletonVisibility

rs.cmd.bless(CmdToggleRetargetSkeleton, 'rs.rig.retargetSkeletonToggle')


class CmdLockRetargetSkeleton(rs.RigCommand):

    ARG_STATE = 'state'

    def arguments(self):
        argState = rs.command.Argument(self.ARG_STATE, 'boolean')
        argState.flags = 'query'
        argState.defaultValue = True

        return [argState] + rs.RigCommand.arguments(self)

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        rig = self.rigToQuery
        if not rig:
            return False
        if not rs.Retargeting.isRetargetingRig(rig):
            return False
        return True

    def execute(self, msg, flags):
        rig = self.firstRigToEdit
        retargeting = rs.Retargeting(rig)
        locked = self.getArgumentValue(self.ARG_STATE)
        retargeting.skeletonLocked = locked

    def query(self, argument):
        if argument == self.ARG_STATE:
            rigToQuery = self.rigToQuery
            retargeting = rs.Retargeting(rigToQuery)
            return retargeting.skeletonLocked

rs.cmd.bless(CmdLockRetargetSkeleton, 'rs.rig.retargetSkeletonLock')


class CmdRetargetMapSetFile(rs.RigCommand):

    def interact(self):
        rig = self.rigToQuery
        if rig is None:
            return False

        currentPath = rs.service.userValue.get('rs.retargetMapFile')
        self._path = modo.dialogs.customFile('fileOpen', 'Choose Retarget Mapping File ', ('map',), ('Mapping File',), ('*.lxam',), path=currentPath)
        if self._path is None:
            return False

        return True

    def execute(self, msg, flags):
        rs.service.userValue.set('rs.retargetMapFile', self._path)

rs.cmd.bless(CmdRetargetMapSetFile, "rs.rig.retargetMapFile")
