

import lx
import modo

from .items.root_item import RootItem
from .core import service
from . import const as c
from . import name_op


class MetaRig (object):
    """
    Meta rig caches all the actual rig data that needs to be available publicly.
    
    Meta rig is a setup of scene group items, each containing a set of items
    or channels that can be interacted with by code or user.
    
    Parameters
    ----------
    root : RootItem
        Root item of the rig.
        
    Raises
    ------
    TypeError
        When trying to initialise meta rig with non root item.
    """

    GRAPH_META_RIG = "rs.metaRig"

    def renderNames(self):
        """ Renders names for all meta rig items.
        """
        self._nameOp = name_op.NameOperator(self._root.namingScheme)
        self.iterateOverGroups(self._renderGroupName)

    def iterateOverGroups(self, callback):
        for group in list(self._groups.values()):
            callback(group)

    def getGroup(self, identifier):
        """ Gets meta group by its identifier.
        
        Raises
        ------
        LookupError
            If requested meta group cannot be found.
        """
        try:
            return self._groups[identifier]
        except KeyError:
            raise LookupError
        raise LookupError

    def selfDelete(self):
        self.iterateOverGroups(self._selfDeleteGroup)
            
    # -------- Private methods
    
    @property
    def _groups(self):
        if self.__groups is None:
            self._scanGroups()
        return self.__groups

    def _renderGroupName(self, group):
        tokens = {}
        tokens[c.NameToken.RIG_NAME] = self._root.name
        tokens[c.NameToken.BASE_NAME] = group.descUsername
        tokens[c.NameToken.ITEM_TYPE] = group.descIdentifier
        newName = self._nameOp.renderNameMeta(tokens)
        group.modoGroupItem.name = newName

    def _selfDeleteGroup(self, group):
        lx.eval('!item.delete group child:%d item:{%s}' % (group.descDeleteWithChildren, group.modoGroupItem.id))

    def _scanGroups(self):
        rootMetaGraph = self._root.modoItem.itemGraph(self.GRAPH_META_RIG)
        connectedGroups = rootMetaGraph.reverse()
        self.__groups = {}
        for group in connectedGroups:
            tag = lx.object.StringTag(group.internalItem)
            try:
                groupIdent = tag.Get(c.TagIDInt.META_GROUP)
            except LookupError:
                continue
            try:
                metaGroup = service.systemComponent.get(c.SystemComponentType.META_GROUP, groupIdent)
            except LookupError:
                continue
            self.__groups[groupIdent] = metaGroup(group)

    def _reset(self):
        self.__groups = None

    def __init__ (self, root):
        if not isinstance(root, RootItem):
            raise TypeError

        self._root = root
        self._reset()

    def __eq__(self, other):
        if isinstance(other, MetaRig):
            return self._root.modoItem.id == other.modoItem.id
        elif isinstance(other, str):
            return self._root.modoItem.id == other
        else:
            return False
