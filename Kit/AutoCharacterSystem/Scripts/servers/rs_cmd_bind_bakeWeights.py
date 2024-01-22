

import lx
import lxu
import modo
import modox

import rs


class CmdBakeNormalizedWeights(rs.RigCommand):
    """ Wrapper for default bake weights command for a normalizing folder.
    """

    def restoreItemSelection(self):
        return True

    def execute(self, msg, flags):
        for rig in self.rigsToEdit:
            deformStack = rs.DeformStack(rig.rootItem)
            try:
                normFolderItem = deformStack.normalizingFolder
            except LookupError:
                continue
            modox.NormalizingFolder(normFolderItem.modoItem).bakeWeights()

rs.cmd.bless(CmdBakeNormalizedWeights, 'rs.bind.bakeNormalizedWeights')