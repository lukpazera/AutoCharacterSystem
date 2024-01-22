

import rs


class CmdRigRebuildMeta(rs.RigCommand):
    """ Rebuilds meta rig for a current rig.
    """

    def execute(self, msg, flags):
        for rig in self.rigsToEdit:
            rig.rebuildMeta()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append((rs.c.Notifier.ACCESS_LEVEL, '+d'))
        return notifiers

rs.cmd.bless(CmdRigRebuildMeta, "rs.rig.rebuildMeta")

