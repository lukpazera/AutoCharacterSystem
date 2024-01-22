
import lx
import lxu
import modo
import modox

import rs


class CmdSelectControllersByModuleReferenceName(rs.RigCommand):

    ARG_REFERENCE_NAME = 'refName'
    ARG_MODE = 'mode'

    MODE_HINTS = [(0, 'set'),
                  (1, 'add'),
                  (2, 'rem')]

    SELECTION_MODE_MAP = {0: modox.SelectionMode.ADD,
                          1: modox.SelectionMode.ADD,
                          2: modox.SelectionMode.SUBSTRACT}

    MODE_SUFFIX = {0: 'Set',
                   1: 'Add',
                   2: 'Sub'}

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argRefName = rs.cmd.Argument(self.ARG_REFERENCE_NAME, 'string')
        argRefName.defaultValue = ''

        argMode = rs.cmd.Argument(self.ARG_MODE, 'integer')
        argMode.defaultValue = 0
        argMode.flags = 'optional'
        argMode.hints = self.MODE_HINTS

        return [argRefName, argMode] + superArgs

    def basic_ButtonName(self):
        return self.getArgumentValue(self.ARG_REFERENCE_NAME)

    def icon(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        refName = self.getArgumentValue(self.ARG_REFERENCE_NAME)

        if refName.startswith('Right'):
            sideToken = 'rightSide'
        elif refName.startswith('Left'):
            sideToken = 'leftSide'
        else:
            sideToken = 'center'

        modeSuffix = self.MODE_SUFFIX[mode]

        return 'rs.select.' + sideToken + modeSuffix

    def execute(self, msg, flags):
        mode = self.getArgumentValue(self.ARG_MODE)
        referenceName = self.getArgumentValue(self.ARG_REFERENCE_NAME)

        modulesToSelect = []
        for rig in rs.Scene().selectedRigs:
            modules = rig.modules.allModulesByReferenceNames
            try:
                modulesToSelect.extend(modules[referenceName])
            except KeyError:
                continue

        if len(modulesToSelect) > 0:
            itemSelection = modox.ItemSelection()
            if mode == 0:  # clear selection in set mode
                itemSelection.clear()
            for module in modulesToSelect:
                ctrlsModoItems = module.getElementsFromSet(rs.c.ElementSetType.CONTROLLERS)
                itemSelection.set(ctrlsModoItems, self.SELECTION_MODE_MAP[mode], batch=True)

rs.cmd.bless(CmdSelectControllersByModuleReferenceName, 'rs.selectCtrls.byModuleRefName')


class CmdSelectControllersByModuleReferenceNameFCL(rs.RigCommand):

    ARG_CMD_LIST = 'cmdList'
    ARG_SIDE = 'side'
    ARG_MODE = 'mode'

    SIDE_HINTS = ((0, 'center'),
                  (1, 'right'),
                  (2, 'left'))

    MODE_HINTS = [(0, 'set'),
                  (1, 'add'),
                  (2, 'rem')]

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        cmdList = rs.cmd.Argument(self.ARG_CMD_LIST, 'integer')
        cmdList.flags = 'query'
        cmdList.valuesList = self._buildFromCommandList
        cmdList.valuesListUIType = rs.cmd.ArgumentValuesListType.FORM_COMMAND_LIST

        side = rs.cmd.Argument(self.ARG_SIDE, 'integer')
        side.hints = self.SIDE_HINTS

        mode = rs.cmd.Argument(self.ARG_MODE, 'integer')
        mode.flags = 'optional'
        mode.defaultValue = 0  # Set
        mode.hints = self.MODE_HINTS

        return [cmdList, side, mode] + superArgs

    def execute(self, msg, flags):
        pass

    def query(self, argIndex):
        pass

    # -------- Private methods

    def _buildFromCommandList(self):
        """ Builds a list of features for an item.

        A feature needs to be listed and needs to past test
        on each item in selection in order to show up in properties.
        """
        mode = self.getArgumentValue(self.ARG_MODE)
        side = self.getArgumentValue(self.ARG_SIDE)

        moduleReferenceNamesToList = []
        for rig in rs.Scene().selectedRigs:
            for refName in list(rig.modules.allModulesByReferenceNames.keys()):

                # Skip ref names that are already on the list
                if refName in moduleReferenceNamesToList:
                    continue

                # Side filtering
                if side == 1:
                    if not refName.startswith('Right'):  # 1 = right side
                        continue
                elif side == 2:
                    if not refName.startswith('Left'):  # 2 = left side
                        continue
                else:
                    if refName.startswith('Right') or refName.startswith('Left'):
                        continue

                moduleReferenceNamesToList.append(refName)

        moduleReferenceNamesToList.sort()

        commandList = []
        cmd = 'rs.selectCtrls.byModuleRefName {%s} {%d}'
        for refName in moduleReferenceNamesToList:
            commandList.append(cmd % (refName, mode))
        return commandList

rs.cmd.bless(CmdSelectControllersByModuleReferenceNameFCL, 'rs.selectCtrlsFCL.byModuleRefName')


class CmdOpenCtrlSelectionPanel(rs.RigCommand):
    """ Opens UI for selecting/deselecting module controllers.
    """

    ARG_MODE = 'mode'

    MODE_HINTS = [(0, 'set'),
                  (1, 'add'),
                  (2, 'rem')]

    MODE_PREFIX = {
        0: '',
        1: 'Add',
        2: 'Sub'
    }

    ICON_MODE_TOKEN = {
        0: 'Set',
        1: 'Add',
        2: 'Sub'
    }

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argMode = rs.cmd.Argument(self.ARG_MODE, 'integer')
        argMode.flags = ['optional']
        argMode.hints = self.MODE_HINTS
        argMode.defaultValue = 0

        return [argMode] + superArgs

    def icon(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        return 'rs.select.moduleCtrls%sPanel' % self.ICON_MODE_TOKEN[mode]

    def execute(self, msg, flags):
        mode = self.getArgumentValue(self.ARG_MODE)

        layoutName = "rs_%sSelectCtrlsByModule" % self.MODE_PREFIX[mode]
        panelHeight = self._calculatePanelHeight()
        cmd = 'layout.createOrClose {rsSelCtrlsByModule} {%s} true {Select Controllers By Module} width:400 height:%d style:popoverClickOff'
        lx.eval(cmd % (layoutName, panelHeight))

    # -------- Private methods

    def _calculatePanelHeight(self):
        rowHeight = 23
        minSize = 8

        rightCount = 0
        leftCount = 0
        centerCount = 0
        for rig in rs.Scene().selectedRigs:
            for module in rig.modules.allModules:
                side = module.side
                if side == rs.c.Side.RIGHT:
                    rightCount += 1
                elif side == rs.c.Side.LEFT:
                    leftCount += 1
                else:
                    centerCount += 1

        rows = max(rightCount, leftCount, centerCount)
        return rows * rowHeight + minSize


rs.cmd.bless(CmdOpenCtrlSelectionPanel, "rs.select.openModuleCtrlsUI")


class CmdSelectModuleControllersFromItemSelection(rs.RigCommand):

    def execute(self, msg, flags):
        itemSelection = modox.ItemSelection()
        selection = itemSelection.getRaw()
        modules = rs.SelectionUtils.getModulesFromItems(selection)
        ctrlsToSelect = []

        for module in modules:
            ctrls = module.getElementsFromSet(rs.c.ElementSetType.CONTROLLERS)
            ctrlsToSelect.extend(ctrls)

        itemSelection.set(ctrlsToSelect, modox.SelectionMode.REPLACE, batch=True)

rs.cmd.bless(CmdSelectModuleControllersFromItemSelection, "rs.select.moduleCtrlsFromSelection")


class CmdSelectControllersPredefined(rs.RigCommand):

    ARG_SET = 'set'
    ARG_MODE = 'mode'

    MODE_HINTS = [(0, 'set'),
                  (1, 'add'),
                  (2, 'rem')]

    SET_HINTS = [(0, 'rhand'),
                 (1, 'lhand')]

    MODE_SUFFIX = {
        0: 'Set',
        1: 'Add',
        2: 'Sub'
    }

    SELECTION_MODE_MAP = {0: modox.SelectionMode.ADD,
                          1: modox.SelectionMode.ADD,
                          2: modox.SelectionMode.SUBSTRACT}

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argSet = rs.cmd.Argument(self.ARG_SET, 'integer')
        argSet.hints = self.SET_HINTS

        argMode = rs.cmd.Argument(self.ARG_MODE, 'integer')
        argMode.defaultValue = 0
        argMode.flags = 'optional'
        argMode.hints = self.MODE_HINTS

        return [argSet, argMode] + superArgs

    def icon(self):
        predefinedSet = self.getArgumentValue(self.ARG_SET)
        mode = self.getArgumentValue(self.ARG_MODE)
        modeSuffix = self.MODE_SUFFIX[mode]

        if predefinedSet == 0:  # right hand
            return 'rs.select.rHandCtrls' + modeSuffix
        elif predefinedSet == 1:  # left hand
            return 'rs.select.lHandCtrls' + modeSuffix

    def execute(self, msg, flags):
        predefinedSet = self.getArgumentValue(self.ARG_SET)
        mode = self.getArgumentValue(self.ARG_MODE)

        if predefinedSet == 0:  # right hand
            refName = 'Right Arm'
        elif predefinedSet == 1:  # left hand
            refName = 'Left Arm'
        else:
            return

        modulesToSelect = []
        for rig in rs.Scene().selectedRigs:
            armModule = rig.modules.getModuleByReferenceName(refName)
            if armModule is None:
                continue
            modulesToSelect.extend(armModule.submodules)

        if len(modulesToSelect) > 0:
            itemSelection = modox.ItemSelection()
            if mode == 0:  # clear selection in set mode
                itemSelection.clear()
            for module in modulesToSelect:
                ctrlsModoItems = module.getElementsFromSet(rs.c.ElementSetType.CONTROLLERS)
                itemSelection.set(ctrlsModoItems, self.SELECTION_MODE_MAP[mode], batch=True)

rs.cmd.bless(CmdSelectControllersPredefined, 'rs.selectCtrls.predefined')
