

import lx
import lxu
import modo

import rs


class CmdPresetThumbCapture(rs.Command):
    """ Toggles UI used to capture a thumbnail for a preset.
    """

    ARG_THUMB_IDENT = 'ident'

    def arguments(self):
        thumbIdent = rs.command.Argument(self.ARG_THUMB_IDENT, 'string')

        return [thumbIdent]

    def execute(self, msg, flags):
        thumbPreset = self._getPresetThumbnail()
        if thumbPreset is not None:
            thumbPreset.openWindow()

    def basic_ButtonName (self):
        thumbPreset = self._getPresetThumbnail()
        if thumbPreset is not None:
            return thumbPreset.descButtonName
        return ''

    def _getPresetThumbnail(self):
        thumbIdent = self.getArgumentValue(self.ARG_THUMB_IDENT)
        try:
            return rs.service.systemComponent.get(rs.c.SystemComponentType.PRESET_THUMBNAIL, thumbIdent)
        except LookupError:
            rs.log.out('Invalid preset thumbnail identifier!', rs.log.MSG_ERROR)
        return None

rs.cmd.bless(CmdPresetThumbCapture, "rs.preset.captureThumb")