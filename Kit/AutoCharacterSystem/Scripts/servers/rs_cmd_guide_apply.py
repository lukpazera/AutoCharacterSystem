
import lx
import lxu
import modo

import rs


class CmdGuideApply(rs.RigCommand):
    """ Applies guide to the edit rig.
    """

    def restoreItemSelection(self):
        return True

    def applyEditActionPre(self):
        return True
    
    def applyEditActionPost(self):
        return True

    def dropToolPre(self):
        return True

    def execute(self, msg, flags):
        guide = rs.Guide(self.firstRigToEdit)
        guide.apply()

rs.cmd.bless(CmdGuideApply, 'rs.guide.apply')