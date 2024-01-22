

import lx
import modo
import modox

from .items.guide import GuideItem
from .log import log
from .debug import debug
from .event_handler import EventHandler
from . import const as c
from .const import EventTypes as e


class GuideSymmetry(object):
    """ Takes care of updating guides that have symmetry enabled.
    
    This class should be used as part of guide update process.
    
    Methods
    -------
    scanItem : modo.Item
        This needs to be called for every item in rig, a list of guides
        that have symmetry on will be created.
    
    applySymmetry
        This needs to be called before guide matching is performed.
        This method applies new transforms to guides that have symmetry on.
    """
    
    def init(self):
        self._guides = []
    
    def setGuides(self, guides):
        """ Sets a list of guides to perform transform operations on.
        """
        self.init()
        for guide in guides:
            self.scanItem(guide)

    def scanItem(self, guide):
        if not isinstance(guide, GuideItem):
            try:
                guide = GuideItem(guide)
            except TypeError:
                return
        if guide.side is not c.Side.CENTER:
            self._guides.append(guide)
    
    def mirrorTransforms(self):
        """ Mirrors transforms for provided guides.
        
        Use this to flip the guide to the other side.
        Note that edit action needs to be applied for this to work properly.
        
        Returns
        -------
        bool
            True when at least one guide transform was changed.
            False otherwise.
        """
        if not self._guides:
            return False

        xfrms = []
        for guide in self._guides:
            xfrms.append(self._calculateFlippedTransform(guide.modoItem, guide.modoItem))

        for x in range(len(self._guides)):
            self._applyFlippedTransform(self._guides[x].modoItem, xfrms[x])
            if debug.output:
                log.out('Applying flipped transform to guide during mirror: %s' % self._guides[x].modoItem.name)
        
        return True

    def applySymmetry(self):
        """ Applies flipped transform to a guide.

        Note that edit action needs to be applied for this to work properly.

        Returns
        -------
        bool
            True when at least one guide transform was changed.
            False otherwise.
        """
        if not self._guides:
            return False
        
        # Filter guides with no symmetry out.
        symmetryGuides = [guide for guide in self._guides if guide.symmetricGuide is not None]
        if not symmetryGuides:
            if debug.output:
                log.out("No symmetric guides to apply symmetry to!", log.MSG_ERROR)
            return False
        
        xfrms = []
        space = lx.symbol.iLOCATOR_LOCAL
        for guide in symmetryGuides:
            xfrms.append(self._calculateFlippedTransform(guide.symmetricGuide.modoItem, guide.modoItem, space=space))

        for x in range(len(symmetryGuides)):
            self._applyFlippedTransform(symmetryGuides[x].modoItem, xfrms[x], space=space)
            if debug.output:
                log.out('Applying flipped transform to guide during applySym: %s' % self._guides[x].modoItem.name)
            
        return True

    # -------- Private methods

    def _calculateFlippedTransform(self,
                                   sourceModoItem=None,
                                   targetModoItem=None,
                                   space=lx.symbol.iLOCATOR_LOCAL):
        """ Calculates transform flipped on x from given item's world transform.
        
        The alignment is not mirrored.
        This method calculates new local transform matrix4 and stores it.
        
        Parameters
        ----------
        sourceModoItem : modo.Item, optional
            Modo item which world transform will be taken as reference.
            If item is not set the guide itself will be used as reference.
            This allows for flipping the item itself, with no reference.
            
        targetModoItem : modo.Item, optional
            The item to which the flipped transform is going to be applied.
            It's important that this item is known because the flipped transform
            will be in world space instead of local space if target item has
            inherit pos/rot off.
            When not set this is the same as the source item.

        space : int
            lx.symbol.iLOCATOR_XXX
            Flipped transforms can be calculated either in local or in world space.

        Returns
        -------
        modo.Matrix4
        """
        if sourceModoItem is None:
            return
        if targetModoItem is None:
            targetModoItem = sourceModoItem

        # Negative X scale matrix is used.
        negativeScaleMtx = modo.Matrix4()
        negativeScaleMtx.m[0][0] = -1.0

        refMtxObject = sourceModoItem.channel('worldMatrix').get() # this gets lx.unknown
        refWorldMtx = modo.Matrix4(refMtxObject)
        flippedWorldMtx = negativeScaleMtx * refWorldMtx * negativeScaleMtx
        
        # Checking for inherit position/rotation is iffy now.
        # It assumes that either none of these or all of these are switched.
        # TODO: Make it more robust to work with individual switches being turned on/off.
        inheritPos = bool(targetModoItem.channel('inheritPos').get())
        inheritRot = bool(targetModoItem.channel('inheritRot').get())
        
        if space == lx.symbol.iLOCATOR_LOCAL and inheritPos and inheritRot:
            refMtxObject = sourceModoItem.channel('wParentMatrix').get()
            refParentMtx = modo.Matrix4(refMtxObject)
                    
            # We are flipping both world and parent matrices on X.
    
            flippedParentMtx = negativeScaleMtx * refParentMtx * negativeScaleMtx
            # Parent matrix is inverted as well as we want go get local transforms.
            flippedParentMtx.invert()
        else:
            flippedParentMtx = modo.Matrix4()
        
        return flippedWorldMtx * flippedParentMtx
    
    def _applyFlippedTransform(self, modoItem, xfrmMatrix4, space=lx.symbol.iLOCATOR_LOCAL):
        """ Applies previously calculated flipped transform.
        
        This methods works only when the calculate method above was already called.
        
        Parameters
        ----------
        modoItem : modo.Item
        xfrmMatrix4 : modo.Matrix4
        """
        position = modo.Vector3(xfrmMatrix4.position)
        orientation = modo.Matrix3(xfrmMatrix4)
        scale = xfrmMatrix4.scale() # This is function and returns modo.Vector3 not tuple for some reason
        modox.TransformUtils.applyTransform(modoItem,
                                            position,
                                            orientation,
                                            scale,
                                            mode=space,
                                            action=lx.symbol.s_ACTIONLAYER_SETUP)
    
    def __init__(self):
        self.init()


class GuideSymmetryEventHandler(EventHandler):
    """ Updates symmetry if needed.
    """
    descIdentifier = 'gdsym'
    descUsername = 'Guide Symmetry Event Handler'

    @property
    def eventCallbacks(self):
        return {e.GUIDE_LINK_CHANGED: self.event_guideLinkChanged,
                }

    def event_guideLinkChanged(self, **kwargs):
        try:
            sourceGuide = kwargs['guide']
        except KeyError:
            return

        symmetryDrivenGuide = sourceGuide.symmetryTargetGuide
        if symmetryDrivenGuide is None:
            return

        # This guide is driving symmetry on another guide,
        # the driven guide needs to have the same link set up.
        linkSourceGuide = sourceGuide.transformLinkedGuide

        if linkSourceGuide is None:
            # Link was removed.
            symmetryDrivenGuide.transformLinkedGuide = None
            return

        linkSymmetryDrivenGuide = linkSourceGuide.symmetryTargetGuide
        if linkSymmetryDrivenGuide is not None:
            linkTarget = linkSymmetryDrivenGuide
        else:
            linkTarget = linkSourceGuide

        symmetryDrivenGuide.transformLinkedGuide = linkTarget
