

import lx
import modo
import modox

import rs
from .common import PropEnableJointDeformation
from .common import PropEnableControllerAndTransformSet


class PropEnableDeformation(PropEnableJointDeformation):

    descAimAtJointType = True
    descTipJointGuideKey = 'tiprefgd'

    def onDisabled(self):
        # Change bind locator shape to box.
        ctrl = self.module.getKeyItem(rs.c.KeyItem.BIND_LOCATOR)

        rs.run('!item.channel locator$link none item:{%s}' % ctrl.modoItem.id)
        rs.run('!item.channel locator$isShape box item:{%s}' % ctrl.modoItem.id)

    def onEnabled(self, piece):
        ctrl = self.module.getKeyItem(rs.c.KeyItem.BIND_LOCATOR)

        rs.run('!item.channel locator$isShape circle item:{%s}' % ctrl.modoItem.id)
        rs.run('!item.channel locator$isRadius 0.0 item:{%s}' % ctrl.modoItem.id)

        rs.run('!item.channel locator$link custom item:{%s}' % ctrl.modoItem.id)


class PropEnableExtraController(PropEnableControllerAndTransformSet):

    descIdentifier = 'pextra'
    descUsername = 'musEnableExtra'
    descRefreshContext = True
    controllerIdent = 'extractrl'
    channelSet = [modox.c.TransformChannels.RotationZ,
                  modox.c.TransformChannels.ScaleX,
                  modox.c.TransformChannels.ScaleY]
    descTooltipMsgTableKey = 'jntMusEnableExtra'


class PropEnableHeadController(PropEnableControllerAndTransformSet):

    descIdentifier = 'phead'
    descUsername = 'musEnableHead'
    descRefreshContext = True
    controllerIdent = 'headctrl'
    channelSet = modox.c.TransformChannels.PositionAll
    descTooltipMsgTableKey = 'jntMusEnableHead'


class PropEnableTailController(PropEnableControllerAndTransformSet):

    descIdentifier = 'ptail'
    descUsername = 'musEnableTail'
    descRefreshContext = True
    controllerIdent = 'tailctrl'
    channelSet = modox.c.TransformChannels.PositionAll
    descTooltipMsgTableKey = 'jntMusEnableTail'


class MuscleJointModule(rs.base_FeaturedModule):

    descIdentifier = 'std.muscleJoint'
    descUsername = 'Muscle Joint'
    descFeatures = [PropEnableDeformation,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableHeadController,
                    PropEnableTailController,
                    PropEnableExtraController]
    descVariants = []
