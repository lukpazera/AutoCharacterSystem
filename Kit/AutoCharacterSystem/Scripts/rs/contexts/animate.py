

import lx

import rs.context
from ..util import run
from ..const import ElementSetType as e
from ..const import ItemVisible as v
from ..const import TriState as t
from ..const import Context as cxt
from ..items.bind_proxy import BindProxyItem
from ..log import log
from ..rig_clay_op import RigClayUtils


class ContextAnimate(rs.context.Context):
    
    _SETTING_GROUP_ANIM_CONTEXT_VISIBILITY = 'animcxtvis'

    descIdentifier = cxt.ANIMATE
    descUsername = 'Animate'

    setup = False # Switch setup mode off
    isHierarchyVisible = False

    @property
    def elementsVisibleToggle(self):        
        return {None: [e.CONTROLLERS_SET,
                       e.BIND_SKELETON,
                       e.RESOLUTION_BIND_MESHES, e.RESOLUTION_RIGID_MESHES, e.RESOLUTION_BIND_PROXIES,
                       e.SOCKETS]}
        
    @property
    def elementsVisible(self):
        """ Gets a dictionary of element set id/visibility value pairs.
        
        Visibility of bind locators and meshes can be toggled via a setting.
        """
        return {e.CONTROLLERS_SET: True,
                e.BIND_SKELETON: True,
                e.SOCKETS: False,
                e.RESOLUTION_BIND_MESHES: True,
                e.RESOLUTION_RIGID_MESHES: True,
                e.RESOLUTION_BIND_PROXIES: True}
    
    elementsSelectable = {e.BIND_SKELETON: t.OFF,
                          e.RESOLUTION_BIND_MESHES: t.OFF,
                          e.RESOLUTION_RIGID_MESHES: t.OFF,
                          e.RESOLUTION_BIND_PROXIES: t.OFF}

    def onSet(self):
        run('!item.componentMode item true')
        run('!view3d.overlay false')
        RigClayUtils.updateRegionsEnableState()
    
    def onLeave(self):
        RigClayUtils.updateRegionsEnableState()
        run('!cmdRegions.disable disable:1')
