

import lx
import lxu
import modo
import modox

import rs


class CmdGuideAttachToOther(rs.RigCommand):
    """ Allows for linking root guide of one module to a guide from another module.
    """

    ARG_GUIDE_FROM = 'guideFrom'
    ARG_GUIDE_TO = 'guideTo'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        rootFromArg = rs.cmd.Argument(self.ARG_GUIDE_FROM, '&item')
        rootFromArg.flags = 'optional'
        rootFromArg.defaultValue = None

        guideToArg = rs.cmd.Argument(self.ARG_GUIDE_TO, '&item')
        guideToArg.flags = 'optional'
        guideToArg.defaultValue = None

        return [rootFromArg, guideToArg] + superArgs

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        g1, g2 = self._getGuideControllers()
        result = g1 is not None and g2 is not None

        if not result:
            msg.set(rs.c.MessageTable.DISABLE, "guideAttach")
        return result

    def execute(self, msg, flags):
        guideControllersFrom, guideControlerTo = self._getGuideControllers()
        if not guideControllersFrom or guideControlerTo is None:
            return

        guide = rs.Guide(guideControlerTo.item.rigRootItem)
        for guideCtrlFrom in guideControllersFrom:
            guide.attachGuideToOther(guideCtrlFrom.item, guideControlerTo.item)

        rs.Scene().contexts.refreshCurrent()

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getGuideControllers(self):
        guideControllersFrom = []
        guideControllerTo = None

        # Get guides from arguments if they are set
        if self.isArgumentSet(self.ARG_GUIDE_FROM):
            try:
                guideControllersFrom = [rs.ControllerGuide(modox.SceneUtils.findItemFast(self.getArgumentValue(self.ARG_GUIDE_FROM)))]
            except TypeError:
                pass
        if self.isArgumentSet(self.ARG_GUIDE_TO):
            try:
                guideControllerTo = rs.ControllerGuide(modox.SceneUtils.findItemFast(self.getArgumentValue(self.ARG_GUIDE_TO)))
            except TypeError:
                pass

        # Get guides from selection.
        # We consider last selected guide a target, all previous ones - source.
        if not guideControllersFrom or guideControllerTo is None:
            itemSelection = modox.ItemSelection()
            count = itemSelection.size

            if count < 2:
                return [], None

            try:
                guideControllerTo = rs.ControllerGuide(itemSelection.getLastRaw())
            except TypeError:
                return [], None

            guideToRigRoot = guideControllerTo.item.rigRootItem

            # Get guide from
            for x in range(count - 1):
                rawItem = itemSelection.getRawByIndex(x)

                try:
                    guideCtrl = rs.ControllerGuide(rawItem)
                except TypeError:
                    continue

                if guideCtrl.item.rigRootItem != guideToRigRoot:
                    continue

                guideControllersFrom.append(guideCtrl)

        if not guideControllersFrom or guideControllerTo is None:
            return [], None

        return guideControllersFrom, guideControllerTo

rs.cmd.bless(CmdGuideAttachToOther, 'rs.guide.attachToOther')


class CmdGuideDetachAllAttached(rs.RigCommand):

    ARG_GUIDE = 'guide'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        rootArg = rs.cmd.Argument(self.ARG_GUIDE, '&item')
        rootArg.flags = 'optional'
        rootArg.defaultValue = None

        return [rootArg] + superArgs

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        result = len(self._getItems()) > 0

        if not result:
            msg.set(rs.c.MessageTable.DISABLE, "guideDetach")
        return result

    def execute(self, msg, flags):
        guidesWitchAttachments = self._getItems()
        for guide in guidesWitchAttachments:
            guide.detachAllAttachedGuides()

        rs.Scene().contexts.refreshCurrent()

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getItems(self):
        itemSelection = modox.ItemSelection()
        count = itemSelection.size

        guides = []
        for x in range(count):
            rawItem = itemSelection.getRawByIndex(x)

            try:
                guide = rs.GuideItem(rawItem)
            except TypeError:
                continue

            if not guide.hasOtherGuidesAttached:
                continue

            guides.append(guide)

        return guides

rs.cmd.bless(CmdGuideDetachAllAttached, 'rs.guide.detachAll')
