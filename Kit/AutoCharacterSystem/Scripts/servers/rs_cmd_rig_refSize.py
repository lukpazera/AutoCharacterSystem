
import rs


class CmdRigReferenceSize(rs.RigCommand):
    """ Change rig reference size.

    This is changing value only, it is NOT applying new size to the rig.
    """

    ARG_SIZE = 'size'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        argSize = rs.cmd.Argument(self.ARG_SIZE, 'distance')
        argSize.flags = 'query'

        return [argSize] + superArgs

    def execute(self, msg, flags):
        rigSize = self.getArgumentValue(self.ARG_SIZE)
        if not rigSize:
            return

        rigsToEdit = self.rigsToEdit

        for rig in rigsToEdit:
            rs.RigSizeOperator(rig).referenceSize = rigSize

    def query(self, argument):
        if argument == self.ARG_SIZE:
            rigToQuery = self.rigToQuery
            if rigToQuery is None:
                return 0.0
            return rs.RigSizeOperator(rigToQuery).referenceSize

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        # React to changes to current Rig graph as well
        notifiers.append(('graphs.event', '%s +t' % rs.c.RigGraph.EDIT_RIG))
        return notifiers

rs.cmd.bless(CmdRigReferenceSize, 'rs.rig.refSize')