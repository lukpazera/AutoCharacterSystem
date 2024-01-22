

from .log import log
from .path import path
from . import const as c 


class Debug(object):
    """ Some debugging tools.
    """
    
    @property
    def output(self):
        """
        Tests whether debug output is enabled.

        Returns
        -------
        bool
        """
        return self._output
    
    @output.setter
    def output(self, state):
        """ Enables/disables extra debug output.
        
        Clients can use this property to check whether extra debug output
        should be enabled or not.
        """
        self._output = state
        
    @property
    def logToFile(self):
        return self._logToFile
    
    @logToFile.setter
    def logToFile(self, state):
        """
        Enable, disable logging to file.

        Parameters
        ----------
        state : bool
        """
        self._logToFile = state
        if not state:
            log.outputToFile(None)
        else:
            filename = path.generateFullFilenamePath(c.Path.TEMP_FILES, 'rs_debug_log.txt')
            log.outputToFile(filename)

    # -------- Private methods

    def __init__(self):
        self._logToFile = False
        self._output = False

debug = Debug()