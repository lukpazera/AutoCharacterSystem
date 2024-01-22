

import os.path

import lx
import lxu
import modo
import modox

import rs


class CmdRigApplyPreset(rs.Command):
    """ Apply preset from a given item.
    """

    ARG_ITEM = 'item'
    
    def arguments(self):
        itemArg = rs.command.Argument(self.ARG_ITEM, '&item')

        return [itemArg]

    def enable(self, msg):
        """
        We want this command to always be enabled so it works even when dropping
        preset to non ACS3 scene.
        """
        return True

    def applyEditActionPre(self):
        return True

    def applyEditActionPost(self):
        return True

    def setContextPre(self):
        if self._presetClass is None:
            return None
        
        return self._presetClass.descContext

    def executeStart(self):
        # We want to set item and preset class in pre execute
        # Since the setContextPre() depends on it to tell command to switch
        # to the context that is appropriate for given preset type.
        # This needs to be done before calling base class executeStart()
        # since this is where the command will attempt to switch the context.
        self._item = None
        self._presetClass = None

        itemIdent = self.getArgumentValue(self.ARG_ITEM)
        try:
            self._item = modo.Item(modox.SceneUtils.findItemFast(itemIdent))
        except LookupError:
            return

        self._presetClass = rs.preset.Preset.getPresetClassFromContentItem(self._item)
        
        rs.Command.executeStart(self)

    def execute(self, msg, flags):
        if self._item is None or self._presetClass is None:
            return

        # The preset will be applied to all selected rigs.
        # We need to make not to delete preset right away,
        # we'll do it manually after the preset is applied to all rigs.
        scene = rs.Scene()
        
        preset = None
        rigs = []
        destinationItem = self._getDestinationItem()
        presetName = self._getName()

        # Get rig from destination item first but only if preset supports that.
        if self._presetClass.descSupportsDestinationItem and destinationItem is not None:
            # get rig from item here.
            rigRoot = destinationItem.rigRootItem
            if rigRoot:
                rigs = [rs.Rig(rigRoot)]

        # DestinationRig property is checked only when the rig was not already set
        # from the destination item.
        if not rigs:
            if self._presetClass.descDestinationRig == self._presetClass.DestinationRig.EDIT:
                rigs = [scene.editRig]
            elif self._presetClass.descDestinationRig == self._presetClass.DestinationRig.SELECTED:
                rigs = scene.selectedRigs

        for rig in rigs:
            preset = self._presetClass(rig)
            preset.destinationItem = destinationItem
            preset.name = presetName
            preset.load(self._item, cleanUp=False)

        self._presetClass.cleanUp(self._item)

    def notifiers(self):
        return []

    # -------- Private methods

    def _getDestinationItem(self):
        destItemIdent = rs.service.userValue.get(rs.c.UserValue.PRESET_DEST_IDENT)
        if destItemIdent:
            try:
                rawItem = modox.SceneUtils.findItemFast(destItemIdent)
            except LookupError:
                return None

            try:
                return rs.Item.getFromOther(rawItem)
            except TypeError:
                pass

        return None

    def _getName(self):
        filename = rs.service.userValue.get(rs.c.UserValue.PRESET_FILENAME)
        file = os.path.basename(filename)
        return os.path.splitext(file)[0]

rs.cmd.bless(CmdRigApplyPreset, "rs.rig.applyPreset")