

import rs


class CmdRigName(rs.RigCommand):
    """ Change rig name.
    """

    ARG_NAME = 'name'
    ARG_ROOT_ITEM = 'rootItem'

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        name = rs.cmd.Argument(self.ARG_NAME, 'string')
        name.flags = 'query'
        name.defaultValue = ''
        
        return [name] + superArgs

    def execute(self, msg, flags):
        rigName = self.getArgumentValue(self.ARG_NAME)
        if not rigName:
            return

        rigsToEdit = self.rigsToEdit

        addNumberSuffix = False
        if len(rigsToEdit) > 1:
            addNumberSuffix = True
        
        i = 1
        for rig in rigsToEdit:
            if addNumberSuffix:
                rig.name = rigName + str(i)
                i += 1
            else:
                rig.name = rigName

    def query(self, argument):
        if argument == self.ARG_NAME:
            rigToQuery = self.rigToQuery
            if rigToQuery is None:
                return ''
            return rigToQuery.name

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers

rs.cmd.bless(CmdRigName, 'rs.rig.name')