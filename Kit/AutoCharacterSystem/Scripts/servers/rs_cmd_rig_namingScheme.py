

import lx
import lxu
import modo

import rs


class CmdRigNamingScheme(rs.RigCommand):
    """ Sets or queries naming scheme for a rig.
    """

    ARG_LIST = "list"

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)
        
        listArg = rs.cmd.Argument(self.ARG_LIST, "integer")
        listArg.flags = "query"
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        return [listArg] + superArgs

    def query(self, argument):
        if argument == self.ARG_LIST:
            rigToQuery = self.rigToQuery
            if rigToQuery is None:
                return 0

            queryRigNameScheme = rigToQuery.namingScheme

            index = -1
            sortedNamingSchemes = self._buildSortedNamingSchemesList()
            for n, nameScheme in enumerate(sortedNamingSchemes):
                if nameScheme.descIdentifier == queryRigNameScheme.descIdentifier:
                    index = n
                    break

            if index < 0:
                rs.log.out("Bad naming scheme reference.", messageType=rs.log.MSG_ERROR)
                return 0

            return index

    def execute(self, msg, flags):
        nameSchemeIndex = self.getArgumentValue(self.ARG_LIST)
        nameSchemesList = self._buildSortedNamingSchemesList()

        newNameScheme = nameSchemesList[nameSchemeIndex]
        if not newNameScheme:
            return

        rigs = self.rigsToEdit
        for rig in rigs:
            rig.namingScheme = newNameScheme
    
    def notifiers(self):
        notifiers = rs.Command.notifiers(self)

        # For the popup to refresh command needs to react to
        # datatype change when new rig root item is added or removed
        notifiers.append(('item.event', 'add[%s] +t' % rs.c.RigItemType.ROOT_ITEM))
        notifiers.append(('item.event', 'remove[%s] +t' % rs.c.RigItemType.ROOT_ITEM))
        
        # React to changes to current Rig graph as well
        # this changes current selection.
        notifiers.append(('graphs.event', '%s +t' % rs.c.RigGraph.EDIT_RIG))

        return notifiers

    def _buildSortedNamingSchemesList(self):
        try:
            nameSchemes = rs.service.systemComponent.getOfType(rs.NamingScheme.sysType())
        except LookupError:
            nameSchemes = []
        sortedList = []
        helperDict = {}
        for scheme in nameSchemes:
            sortedList.append(scheme.descUsername)
            helperDict[scheme.descUsername] = scheme
        outputList = []
        for username in sortedList:
            outputList.append(helperDict[username])
        return outputList

    def _buildPopup(self):
        entries = []
        nameSchemes = self._buildSortedNamingSchemesList()
        for scheme in nameSchemes:
            entries.append((scheme.descIdentifier, scheme.descUsername))
        return entries

rs.cmd.bless(CmdRigNamingScheme, 'rs.rig.namingScheme')