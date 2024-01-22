

import lx
import lxu
import modo
import modox

import rs


class CmdRigSavePreset(rs.Command):
    """ Saves channels preset to a file.
    """

    ARG_IDENTIFIER = 'ident'
    ARG_FILENAME = 'filename'
    ARG_CAPTURE_THUMB = 'captureThumb'

    def restoreItemSelection(self):
        return True

    def init(self):
        self._path = None

    def arguments(self):
        identifier = rs.command.Argument(self.ARG_IDENTIFIER, 'string')
        
        filename = rs.command.Argument(self.ARG_FILENAME, 'string')
        filename.flags = ['optional']
        filename.defaultValue = ''
        
        thumb = rs.command.Argument(self.ARG_CAPTURE_THUMB, 'boolean')
        thumb.flags = ['optional']
        thumb.defaultValue = False
        return [identifier, filename, thumb]

    def interact(self):
        if rs.Scene().editRig is None:
            return False

        if self.isArgumentSet(self.ARG_FILENAME):
            self._path = self.getArgumentValue(self.ARG_FILENAME)
            return True

        self._path = modo.dialogs.customFile(
            dtype='fileSave',
            title='Save Preset',
            names=('lxp',),
            unames=('ACS Rig',),
            ext=('lxp',))
        if self._path is None:
            return False
        return True

    def basic_ButtonName(self):
        presetClass = self._getPresetClass()
        if presetClass is None:
            return ''

        scene = rs.Scene()
        try:
            rig = scene.getSelectedRigByIndex(0)
        except IndexError:
            return presetClass.descDefaultButtonName

        preset = presetClass(rig)
        buttonName = preset.buttonName
        if buttonName:
            return buttonName
        return preset.descDefaultButtonName

    def icon(self):
        presetClass = self._getPresetClass()
        if presetClass is None:
            return ''

        scene = rs.Scene()
        try:
            rig = scene.getSelectedRigByIndex(0)
        except IndexError:
            return presetClass.descDefaultIcon

        preset = presetClass(rig)
        icon = preset.icon
        if icon:
            return icon
        return presetClass.descDefaultIcon

    def execute(self, msg, flags):
        identifier = self.getArgumentValue(self.ARG_IDENTIFIER)
        captureThumb = self.getArgumentValue(self.ARG_CAPTURE_THUMB)
        
        scene = rs.Scene()
        try:
            rig = scene.getSelectedRigByIndex(0)
        except IndexError:
            rs.log.out('No rig to save preset from.')
            return
            
        try:
            presetClass = rs.service.systemComponent.get(rs.c.SystemComponentType.PRESET, identifier)
        except LookupError:
            return

        preset = presetClass(rig)
        preset.save(self._path, captureThumb=captureThumb)

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_LABEL)
        return notifiers

    # -------- Private methods

    def _getPresetClass(self):
        identifier = self.getArgumentValue(self.ARG_IDENTIFIER)
        try:
            return rs.service.systemComponent.get(rs.c.SystemComponentType.PRESET, identifier)
        except LookupError:
            pass

        return None

rs.cmd.bless(CmdRigSavePreset, "rs.rig.savePreset")