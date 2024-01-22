

import os

import lx
import modo
import modox

import rs


class CmdOpenAnimatePalette(modox.Command):
    """ Open animation palette.
    """
    
    def flags(self):
        return lx.symbol.fCMD_UI

    def enable(self, msg):
        return True

    def execute(self, msg, flags):
        rs.run('layout.createOrClose cookie:ACS3AnimatePalette layout:{rsAnimatePaletteLayout} title:{Animate} width:1600 height:46 persistent:1 style:palette')

rs.cmd.bless(CmdOpenAnimatePalette, 'rs.animPalette.open')


class CmdOpenSetupPalette(modox.Command):
    """ Open setup palette.
    """

    def flags(self):
        return lx.symbol.fCMD_UI

    def enable(self, msg):
        return True

    def execute(self, msg, flags):
        rs.run('layout.createOrClose cookie:ACS3SetupPalette layout:{rsSetupPaletteLayout} title:{Rig} width:256 height:832 persistent:1 style:palette')

rs.cmd.bless(CmdOpenSetupPalette, 'rs.setupPalette.open')


class CmdCustomTimelineLayout(rs.Command):

    ARG_STATE = 'state'

    _FILE_LAYOUT_TIMELINE = 'ovr_layout_timeline.CFG'
    _FILE_DISABLED_EXT = '.disabled'
    
    def arguments(self):
        argState = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        argState.flags = 'query'
        argState.defaultValue = False
        return [argState]

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)
            
    def enable(self, msg):
        return True

    def execute(self, msg, flags):
        state = self.getArgumentValue(self.ARG_STATE)
        configsPath = rs.service.path[rs.c.Path.CONFIGS]
        if state:
            if not self._isTimelineLayoutOn():
                src = os.path.join(configsPath, self._FILE_LAYOUT_TIMELINE + self._FILE_DISABLED_EXT)
                dst = os.path.join(configsPath, self._FILE_LAYOUT_TIMELINE)
                os.rename(src, dst)
        else:
            if self._isTimelineLayoutOn():
                dst = os.path.join(configsPath, self._FILE_LAYOUT_TIMELINE + self._FILE_DISABLED_EXT)
                src = os.path.join(configsPath, self._FILE_LAYOUT_TIMELINE)
                os.rename(src, dst)
        
        result = modo.dialogs.okCancel('Rigging System Custom Timeline Layout', 'You have to reset preferences and restart MODO for changes to have an effect.\nDo you want to do it now?')
        if result == 'ok':
            rs.run('config.reset')

    def query(self, argument):
        if argument == self.ARG_STATE:
            return self._isTimelineLayoutOn()
    
    # -------- Private methods
    
    def _isTimelineLayoutOn(self):
        path = rs.service.path[rs.c.Path.CONFIGS]
        return os.path.isfile(os.path.join(path, self._FILE_LAYOUT_TIMELINE))
        
rs.cmd.bless(CmdCustomTimelineLayout, 'rs.ui.customTimelineLayout')