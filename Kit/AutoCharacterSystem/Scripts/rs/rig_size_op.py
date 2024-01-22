

from .rig import Rig
from .const import EventTypes as e
from .event_handler import EventHandler
from .guide import Guide
from .module_guide import ModuleGuide
from .shape_op import ShapesOperator
from .core import service
from .log import log
from . import const as c


class RigSizeOperator(object):
    """
    This class is used to manage rig reference size property.
    """

    @property
    def referenceSize(self):
        return self._rig.rootItem.referenceSize

    @referenceSize.setter
    def referenceSize(self, newSize):
        self._rig.rootItem.referenceSize = newSize
        service.events.send(e.RIG_REFERENCE_SIZE_CHANGED, rig=self._rig, size=newSize)

    def applyReferenceSize(self, newSize):
        """
        Sets new reference size and applies it to rig.
        This means that all the modules are scaled according to the new size.
        """
        self.referenceSize = newSize

    # -------- Private methods

    def __init__(self, rigInitializer):
        if not isinstance(rigInitializer, Rig):
            try:
                self._rig = Rig(rigInitializer)
            except TypeError:
                raise
        else:
            self._rig = rigInitializer


class RigSizeEventHandler(EventHandler):
    """ Handles events that trigger rig size operations.
    """

    descIdentifier = 'rigsize'
    descUsername = 'Rig Size'

    @property
    def eventCallbacks(self):
        return {e.MODULE_DROP_ACTION_PRE: self.event_moduleDropActionPre,
                e.GUIDE_APPLY_POST: self.event_guideApplyPost,
                e.RIG_REFERENCE_SIZE_CHANGED: self.event_rigReferenceSizeChanged,
                e.MODULE_NEW: self.event_moduleNew,
                e.PIECE_NEW: self.event_pieceNew,
                e.PIECE_SAVE_PRE: self.event_pieceSavePre,
                e.PIECE_LOAD_POST: self.event_pieceLoadPost
                }

    def event_moduleDropActionPre(self, **kwargs):
        """
        Event fired after module is dropped into the scene and before drop action will be applied.

        This covers action on loading modules.

        Parameters
        ----------
        position : modo.Vector3, None
            None means module is not dropped into viewport but simply its preset is loaded.
        """
        try:
            module = kwargs['module']
            action = kwargs['action']
            position = kwargs['position']
        except KeyError:
            return

        # We do not resize guide & shapes if module has snap to mouse and group drop action set
        # and it's dropped into location in viewport. In this case the drop action will do the scaling
        # so there's no need to do it automatically beforehand.
        if action in [c.ModuleDropAction.MOUSE_AND_GROUND] and position is not None:
            return

        rig = Rig(module.rigRootItem)

        rigSizeOp = RigSizeOperator(rig)
        refSize = rigSizeOp.referenceSize

        modGuide = ModuleGuide(module)
        # Set new module size, this scales all the guides and all module shapes as well automatically.
        # The 'silent' argument is for that.
        modGuide.setSize(refSize, silent=False)

        # Changing module size will change its root point as well (unless it's at origin).
        # Changing size happens with relation to origin, so when that's done
        # we need to put the main module back to required position if one was given.
        if position is not None and not modGuide.isLinked:
            modGuide.setToPosition(position)

    def event_guideApplyPost(self, **kwargs):
        try:
            rig = kwargs['rig']
        except KeyError:
            return

        Guide(rig).freezeScale()

    def event_rigReferenceSizeChanged(self, **kwargs):
        """ Update all modules reference size.
        """
        try:
            rig = kwargs['rig']
            refSize = kwargs['size']
        except KeyError:
            return

        for module in rig.modules.allModules:
            ModuleGuide(module).referenceSize = refSize
            for piece in module.pieces:
                piece.referenceSize = refSize

    def event_moduleNew(self, **kwargs):
        """
        When new module is created we need to store rig reference size on it.
        """
        try:
            module = kwargs['module']
        except KeyError:
            return

        rigSizeOp = RigSizeOperator(module.rigRootItem)
        ModuleGuide(module).referenceSize = rigSizeOp.referenceSize

    def event_pieceNew(self, **kwargs):
        """
        When new piece is created we need to set reference size for it from rig.

        Note that this event works correctly ONLY when piece is added via command.
        This is because creating new piece from Piece class adds piece with no rig context yet.
        """
        try:
            piece = kwargs['piece']
        except KeyError:
            return

        rigSizeOp = RigSizeOperator(piece.rigRootItem)
        piece.referenceSize = rigSizeOp.referenceSize

    def event_pieceSavePre(self, **kwargs):
        """
        Make sure to update piece reference size right before save, just in case...
        """
        try:
            piece = kwargs['piece']
        except KeyError:
            return

        rigSizeOp = RigSizeOperator(piece.rigRootItem)
        piece.referenceSize = rigSizeOp.referenceSize

    def event_pieceLoadPost(self, **kwargs):
        """
        When piece is loaded we need to scale all its shapes according to difference
        in reference size between one inside the piece and one in the rig.
        """
        try:
            piece = kwargs['piece']
        except KeyError:
            return

        pieceRefSize = piece.referenceSize
        rigSizeOp = RigSizeOperator(piece.rigRootItem)
        rigRefSize = rigSizeOp.referenceSize
        piece.referenceSize = rigRefSize

        scaleFactor = rigRefSize / pieceRefSize
        shapeOp = ShapesOperator(piece.rigRootItem)
        shapeOp.applyScaleFactorToAssembly(piece.assemblyModoItem, scaleFactor)
