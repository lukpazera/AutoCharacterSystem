

import lx
import modo
import modox

from ..xfrm_link_setup import TransformLinkSetup
from ..const import TransformLinkType as t
from ..log import log


class StaticTransformLinkSetup(TransformLinkSetup):
    """ Static transform link setup between items.
    
    Target item transforms are linked to extra transform items
    on the linked item. Editing such linked item via transform tool
    doesn't give correct tool handles feedback so this link should
    be used for fixed linking that is not editable further by user.
    """

    descIdentifier = t.STATIC
    descUsername = 'Fixed'

    def onNew(self, compensation=True):
        self._setupLink(self.targetModoItem)

    def onRemove(self):
        self._removeSetup()

    @property
    def setupItems(self):
        """ Gets a list of all items comprising the link setup.
        
        In this case these will be all transform items that have their
        matrices driven by the target item.
        
        Returns
        -------
        list of modo.Item
        """
        xfrmItems = []
        for xfrmItem in modo.LocatorSuperType(self.modoItem).transforms:
            # It's somehow possible that this method returns non transform items.
            # In one scene there was a link to regular locator item.
            # TODO: Investigate this at some point.
            # It might be a side effect of changing graph names without rebuilding
            # entire asset.
            if xfrmItem.superType != 'transform':
                continue
            mtxChan = xfrmItem.channel('matrix')
            if mtxChan is None:
                continue
            try:
                driverChan = mtxChan.reverse(0)
            except LookupError:
                continue
            if driverChan.item == self.targetModoItem:
                xfrmItems.append(xfrmItem)
        return xfrmItems

    # -------- Private methods
    
    def _setupLink(self, itemTo):
        """ Creates link setup.
        
        Setup for this link requires only the matrix compose item.
        
        We plug all world transform channels in correct order as matrix
        compose inputs, then plug the output into the itemFrom
        parent channel.
        """
        modox.TransformUtils.applyEdit()

        scene = modo.Scene()
        loc = modo.LocatorSuperType(self.modoItem)
        
        # 1.
        # Force creating primary transform items.
        # The order of extra transform items will be broken otherwise.
        posXfrm = loc.position
        rotXfrm = loc.rotation
        sclXfrm = loc.scale
        
        # 2.
        # Preserve world position and orientation of the linked item.
        # This is done by calculating new local transform for the item
        # in target item's space.
        m = self.modoItem.channel('worldMatrix').get()
        itemFromWMtx = modo.Matrix4(m)
        m = self.targetModoItem.channel('worldMatrix').get()
        itemToWMtx = modo.Matrix4(m)

        # Now calculate new local transforms for the item.
        itemToInvMtx = itemToWMtx.inverted()
        localXfrmMtx = itemFromWMtx * itemToInvMtx
    
        pos = modo.Vector3(localXfrmMtx.position)
        rot = modo.Matrix3(localXfrmMtx)
    
        rotOrder = modox.TransformUtils.getRotationOrder(rotXfrm)
        loc.position.set(localXfrmMtx.position, time=0.0, action=lx.symbol.s_ACTIONLAYER_SETUP)
        loc.rotation.set(rot.asEuler(degrees=False, order=rotOrder), time=0.0, action=lx.symbol.s_ACTIONLAYER_SETUP)
        
        # 3.
        # Insert new transform items and link them with the target item
        # world matrices.
        # Transforms need to be added in correct order
        # (at the top of the transform stack)
        lscl = loc.transforms.insert('scale', 'prepend')
        lrot = loc.transforms.insert('rotation', 'prepend')
        lpos = loc.transforms.insert('position', 'prepend')
        
        inposChan = lpos.channel('matrix')
        inrotChan = lrot.channel('matrix')
        insclChan = lscl.channel('matrix')

        wposChan = itemTo.channel('wposMatrix')
        wrotChan = itemTo.channel('wrotMatrix')
        wsclChan = itemTo.channel('wsclMatrix')
    
        wsclChan >> insclChan
        wrotChan >> inrotChan
        wposChan >> inposChan

    def _removeSetup(self):
        """ Deletes all setup items and performs any clean up actions.
        """
        modox.TransformUtils.applyEdit()

        # 1.
        # Recalculate item transforms back to world space
        # and apply them as new local transforms.
        m = self.modoItem.channel('worldMatrix').get()
        itemFromWMtx = modo.Matrix4(m)
        pos = modo.Vector3(itemFromWMtx.position)
        rot = modo.Matrix3(itemFromWMtx)
    
        loc = modo.LocatorSuperType(self.modoItem)
        rotOrder = modox.TransformUtils.getRotationOrder(self.modoItem) # Get primary xfrm item rotation order
        loc.position.set(itemFromWMtx.position, time=0.0, action=lx.symbol.s_ACTIONLAYER_SETUP)
        loc.rotation.set(rot.asEuler(degrees=False, order=rotOrder), time=0.0, action=lx.symbol.s_ACTIONLAYER_SETUP)
        # 2.
        # Remove transform items.
        constraintSetupItems = self.setupItems
        for item in constraintSetupItems:
            lx.eval('!item.delete child:0 item:{%s}' % item.id)
    

