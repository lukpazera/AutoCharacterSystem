

import os

import lx
import lxu
import modo
import modox

import rs


class CmdRigNew (rs.Command):
    """ Adds new rig to the scene.

    If no root item is passed a default, empty rig will be added.
    If root is passed then the rig will be created from the hierarchy
    under the root.
    """

    ARG_NAME = 'name'
    ARG_EMPTY = 'empty'

    def arguments(self):
        nameArg = rs.command.Argument(self.ARG_NAME, 'string')
        nameArg.flags = ['optional']
        nameArg.defaultValue = ''
        
        emptyArg = rs.command.Argument(self.ARG_EMPTY, 'boolean')
        emptyArg.flags = 'optional'
        emptyArg.defaultValue = False
        
        return [emptyArg, nameArg]

    def notifiers(self):
        """ New rig command is always enabled and doesn't need any notifiers.

        By returning empty list we clear any default notifiers.
        """
        return []

    def enable(self, msg):
        """ This command is always enabled.
        By returning True we override any default enable state behaviour.
        """
        return True

    def execute(self, msg, flags):
        rigName = self.getArgumentValue(self.ARG_NAME)
        empty = self.getArgumentValue(self.ARG_EMPTY)

        scene = rs.Scene()
        rig = scene.newRig(rigName)

        if not empty:
            baseModuleFilename = os.path.join(rs.service.path[rs.c.Path.MODULES_INTERNAL], 'Base.lxp')
            if os.path.isfile(baseModuleFilename):
                lx.eval('!preset.do {%s}' % baseModuleFilename)
                rig.rootModoItem.select(replace=True)
                modox.Item(rig.rootModoItem.internalItem).autoFocusInItemList()
            else:
                empty = True
            rs.run('rs.subcontext assembly assm 1')
        else:
            rs.run('rs.module.new')
            rs.run('rs.subcontext assembly dev 1')
        scene.refreshContext()

rs.command.bless(CmdRigNew, 'rs.rig.new')