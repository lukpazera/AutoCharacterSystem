

import lx
import modo
import modox

from ..item_features.controller import ControllerItemFeature
from ..item_mesh import MeshItem
from ..item_mesh import MeshItemResolutionsEventHandler
from ..attach_item import AttachItem
from .. import const as c
from ..log import log
from ..util import run


class BindProxyItem(MeshItem):

    descType = c.RigItemType.BIND_PROXY
    descUsername = 'Bind Proxy Mesh'
    descDefaultName = 'BindProxy'
    descPackages = []
    descSynthName = False
    descDropScriptSource = c.DropScript.ITEM_ON_ITEM_SOURCE
    descDropScriptDestination = c.DropScript.ITEM_ON_ITEM_DESTINATION

    def init(self):
        self._attachItem = AttachItem(self)
    
    def setupCommandRegion(self):
        """ Sets up command region on the proxy mesh.
        
        Command region will be enabled by default!
        """
        bindloc = self._attachItem.attachedToBindLocator
        if bindloc is None:
            return
        
        relatedControllers = bindloc.relatedControllers
        if not relatedControllers:
            return

        try:
            ctrl = ControllerItemFeature(relatedControllers[0])
        except TypeError:
            return
        xitem = modox.Item(ctrl.modoItem.internalItem)
        itemCmd = xitem.itemCommand
        color = bindloc.regionColorRGB
        
        scene = modo.Scene()
        scene.select(self.modoItem, add=False)
        run('!select.type polygon')
        
        # We only want to apply region to polygons that are not on the inner side
        # of the proxy (if there is an inner side).
        # We check every polygon against the inner side material tag.
        # If it's on inner side - we skip and not select it for command region application.
        run('!select.drop polygon')
        mesh = modo.Mesh(self.modoItem.internalItem)
        for polygon in mesh.geometry.polygons:
            if polygon.materialTag != 'Bind Proxy Inner Side': # Fixed material name for now. Should be looked up by graph later.
                polygon.select(replace=False)

        # This will fail if there's a command region with the same name already assigned.
        run('!poly.pcrAssign {%s} selItem:{%s} cmd:{%s} color:{%f %f %f}' % (ctrl.item.nameAndSide, ctrl.modoItem.id, itemCmd, color[0], color[1], color[2]))
        run('!select.drop polygon')
    
    @property
    def commandRegionEnabled(self):
        return self.getChannelProperty('pcrEnable')
    
    @commandRegionEnabled.setter
    def commandRegionEnabled(self, value):
        self.setChannelProperty('pcrEnable', value)


class BindProxyEventHandler(MeshItemResolutionsEventHandler):
    """
    Event handler for updating item mesh resolution data.
    """
    descIdentifier = 'bproxymres'
    descUsername = 'Bind Proxies Resolutions'
    descElementSet = c.ElementSetType.BIND_PROXIES
