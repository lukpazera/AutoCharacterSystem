

import lx
import lxu
import modo
import modox

import rs


class CmdGuideLink(rs.RigCommand):
    """ Allows for linking root guide of one module to a guide from another module.
    """

    ARG_ROOT_FROM = 'rootFrom'
    ARG_GUIDE_TO = 'guideTo'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        rootFromArg = rs.cmd.Argument(self.ARG_ROOT_FROM, '&item')
        rootFromArg.flags = 'optional'
        rootFromArg.defaultValue = None

        guideToArg = rs.cmd.Argument(self.ARG_GUIDE_TO, '&item')
        guideToArg.flags = 'optional'
        guideToArg.defaultValue = None

        return [rootFromArg, guideToArg] + superArgs

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        g1, g2 = self._getItems()
        result = g1 is not None and g2 is not None

        if not result:
            msg.set(rs.c.MessageTable.DISABLE, "guideLink")
        return result

    def applyEditActionPre(self):
        return True

    def applyEditActionPost(self):
        return True

    def execute(self, msg, flags):
        guidesFrom, guideTo = self._getItems()
        if not guidesFrom or guideTo is None:
            return

        guide = rs.Guide(guideTo.rigRootItem)
        for guideFrom in guidesFrom:
            guide.linkGuideTransforms(guideFrom, guideTo)

    def notifiers(self):
        notifiers = rs.RigCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getItems(self):
        guidesFrom = []
        guideTo = None

        # Get guides from arguments if they are set
        if self.isArgumentSet(self.ARG_ROOT_FROM):
            try:
                guidesFrom = [rs.GuideItem(modox.SceneUtils.findItemFast(self.getArgumentValue(self.ARG_ROOT_FROM)))]
            except TypeError:
                pass
        if self.isArgumentSet(self.ARG_GUIDE_TO):
            try:
                guideTo = rs.GuideItem(modox.SceneUtils.findItemFast(self.getArgumentValue(self.ARG_GUIDE_TO)))
            except TypeError:
                pass

        # Get guides from selection.
        # We consider last selected guide a target, all previous ones - source.
        if not guidesFrom or guideTo is None:
            itemSelection = modox.ItemSelection()
            count = itemSelection.size

            if count < 2:
                return [], None

            try:
                guideTo = rs.GuideItem(itemSelection.getLastRaw())
            except TypeError:
                return [], None

            guideToRigRoot = guideTo.rigRootItem

            # Get guide from
            guideToStartIndex = 0
            for x in range(count - 1):
                rawItem = itemSelection.getRawByIndex(x)

                try:
                    guide = rs.GuideItem(rawItem)
                except TypeError:
                    continue

                if not guide.isRootGuide:
                    continue

                if guide.rigRootItem != guideToRigRoot:
                    continue

                guidesFrom.append(guide)

        if not guidesFrom or guideTo is None:
            return [], None

        return guidesFrom, guideTo

rs.cmd.bless(CmdGuideLink, 'rs.guide.link')


class CmdGuideUnlink(rs.RigCommand):
    """ Allows for unlinking root guide from its connection to another module guide.
    """

    ARG_ROOT = 'root'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        rootArg = rs.cmd.Argument(self.ARG_ROOT, '&item')
        rootArg.flags = 'optional'
        rootArg.defaultValue = None

        return [rootArg] + superArgs

    def applyEditActionPost(self):
        return True

    def enable(self, msg):
        if not rs.RigCommand.enable(self, msg):
            return False

        result = len(self._getItems()) > 0
        if not result:
            msg.set(rs.c.MessageTable.DISABLE, "guideUnlink")
        return result

    def execute(self, msg, flags):
        guidesFrom = self._getItems()
        for guide in guidesFrom:
            guide.transformLinkedGuide = None

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

            if guide.isRootGuide:
                guides.append(guide)

        return guides

rs.cmd.bless(CmdGuideUnlink, 'rs.guide.unlink')