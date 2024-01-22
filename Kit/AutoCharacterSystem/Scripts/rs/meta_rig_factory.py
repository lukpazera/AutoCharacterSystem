

import modo

from . import const as c
from . import meta_rig
from . import meta_rig_template
from .core import service
from .log import log


class MetaRigFactory(object):
    """ Use this class to create and manage meta rig.
    """
    
    GRAPH_META_RIG = 'rs.metaRig'

    def new(self, rigRootItem):
        
        template = meta_rig_template.MetaRigTemplate()
        layout = template.layout

        scene = modo.Scene()
        rootMetaGraph =rigRootItem.modoItem.itemGraph(self.GRAPH_META_RIG)
        createdGroups = []

        for x in range(len(layout)):
            groupIdentifier = layout[x]
            ident = groupIdentifier.lstrip()
            hierarchyLevel = len(groupIdentifier) - len(ident)
            
            try:
                groupClass = service.systemComponent.get(c.SystemComponentType.META_GROUP, ident)
            except LookupError:
                log.out('Bad meta group ident...', log.MSG_ERROR)
                createdGroups.append(None)
                continue

            newMetaGroup = groupClass.new()
            newGroup = newMetaGroup.modoGroupItem
            createdGroups.append(newGroup)

            # Sort out parenting
            if hierarchyLevel > 0 and x > 0:
                for y in range(x-1, -1, -1):
                    hl = len(layout[y]) - len(layout[y].lstrip())
                    if hl == (hierarchyLevel - 1):
                        # This is the parent.
                        newGroup.setParent(createdGroups[y], -1)
                        break

            # Link new group to rig root.
            groupMetaGraph = modo.Item(newGroup.internalItem).itemGraph(self.GRAPH_META_RIG)
            groupMetaGraph >> rootMetaGraph
        
        return meta_rig.MetaRig(rigRootItem)