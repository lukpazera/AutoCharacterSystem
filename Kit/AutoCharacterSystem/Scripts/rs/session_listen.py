
import lxifc
import lx
import modo


class SessionEvents(object):
    
    ON_SYSTEM_READY = 1


class SessionListener(lxifc.SessionListener):
    """ Session listener is used to execute code when MODO starts up.
    """
    
    Event = SessionEvents

    def registerCallback(self, ident, callback):
        """ Registers new callback function.
        
        Parameters
        ----------
        ident : on of Event constants.
            Defines the type of session event the callback will be attached to.
            
        callback : function
            function that will be called when an event happens.
        """
        try:
            eventsList = self._callbacks[ident]
        except KeyError:
            self._callbacks[ident] = []
            
        self._callbacks[ident].append(callback)

    def sesl_SystemReady(self):
        try:
            callbacks = self._callbacks[self.Event.ON_SYSTEM_READY]
        except KeyError:
            return
        
        for callback in callbacks:
            callback()

    # -------- Private methods

    def __init__(self):
        self._callbacks = {}
        self.COM = lx.object.Unknown(self)
        lx.service.Listener().AddListener(self.COM)

    def __del__(self):
        lx.service.Listener().RemoveListener(self.COM)

