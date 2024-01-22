
import lx
import lxu
import modo
import modox

import rs


class CmdSelectWeightMapsDirectly(rs.RigCommand):
    """ Selects bind locators(effectors) that deform given mesh.
    """

    def enable(self, msg):
        if len(self._getBindLocators()) > 0:
            return True
        msg.set(rs.c.MessageTable.DISABLE, "selWMapDir")
        return False

    def execute(self, msg, flags):
        bindLocators = self._getBindLocators()

        rs.run('!select.vertexMap {} wght remove')

        for bindloc in bindLocators:
            mapName = bindloc.weightMapName
            if mapName is None:
                continue
            rs.run('!select.vertexMap {%s} wght add' % mapName)

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(modox.c.Notifier.SELECT_ITEM_DISABLE)
        return notifiers

    # -------- Private methods

    def _getBindLocators(self):
        blocItems = []
        bindLocs = modox.ItemSelection().getRaw()
        for rawItem in bindLocs:
            try:
                blocItems.append(rs.BindLocatorItem(rawItem))
            except TypeError:
                continue
        return blocItems

rs.cmd.bless(CmdSelectWeightMapsDirectly, 'rs.bind.selectWeightsDirect')