

import lx
import lxu
import modox

import rs
import rsdev


class CmdDebugStart (lxu.command.BasicCommand):

    def cmd_Flags(self):
        return lx.symbol.fCMD_UI

    def basic_Enable (self, msg):
        return True

    def basic_Execute(self, msg, flags):
        rsdev.debug.start()

lx.bless(CmdDebugStart, "rs.dev.debugStart")


class CmdDebugToFile(rs.Command):

    ARG_STATE = 'state'

    def arguments(self):
        stateArg = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        stateArg.flags = 'optional'
        stateArg.defaultValue = False
        
        return [stateArg]
        
    def enable(self, msg):
        return True

    def flags(self):
        return lx.symbol.fCMD_UI
    
    def notifiers(self):
        return []

    def execute(self, msg, flags):        
        state = self.getArgumentValue(self.ARG_STATE)
        rs.service.debug.logToFile = state

lx.bless(CmdDebugToFile, "rs.dev.debugToFile")


class CmdCountCodebaseLines (rs.Command):

    ARG_VERSION = 'version'

    def arguments(self):
        versionArg = rs.cmd.Argument(self.ARG_VERSION, 'integer')
        versionArg.flags = 'optional'
        versionArg.defaultValue = 3
        
        return [versionArg]
        
    def enable(self, msg):
        return True

    def flags(self):
        return lx.symbol.fCMD_UI
    
    def notifiers(self):
        return []

    def execute(self, msg, flags):
        pythonPaths = None
        cppPaths = None
        title = ''
        
        version = self.getArgumentValue(self.ARG_VERSION)
        if version == 3:
            pythonPaths = [rs.service.path[rs.c.Path.SCRIPTS],
                           'REPO_PATH/AutoCharacterSystem/Build/Scripts']
            cppPaths = ['REPO_PATH/AutoCharacterSystem/Extra/Src']
            title = 'Auto Character System 3'
        else:
            return
        
        rsdev.countLines.countLines(pythonPaths, cppPaths, title)

lx.bless(CmdCountCodebaseLines, "rs.dev.countCodebaseLines")


class CmdCleanPyc(lxu.command.BasicCommand):

    def cmd_Flags(self):
        return lx.symbol.fCMD_UI

    def basic_Enable (self, msg):
        return True

    def basic_Execute(self, msg, flags):
        pycPaths = [rs.service.path[rs.c.Path.SCRIPTS]]
        rsdev.clean_pyc.cleanPyc(pycPaths)

lx.bless(CmdCleanPyc, "rs.dev.cleanPyc")


class CmdPrintItemGraphLinks (lxu.command.BasicCommand):

    def cmd_Flags(self):
        return lx.symbol.fCMD_UI

    def basic_Enable (self, msg):
        return True

    def basic_Execute(self, msg, flags):
        rsdev.graph_links.printGraphLinks()

lx.bless(CmdPrintItemGraphLinks, "rs.dev.printItemGraphLinks")


class CmdPrintRSItemGraphLinks (lxu.command.BasicCommand):

    def cmd_Flags(self):
        return lx.symbol.fCMD_UI

    def basic_Enable (self, msg):
        return True

    def basic_Execute(self, msg, flags):
        rsdev.graph_links.printRSGraphLinksForSelectedItems()

lx.bless(CmdPrintRSItemGraphLinks, "rs.dev.printRSItemGraphLinks")


class CmdBuildPresetFromTemplate(rs.Command):
    ARG_TEMPLATE = 'templateName'
    ARG_TYPE = 'type'

    TYPE_HINTS = ((0, 'rig'),
                  (1, 'scene'))

    def arguments(self):
        typeArg = rs.cmd.Argument(self.ARG_TYPE, 'integer')
        typeArg.hints = self.TYPE_HINTS
        typeArg.defaultValue = 0

        templateArg = rs.cmd.Argument(self.ARG_TEMPLATE, 'string')

        return [typeArg, templateArg]

    def enable(self, msg):
        return True

    def notifiers(self):
        return []

    def execute(self, msg, flags):

        templateType = self.getArgumentValue(self.ARG_TYPE)
        templateName = self.getArgumentValue(self.ARG_TEMPLATE)

        totalMonitorTicks = 500
        monitor = modox.Monitor(totalMonitorTicks, 'Build %s Preset' % templateName)

        if templateType == 0:  # rig
            templateFile = rs.service.path.generateFullFilenamePath(rs.c.Path.TEMPLATES, templateName.lower() + '.txt')
            rsdev.build_preset.buildPresetFromTemplate(templateFile, monitor, totalMonitorTicks)
        elif templateType == 1:  # scene
            templateFile = rs.service.path.generateFullFilenamePath(rs.c.Path.SCENE_TEMPLATES, templateName.lower() + '.txt')
            rsdev.build_preset.buildSampleSceneFromTemplate(templateFile, monitor, totalMonitorTicks)

        monitor.release()

lx.bless(CmdBuildPresetFromTemplate, "rs.dev.buildPreset")