

import lx
import lxu
import modo

import rs


class CmdPresetBrowse(rs.Command):
    """ Open layout with preset browser.
    """

    ARG_THUMB_IDENT = 'ident'

    def enable(self, msg):
        return True

    def arguments(self):
        presetIdent = rs.command.Argument(self.ARG_THUMB_IDENT, 'string')

        return [presetIdent]

    def execute(self, msg, flags):
        ident = self.getArgumentValue(self.ARG_THUMB_IDENT)
        if ident == "rig":
            rs.run('layout.createOrClose RSRigsBrowser rs_RigsBrowser true "Rig Presets" width:640 height:498 style:palette')
        elif ident == "module":
            rs.run('layout.createOrClose RSModulesBrowser rs_ModulesBrowser true "Module Presets" width:640 height:498 style:palette')

rs.cmd.bless(CmdPresetBrowse, "rs.preset.browse")