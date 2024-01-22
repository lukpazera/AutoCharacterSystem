

import lx
import lxu
import modo
import modox

import rs


class CmdTestBindSkeleton(rs.RigCommand):
    """ Builds bind skeleton shadow, allow for testing bind skeleton structure.
    """

    ARG_TYPE = 'type'

    TYPE_HINTS = ((0, 'bind'),
                  (1, 'bake'))

    SHADOW_DESCRIPTION = {0: rs.bind_skel_shadow.BindShadowDescription,
                          1: rs.bind_skel_shadow.BakeShadowDescription}

    def arguments(self):
        argType = rs.command.Argument(self.ARG_TYPE, 'integer')
        argType.hints = self.TYPE_HINTS
        argType.defaultValue = 0

        return [argType] + rs.RigCommand.arguments(self)
    
    def setupMode(self):
        return True

    def execute(self, msg, flags):
        shadowType = self.getArgumentValue(self.ARG_TYPE)
        shadowDescClass = self.SHADOW_DESCRIPTION[shadowType]

        shadowDesc = shadowDescClass()
        shadowDesc.visible = True

        for rig in self.rigsToEdit:
            shadow = rs.BindSkeletonShadow(rig)
            shadow.build(shadowDesc)

rs.cmd.bless(CmdTestBindSkeleton, 'rs.rig.testBindSkeleton')