
import lx
import modo
import modox

import rs


class CmdAnimationPanel(rs.base_OnItemFeatureCommand):
    """ Shows panel with sliders based on selected controller.
    """

    descIFClassOrIdentifier = rs.Controller

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
        return superArgs

    def execute(self, msg, flags):
        ctrl = self.itemFeatureToQuery
        if ctrl is None:
            return
        
        module = rs.Module(ctrl.item.moduleRootItem)
        allCtrls = module.getElementsFromSet(rs.c.ElementSetType.CONTROLLERS)
        for modoItem in allCtrls:
            try:
                ctrl = rs.Controller(modoItem)
            except TypeError:
                continue
            try:
                chanSet = ctrl.channelSet
            except LookupError:
                continue
            chanSet.open()
            break

    def notifiers(self):
        notifiers = rs.base_OnItemFeatureCommand.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

rs.cmd.bless(CmdAnimationPanel, 'rs.anim.panel')