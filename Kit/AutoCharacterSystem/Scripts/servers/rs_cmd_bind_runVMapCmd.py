
import lx
import lxu
import modo
import modox

import rs


class CmdRunVertexMapCommand(rs.RigCommand):
    """ This command can be used to run native MODO's command on ACS rig.

    The purpose of this command is to set up scene context properly so
    MODO's native vertex map command can be run.
    This means that if bind skeleton joint is selected - vmaps corresponding to the joint
    have to be selected directly.
    """

    ARG_COMMAND = 'cmd'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argCmd = rs.cmd.Argument(self.ARG_COMMAND, 'string')

        return [argCmd] + superArgs

    def restoreItemSelection(self):
        return True

    def execute(self, msg, flags):
        bindLocators = self._getBindLocators()

        vmapSelection = modox.VertexMapSelection()
        vmapSelection.store(weight=True, morph=False, uv=False)

        # If bind locators are selected we process weight maps
        # that belong to them.
        if bindLocators:
            # We have to fire command on each map separately
            # since all or most of these commands do not support multiselection properly.
            for bindloc in bindLocators:
                mapName = bindloc.weightMapName
                if mapName is None:
                    continue
                rs.run('!select.vertexMap {%s} wght replace' % mapName)
                rs.run(self.getArgumentValue(self.ARG_COMMAND))
        else:
            vmaps = vmapSelection.get(lx.symbol.i_VMAP_WEIGHT)
            for mapName in vmaps:
                rs.run('!select.vertexMap {%s} wght replace' % mapName)
                rs.run('!' + self.getArgumentValue(self.ARG_COMMAND))

        vmapSelection.restoreByCommand()

    # -------- Private methods

    def _getBindLocators(self):
        """
        Gets all bind locators from selected items.

        Returns
        -------
        list(BindLocatorItem)
        """
        blocItems = []
        bindLocs = modox.ItemSelection().getRaw()
        for rawItem in bindLocs:
            try:
                blocItems.append(rs.BindLocatorItem(rawItem))
            except TypeError:
                continue
        return blocItems

rs.cmd.bless(CmdRunVertexMapCommand, 'rs.bind.runVMapCmd')