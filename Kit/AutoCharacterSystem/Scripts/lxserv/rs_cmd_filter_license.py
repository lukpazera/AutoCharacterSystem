

import lx
import lxu
import modo


class CmdLicenseFilter (lxu.command.BasicCommand):

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

    def basic_Enable (self, msg):
        try:
            typeid = lx.service.Scene().ItemTypeLookup('rs.root')
        except LookupError:
            return False
        return True

lx.bless(CmdLicenseFilter, 'rs.filter.license')