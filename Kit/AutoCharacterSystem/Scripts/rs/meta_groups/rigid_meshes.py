

import modo

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..items.rigid_mesh import RigidMeshItem
from ..log import log


class RigidMeshesMetaGroup(MetaGroup):
    
    descIdentifier = MetaGroupType.RIGID_MESHES
    descUsername = 'Rigid Meshes'
    descModoGroupType = '' # for standard group
    
    def onItemAdded(self, modoItem):
        try:
            rigidMesh = RigidMeshItem(modoItem)
        except TypeError:
            return

        self.modoGroupItem.addItems(modoItem)
