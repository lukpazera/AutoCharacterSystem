

import lx
import modo
import modox

from . import const as c
from .const import EventTypes as e
from .event_handler import EventHandler


class VisibilityEventHandler(EventHandler):
    
    descIdentifier = 'vis'
    descUsername = 'Visbility Operator'

    @property
    def eventCallbacks(self):
        return {e.MODULE_LOAD_POST: self.event_moduleLoadPost,
                e.PIECE_LOAD_POST: self.event_pieceLoadPost
                }
    
    def event_moduleLoadPost(self, **kwargs):
        try:
            module = kwargs['module']
        except KeyError:
            return
        
        module.iterateOverHierarchy(self._resetVis)

    def event_pieceLoadPost(self, **kwargs):
        try:
            piece = kwargs['piece']
        except KeyError:
            return
        
        piece.iterateOverItems(self._resetVis)
        
    # -------- Private methods
    
    def _resetVis(self, modoItem):
        if not modox.Item(modoItem.internalItem).isOfXfrmCoreSuperType:
            return
        chan = modoItem.channel('visible')
        #if chan is None:
            #return
        #lx.out('%s : %s ' % (chan.item.name, str(chan.get(0.0, lx.symbol.s_ACTIONLAYER_SETUP))))
        if chan.get(0.0, lx.symbol.s_ACTIONLAYER_SETUP) == c.ItemVisibleHint.YES:
            chan.set(c.ItemVisible.DEFAULT, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
