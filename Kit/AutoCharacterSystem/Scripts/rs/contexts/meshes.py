

import lx
import modo

import rs.context
from ..util import run
from ..const import ElementSetType as e
from ..const import ItemVisible as v
from ..const import TriState as t
from ..const import Context as cxt
from ..context import ContextElementStatesDesc
from .. import const as c
from ..scene import Scene


class ContextMeshes(rs.context.Context):
    
    descIdentifier = cxt.MESHES
    descUsername = 'Meshes'
    descSubcontexts = [c.MeshesSubcontexts.RESOLUTION,
                       c.MeshesSubcontexts.BIND_MESHES,
                       c.MeshesSubcontexts.BIND_PROXIES,
                       c.MeshesSubcontexts.RIGID_MESHES,
                       c.MeshesSubcontexts.RIG_CLAY]
    descDefaultSubcontext = c.MeshesSubcontexts.RESOLUTION

    setup = True
    edit = True
    isHierarchyVisible = False

    @property
    def elementsVisible(self):
        generic = ContextElementStatesDesc(
            {e.BIND_SKELETON: True,
             e.RESOLUTION_BIND_MESHES: True,
             e.RESOLUTION_RIGID_MESHES: True,
             e.RESOLUTION_BIND_PROXIES: True})

        res = ContextElementStatesDesc(
            {e.BIND_SKELETON: True,
             e.RESOLUTION_BIND_MESHES: True,
             e.RESOLUTION_RIGID_MESHES: True,
             e.RESOLUTION_BIND_PROXIES: True},
             subcontext=c.MeshesSubcontexts.RESOLUTION)    

        clay = ContextElementStatesDesc(
            {e.BIND_SKELETON: False,
             e.RESOLUTION_BIND_MESHES: True,
             e.RESOLUTION_BIND_PROXIES: True,
             e.RESOLUTION_RIGID_MESHES: True},
            subcontext=c.MeshesSubcontexts.RIG_CLAY)

        return [generic, res, clay]
    
    @property
    def elementsSelectable(self):
        subcontext = self.subcontext
        if subcontext == c.MeshesSubcontexts.BIND_MESHES:
            return {e.BIND_SKELETON: t.OFF,
                    e.RESOLUTION_BIND_MESHES: t.DEFAULT,
                    e.RESOLUTION_RIGID_MESHES: t.OFF,
                    e.RESOLUTION_BIND_PROXIES: t.OFF}
        elif subcontext == c.MeshesSubcontexts.BIND_PROXIES:
            return {e.BIND_SKELETON: t.DEFAULT,
                    e.RESOLUTION_BIND_MESHES: t.OFF,
                    e.RESOLUTION_RIGID_MESHES: t.OFF,
                    e.RESOLUTION_BIND_PROXIES: t.DEFAULT}
        elif subcontext == c.MeshesSubcontexts.RIGID_MESHES:
            return {e.BIND_SKELETON: t.DEFAULT,
                    e.RESOLUTION_BIND_MESHES: t.OFF,
                    e.RESOLUTION_RIGID_MESHES: t.DEFAULT,
                    e.RESOLUTION_BIND_PROXIES: t.OFF}
        elif subcontext == c.MeshesSubcontexts.RIG_CLAY:
            return {e.BIND_SKELETON: t.OFF,
                    e.RESOLUTION_BIND_MESHES: t.DEFAULT,
                    e.RESOLUTION_BIND_PROXIES: t.DEFAULT,
                    e.RESOLUTION_RIGID_MESHES: t.DEFAULT}
        else:
            return {e.BIND_SKELETON: t.OFF,
                    e.RESOLUTION_BIND_MESHES: t.OFF,
                    e.RESOLUTION_RIGID_MESHES: t.OFF,
                    e.RESOLUTION_BIND_PROXIES: t.OFF}

    def onSet(self):
        run('!view3d.overlay true')

    def onSubcontextLeave(self):
        if self.subcontext == c.MeshesSubcontexts.RIG_CLAY:
            run('!cmdRegions.disable disable:1')

    def onSubcontextSet(self):
        if self.subcontext == c.MeshesSubcontexts.RIG_CLAY:
            run('!cmdRegions.disable disable:0')

    def refreshOnSubcontextChange(self, previous, new):
        return True
    

