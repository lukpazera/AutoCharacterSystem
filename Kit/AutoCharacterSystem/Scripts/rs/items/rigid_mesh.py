

import lx
import modo

from ..item_mesh import MeshItem
from ..item_mesh import MeshItemResolutionsEventHandler
from .. import const as c
from ..log import log


class RigidMeshItem(MeshItem):

    descType = c.RigItemType.RIGID_MESH
    descUsername = 'Rigid Mesh'
    descDefaultName = 'RigidMesh'
    descPackages = []
    descSynthName = False
    descDropScriptSource = c.DropScript.ITEM_ON_ITEM_SOURCE
    descDropScriptDestination = c.DropScript.ITEM_ON_ITEM_DESTINATION


class RigidMeshEventHandler(MeshItemResolutionsEventHandler):
    """
    Event handler for updating item mesh resolution data.
    """
    descIdentifier = 'rgdmeshmres'
    descUsername = 'Rigid Mesh Resolutions'
    descElementSet = c.ElementSetType.RIGID_MESHES