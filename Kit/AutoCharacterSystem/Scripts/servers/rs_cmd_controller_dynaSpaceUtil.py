
import lx
import lxu
import modo
import modox

import rs
from rs import controller_dyna_space_op


class CmdSelectDynamicParentControllers(rs.RigCommand):

    ARG_MODE = 'mode'

    MODE_HINTS = [(0, 'set'),
                  (1, 'add'),
                  (2, 'rem')]

    SELECTION_MODE_MAP = {0: modox.SelectionMode.ADD,
                          1: modox.SelectionMode.ADD,
                          2: modox.SelectionMode.SUBSTRACT}

    MODE_TOKEN = {0: '',
                  1: 'Add',
                  2: 'Sub'}

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argMode = rs.cmd.Argument(self.ARG_MODE, 'integer')
        argMode.defaultValue = 0
        argMode.flags = 'optional'
        argMode.hints = self.MODE_HINTS

        return [argMode] + superArgs

    def icon(self):
        mode = self.getArgumentValue(self.ARG_MODE)
        return 'rs.controller.select' + self.MODE_TOKEN[mode] + 'DynaParent'

    def enable(self, msg):
        """
        Enable the button if first selected controller has dynamic space.
        """
        if not rs.RigCommand.enable(self, msg):
            return False

        if self.getArgumentValue(self.ARG_MODE) == 2:
            # Remove selection, different check
            return len(self._getDynaParentModifiers(first=True)) > 0
        else:
            try:
                ctrl = self._getControllers(first=True)[0]
            except IndexError:
                return False
            return True

    def execute(self, msg, flags):
        mode = self.getArgumentValue(self.ARG_MODE)

        if mode == 2:  # Remove selection, different code path for that needed
            # Substract mode simply deselects all the modifiers.
            dynaParents = self._getDynaParentModifiers(first=False)
            modox.ItemSelection().set(dynaParents, modox.SelectionMode.SUBSTRACT, batch=True)
        else:
            ctrls = self._getControllers(first=False)
            dynactrls = []

            for ctrl in ctrls:
                dynaSpace = ctrl.dynamicSpace
                if dynaSpace is None:
                    continue
                modifier = dynaSpace.dynamicParentModifier
                if modifier is not None:
                    dynactrls.append(modifier)

            if not dynactrls:
                return

            itemSelection = modox.ItemSelection()
            if mode == 0:  # clear selection in set mode
                itemSelection.clear()
            itemSelection.set(dynactrls, self.SELECTION_MODE_MAP[mode], batch=True)

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getControllers(self, first=False):
        """ Gets controllers with dynamic space.

        Parameters
        ----------
        first : bool
            When true only first found controller will be returned

        Returns
        -------
        list of Controllers or empty list
        """
        controllers = []
        for item in modox.ItemSelection().getRaw():
            try:
                ctrl = rs.Controller(item)
            except TypeError:
                continue

            if ctrl.animationSpace != rs.Controller.AnimationSpace.DYNAMIC:
                continue

            if first:
                return [ctrl]

            controllers.append(ctrl)
        return controllers

    def _getDynaParentModifiers(self, first=False):
        """
        Returns
        -------
        lxu.object.Item
        """
        dynaParents = []
        for item in modox.ItemSelection().getRaw():
            xitem = modox.Item(item)
            if xitem.typeRaw != modox.c.ItemType.MODIFIER_DYNA_PARENT:
                continue
            dynaParents.append(item)

            if first:
                break

        return dynaParents

rs.cmd.bless(CmdSelectDynamicParentControllers, 'rs.controller.selectDynaParent')


class CmdControllerSetDynamicParent(rs.RigCommand):

    ARG_INDEX = 'popupIndex'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        index = rs.cmd.Argument(self.ARG_INDEX, 'integer')
        index.flags = 'query'
        index.valuesList = self._buildPopup
        index.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        return [index] + superArgs

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        ctrl = self._getController()
        result = ctrl is not None
        if not result:
            msg.set(rs.c.MessageTable.DISABLE, "dynaParentSet")
        return result

    def execute(self, msg, flags):
        index = self.getArgumentValue(self.ARG_INDEX)
        rs.run('constraintParent.set index:%d comp:1' % index)

    def query(self, argument):
        if argument == self.ARG_INDEX:
            ctrl = self._getController()
            if ctrl is None:
                return 0

            dynaModifier = modox.DynamicParentModifier(ctrl.dynamicSpace.dynamicParentModifier)
            return dynaModifier.getParentIndex()

        return 0

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DATATYPE)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_VALUE)
        notifiers.append(modox.c.Notifier.SELECT_TIME_VALUE)
        notifiers.append(modox.c.Notifier.GRAPH_CHAN_LINKS_DATATYPE)
        notifiers.append(modox.c.Notifier.GRAPH_CHAN_LINKS_VALUE)
        return notifiers

    # -------- Private methods

    def _getController(self):
        """ Gets controller with animated dynamic space to set parent for.

        Returns
        -------
        Controller
        """
        for item in modox.ItemSelection().getRaw():
            try:
                ctrl = rs.Controller(item)
            except TypeError:
                continue

            dynaSpaceOp = controller_dyna_space_op.ControllerDynamicSpaceOperator(ctrl)
            if not dynaSpaceOp.hasDynamicSpace or not dynaSpaceOp.animatedDynamicSpace:
                continue

            return dynaSpaceOp.controllerFeature
        return None

    def _buildPopup(self):
        """ Builds a popup that the command will present in UI.
        """
        ctrl = self._getController()
        if ctrl is None:
           return []

        entries = [('world', 'World')]

        dynaModifier = modox.DynamicParentModifier(ctrl.dynamicSpace.dynamicParentModifier)
        parents = dynaModifier.parents

        if parents:
            entries.append(('default', 'Default'))
            for x in range(1, len(parents)):
                entries.append((parents[x].id, parents[x].name))

        return entries

rs.cmd.bless(CmdControllerSetDynamicParent, 'rs.ctrl.setDynaParent')


class CmdControllerAddParent(rs.RigCommand):

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        ctrl, parent = self._getControllerAndParent()
        result = ctrl is not None and parent is not None
        if not result:
            msg.set(rs.c.MessageTable.DISABLE, "dynaParentAdd")
        return result

    def basic_ButtonName(self):
        ctrl, parent = self._getControllerAndParent()
        labelMain = modox.Message.getMessageTextFromTable(rs.c.MessageTable.BUTTON, 'ctrlAddParent')

        if ctrl is not None and parent is not None:
            return labelMain + ': ' + parent.name
        noneMsg = modox.Message.getMessageTextFromTable(rs.c.MessageTable.GENERIC, 'none')
        return labelMain + ': ' + noneMsg

    def execute(self, msg, flags):
        ctrl, parent = self._getControllerAndParent()
        modox.ItemSelection().set([ctrl.modoItem, parent], modox.SelectionMode.REPLACE)
        rs.run('constraintParent comp:1')
        modox.ItemSelection().set(ctrl.modoItem, modox.SelectionMode.REPLACE)

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_LABEL)
        return notifiers

    # -------- Private methods

    def _getControllerAndParent(self):
        """ Gets controller with animated dynamic space to set parent for
        and parent item to which the controller should be parented.

        Returns
        -------
        Controller, modo.Item
            Target item can be anything, does not have to be rig item.
        """
        controllerToReturn = None
        parentModoItem = None
        parentIndexStart = 0
        selection = modox.ItemSelection().getRaw()
        for x in range(len(selection)):
            try:
                ctrl = rs.Controller(selection[x])
            except TypeError:
                continue

            dynaSpace = ctrl.dynamicSpace
            if dynaSpace is None:
                continue

            if not ctrl.dynamicSpace.isAnimated:
                continue

            controllerToReturn = ctrl
            parentIndexStart = x + 1
            break

        if 0 < parentIndexStart < len(selection):
            parentModoItem = modo.Item(selection[parentIndexStart])

        return controllerToReturn, parentModoItem

rs.cmd.bless(CmdControllerAddParent, 'rs.ctrl.addParent')


class CmdControllerRemoveParent(rs.RigCommand):
    """
    Removes an existing parent from dynamic space controller.
    """

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False
        ctrl = self._getController()
        if ctrl is None:
            msg.set(rs.c.MessageTable.DISABLE, "dynaParentDel")
            return False

        dynaParent = modox.DynamicParentModifier(ctrl.dynamicSpace.dynamicParentModifier)
        if dynaParent.getParentIndex() < 2:
            msg.set(rs.c.MessageTable.DISABLE, "dynaParentDelDefault")
            return False

        return True

    def execute(self, msg, flags):
        ctrl = self._getController()
        dynaParent = modox.DynamicParentModifier(ctrl.dynamicSpace.dynamicParentModifier)

        currentParentIndex = dynaParent.getParentIndex()
        if currentParentIndex < 2:  # Never remove parents at index 0 and 1 as these are world and default spaces.
            rs.log.out('Cannot remove world or default parent!')
            return

        try:
            dynaParent.removeCurrentParent()
        except LookupError:
            pass

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        notifiers.append(modox.c.Notifier.SELECT_TIME_DISABLE)
        return notifiers

    # -------- Private methods

    def _getController(self):
        """ Gets controller with animated dynamic space to remove parent from.

        Returns
        -------
        Controller
        """
        for item in modox.ItemSelection().getRaw():
            try:
                ctrl = rs.Controller(item)
            except TypeError:
                continue

            dynaSpaceOp = controller_dyna_space_op.ControllerDynamicSpaceOperator(ctrl)
            if not dynaSpaceOp.hasDynamicSpace or not dynaSpaceOp.animatedDynamicSpace:
                continue

            return dynaSpaceOp.controllerFeature
        return None

rs.cmd.bless(CmdControllerRemoveParent, 'rs.ctrl.removeParent')