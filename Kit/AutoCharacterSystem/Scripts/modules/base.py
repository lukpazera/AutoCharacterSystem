
""" Base module functionality.
"""


import lx
import modo
import modox

import rs
from rs.const import EventTypes as e


KEY_SOCKET = 'mainSocket'
KEY_MASTER_CTRL = 'masterCtrl'


class RootMotion(rs.base_ModuleProperty):

    descIdentifier = "rootm"
    descUsername = "rootMotion"
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descScope = rs.base_ModuleProperty.Scope.GLOBAL
    descApplyGuide = False
    descRefreshContext = True
    descTooltipMsgTableKey = 'baseRootMotion'

    _ROOT_MOTION_PIECE = 'rootMotion'

    def onSet(self, value):
        refresh = False

        # Don't do anything if piece is already there.
        try:
            rootMotionPiece = self.module.getFirstPieceByIdentifier(self._ROOT_MOTION_PIECE)
        except LookupError:
            rootMotionPiece = None

        if value:
            if rootMotionPiece is not None:
                return
            newPiece = self.module.addPiece(self._ROOT_MOTION_PIECE, updateItemNames=True)

            # need to set up link between socket and bind locator in th e piece.
            bloc = newPiece.getKeyItem(rs.c.KeyItem.BIND_LOCATOR)
            socket = self.module.getKeyItem(KEY_SOCKET)
            socket.linkedBindLocatorModoItem = bloc.modoItem

            refresh = True  # To refresh the context after root motion piece was added

        else:
            if rootMotionPiece is None:
                return
            self.module.removePiece(self._ROOT_MOTION_PIECE)

        return refresh

    def onQuery(self):
        try:
            rootMotionPiece = self.module.getFirstPieceByIdentifier(self._ROOT_MOTION_PIECE)
        except LookupError:
            return False
        return True


class BaseModule(rs.base_FeaturedModule):

    descIdentifier = 'base'
    descUsername = 'Base'
    descFeatures = [RootMotion]

    def updateReferenceSize(self, refSize):
        """
        Updates reference size on the module user channel.
        """
        chan = self.module.rootModoItem.channel('ReferenceSize')
        if chan is not None:
            chan.set(refSize, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)


class BaseModuleEventHandler(rs.EventHandler):
    """ Handles events concerning base module.
    """

    BASE_MODULE_IDENTIFIER = 'base'
    
    descIdentifier = 'basemod'
    descUsername = 'Base Module'
  
    @property
    def eventCallbacks(self):
        return {e.RIG_REFERENCE_SIZE_CHANGED: self.event_rigReferenceSizeChanged,
                e.MODULE_LOAD_POST: self.event_moduleLoadPost,
                e.PLUG_DISCONNECTED: self.event_plugDisconnected
                }

    def event_rigReferenceSizeChanged(self, **kwargs):
        """ Update Reference size channel value on the base module.
        """
        try:
            rig = kwargs['rig']
            refSize = kwargs['size']
        except KeyError:
            return

        base = rig.modules.baseModule
        if base is None:
            return

        base = BaseModule(base)
        base.updateReferenceSize(refSize)

    def event_moduleLoadPost(self, **kwargs):
        """ Called after module was loaded and added to rig.
        
        When module is loaded we need to do following:
        - go through all its controllers that have dynamic space
        and link them to the base as their default (rig) space.
        - go through all plugs in the rig and connect them to base socket.
        """
        try:
            module = kwargs['module']
        except KeyError:
            return

        rig = rs.Rig(module.rigRootItem)
            
        # Base module was dropped.
        # We need to get all the rig controllers and all the plugs.
        if str(module.identifier).lower() == self.BASE_MODULE_IDENTIFIER:
            baseModule = module
            plugModoItems = rig[rs.c.ElementSetType.PLUGS].elements

        # Other module was dropped.
        # We only need controllers and plug modo items from this module. 
        else:
            baseModule = rig.modules.baseModule
            if baseModule is None:
                return # No need to do anything if there's no base module in the rig yet.
            plugModoItems = module.getElementsFromSet(rs.c.ElementSetType.PLUGS)

        if plugModoItems:
            self._attachUnconnectedPlugsToBase(plugModoItems, baseModule)

    def event_plugDisconnected(self, **kwargs):
        """ Event sent when a plug was disconnected from a socket.
        
        If plug belongs to a rig which has a base module we're going to automatically
        connect the plug to the base.
        """
        try:
            plug = kwargs['plug']
        except KeyError:
            return

        rig = rs.Rig(plug.rigRootItem)
        baseModule = rig.modules.baseModule
        if baseModule is None:
            return
        
        self._attachUnconnectedPlugsToBase([plug.modoItem], baseModule)

    # -------- Private methods

    def _attachUnconnectedPlugsToBase(self, plugModoItems, baseModule):
        """ Attaches all unconnected plugs from a list to a base module.
        
        Parameters
        ----------
        plugModoItems : list of modo.Item
            This is the list of plugs that may need to be connected.
            Only plugs that have no connection yet will be connected.
            
        baseModule : Module
            Base module to connect to.
        """
        socket = baseModule.getKeyItems(KEY_SOCKET)[KEY_SOCKET]
        
        for modoItem in plugModoItems:
            try:
                plug = rs.PlugItem(modoItem)
            except TypeError:
                continue
            if plug.socket is not None:
                continue
            plug.connectToSocket(socket, drawConnection=False)
