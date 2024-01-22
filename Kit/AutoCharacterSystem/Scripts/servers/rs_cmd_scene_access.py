

import lx
import lxu
import modo
import modox

import rs


class CmdSceneAccessLevel(rs.RigCommand):

    ARG_LEVEL = 'level'

    LEVEL_HINT = (
        (0, 'anim'),
        (1, 'edit'),
        (2, 'dev')
    )
    
    def enable(self, msg):
        return True

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argLevel = rs.cmd.Argument(self.ARG_LEVEL, 'integer')
        argLevel.flags = 'query'
        argLevel.hints = self.LEVEL_HINT

        return [argLevel] + superArgs
       
    def execute(self, msg, flags):
        
        # Getting argument with hint still gets me the underlying integer.
        # This is different to getting value of a channel with hints.
        accessLevel = self.getArgumentValue(self.ARG_LEVEL)
        scene = rs.Scene()
        scene.accessLevel = accessLevel
        
        # Hard coded for now - automatically switches to animate context
        # when access level was set to anim.
        # TODO: Needs to be done in a proper way at some point.
        if accessLevel == rs.c.AccessLevel.ANIMATE and scene.anyRigsInSceneFast():
            rs.run('rs.context %s state:1' % rs.c.Context.ANIMATE)
            
        rs.service.notify(rs.c.Notifier.ACCESS_LEVEL, rs.c.Notify.DISABLE)

    def query(self, argument):
        if argument == self.ARG_LEVEL:
            return rs.Scene.getAccessLevelFast()
        return None

rs.cmd.bless(CmdSceneAccessLevel, 'rs.scene.access')