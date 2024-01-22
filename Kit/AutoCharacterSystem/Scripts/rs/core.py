
""" Core service module.

    Service is used to register and obtain information about registered
    rigging system components.
"""


import time

import lx

from . import sys_component_op
from . import events_op
from . import notifier
from . import path
from . import core_buffer
from . import session_listen
from . import debug
from . import const as c
from .log import log
from .path import path
from .user_value import userValues
from .ui import ui
from .debug import debug


SYSTEM_VERSION = 1


class GlobalState(object):
    ControlledDrop = False


class Service (object):
    """ Service is a singleton and is always present then system is running.
    """

    @property
    def systemVersion(self):
        """
        Gets current system version of the plugin.

        Every time something changes in the codebase that breaks compatibility
        with assets created with previous versions system version number goes up.
        This way code can branch out based on system version if necessary.

        Returns
        -------
        int
        """
        return SYSTEM_VERSION

    @property
    def debug(self):
        """ Gets access to debugging helper tools.
        """
        return debug

    @property
    def systemComponent(self):
        """ Gets access to system component operator.
        
        Use this operator to register/retrieve registered system components.
        """
        return self._sysComponentOp

    @property
    def path(self):
        """ Gets access to paths registered with the system.
        """
        return path

    @property
    def userValue(self):
        """ Gets access to user values registered with the system.
        """
        return userValues

    @property
    def ui(self):
        """ Gives access to aspects of UI that can be queried/set from code.
        
        Returns
        -------
        UserInterface
        """
        return ui
    
    @property
    def buffer(self):
        """ Gets access to a simple buffer that allows for storing objects of any type.
        """
        return self._buffer
        
    @property
    def events(self):
        return self._eventsOp

    def notify(self, notifierIdent, flags):
        """ Sends command notification.
        
        Parameters
        ----------
        notifierIdent : str
        
        flags : lx.symbol.fCMDNOTIFY_XXX
        """
        try:
            notifierObj = self.systemComponent.get(notifier.Notifier.sysType(), notifierIdent)
        except LookupError:
            raise LookupError
        notifierObj.notify(flags)

    @property
    def listenToScene(self):
        return bool(lx.eval('user.value rs.listenToScene ?')) # faster then using script sys service!
    
    @listenToScene.setter
    def listenToScene(self, state):
        """ Toggles listening to scene events on/off.
        
        NOTE: Don't use it unless you really know what you're doing.
        This method is used by rs.Command to pause rs listeners when the command is in progress.

        Parameters
        ----------
        bool
        """
        lx.eval('!user.value rs.listenToScene %d' % int(state))

    @property
    def globalState(self):
        """
        Gives access to predefined global states.

        This is not great solution, I should probably think about better implementation
        but it'll do for now.
        """
        return GlobalState

    # -------- Private methods

    def _onSystemReady(self):
        """ Gets called when the system is ready, right before the main loop starts.
        """
        self._setupUserValues()
        self.ui.init()
        self.listenToScene = True

    def _setupUserValues(self):
        """ Sets up user values used by the system.
        """
        self.userValue.registerTemporary(c.UserValue.LISTEN_TO_SCENE, 'boolean')
        self.userValue.registerTemporary(c.UserValue.PRESET_DROP_ACTION_CODE, 'string')
        self.userValue.registerTemporary(c.UserValue.PRESET_DEST_IDENT, 'string')
        self.userValue.registerTemporary(c.UserValue.PRESET_FILENAME, 'string')

    def __init__ (self):
        self._sysComponentOp = sys_component_op.SystemComponentsOperator()
        self._eventsOp = events_op.EventsOperator()
        self._buffer = core_buffer.Buffer()
        
        self._sessionListener = session_listen.SessionListener()
        self._sessionListener.registerCallback(session_listen.SessionListener.Event.ON_SYSTEM_READY, self._onSystemReady)

service = Service()