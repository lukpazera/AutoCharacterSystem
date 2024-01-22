

from .user_value import userValues
from . import const as c


class UserInterface(object):
    """ Deals with parts of UI that can be queried/set from code.
    """
    
    _PREFIX = 'rs.ui.'

    def getState(self, key):
        """ Gets one of global ui state values.
        
        Parameters
        ----------
        key : str
            Key for the UI state, one of rs.c.UIState.XXX
        
        Returns
        -------
        str
        """
        return userValues.get(self._PREFIX + key)
    
    def setState(self, key, state):
        """ Sets one of globabl ui state values.
        
        Parameters
        ----------
        key : str
            Key for the UI state, one of rs.c.UIState.XXX
        
        state : str
            Ui state value such as rs.c.MeshEditMode.XXX
        """
        userValues.set(self._PREFIX + key, state)

    def init(self):
        """ Initialises UI, should be called on startup from rs.service.
        
        Register all the temporary user values here.
        """
        pass

ui = UserInterface()
