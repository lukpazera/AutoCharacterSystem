

import modo

from ..meta_group import MetaGroup
from ..const import MetaGroupType
from ..items.bind_mesh import BindMeshItem
from ..log import log


class BindMeshesMetaGroup(MetaGroup):
    """ Meta group for bind meshes.
    
    This is just a basic group that holds items of a certain type.
    I could have a helper class for that kind of groups instead
    of copying/pasting the same code over and over.
    """
    
    descIdentifier = MetaGroupType.BIND_MESHES
    descUsername = 'Bind Meshes'
    descModoGroupType = '' # for standard group
    
    def onItemAdded(self, modoItem):
        try:
            mesh = BindMeshItem(modoItem)
        except TypeError:
            return

        self.modoGroupItem.addItems(modoItem)
