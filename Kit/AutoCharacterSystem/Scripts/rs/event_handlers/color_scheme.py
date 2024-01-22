
""" Event handler that is processing events affecting item colors.
"""


import modo

from ..event_handler import EventHandler
from ..const import EventTypes as e
from ..log import log
from ..item_features.color import ColorItemFeature


class ColorSchemeEventHandler(EventHandler):
    """ Handles events that affect item colors.
    """

    descIdentifier = 'colschm'
    descUsername = 'Color Scheme'
  
    @property
    def eventCallbacks(self):
        return {e.MODULE_SIDE_CHANGED: self.event_moduleSideChanged,
                e.ITEM_SIDE_CHANGED: self.event_itemSideChanged,
                e.RIG_COLOR_SCHEME_CHANGED: self.event_colorSchemeChanged,
                e.PIECE_LOAD_POST: self.event_postLoadPiece}

    def event_moduleSideChanged(self, **kwargs):
        try:
            module = kwargs['module']
        except KeyError:
            return
 
        module.iterateOverHierarchy(self._callReapplyItemColor)

    def event_itemSideChanged(self, **kwargs):
        try:
            item = kwargs['item']
        except KeyError:
            return
 
        self._callReapplyItemColor(item)

    def event_colorSchemeChanged(self, **kwargs):
        try:
            rig = kwargs['rig']
        except KeyError:
            return
 
        rig.iterateOverHierarchy(self._callReapplyItemColor)

    def event_postLoadPiece(self, **kwargs):
        try:
            piece = kwargs['piece']
        except KeyError:
            return

        piece.iterateOverItems(self._callReapplyItemColor,
                               includeSubassemblies=True)

    # -------- Private methods
    
    def _callReapplyItemColor(self, modoItem):
        try:
            colorFeature = ColorItemFeature(modoItem)
        except TypeError:
            return
        colorFeature.reapplyColor()

