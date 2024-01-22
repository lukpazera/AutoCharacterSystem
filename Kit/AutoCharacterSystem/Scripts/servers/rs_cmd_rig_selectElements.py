

import lx
import modo

import rs


class CmdSelectElementSet(rs.RigCommand):
    """ Selects element set that belongs to the edit rig.
    """

    ARG_IDENTIFIER = 'ident'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        identArg = rs.cmd.Argument(self.ARG_IDENTIFIER, 'string')

        return [identArg] + superArgs

    def execute(self, msg, flags):
        elset = self.getArgumentValue(self.ARG_IDENTIFIER)
        scene = modo.Scene()
        itemsToSelect = []
        for rig in self.rigsToEdit:
            itemsToSelect.extend(rig[elset].elements)
        scene.select(itemsToSelect, add=False)

rs.cmd.bless(CmdSelectElementSet, 'rs.rig.selectElements')