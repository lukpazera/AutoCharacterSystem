

import rs


class CmdRigSelfValidate(rs.RigCommand):

    def execute(self, msg, flags):
        for rig in self.rigsToEdit:
            rig.selfValidate()

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append((rs.c.Notifier.ACCESS_LEVEL, '+d'))
        return notifiers

rs.command.bless(CmdRigSelfValidate, 'rs.rig.selfValidate')