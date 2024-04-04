
""" Path managment module.
"""


import os
import lx

from . import const as c


class Path(object):
    """ Manages paths that should be known to the system.
    
    Paths are identified by string keys.
    Default path keys are defined as constants - rs.c.Path.XXX
    Paths can be accessed with get() method or via pathObject[pathIdent].
    """
    
    MAIN_PATH_ALIAS = 'kit_AutoCharacterSystem:'
    MAIN_PATH = lx.eval('query platformservice alias ? "%s"' % MAIN_PATH_ALIAS)
    
    # -------- Public methods

    def register(self, ident, path):
        if ident not in self._paths:
            self._paths[ident] = []
        self._paths[ident].append(path)

    def getAll(self, ident):
        """ Gets all paths registered with given identifier.
        
        Parameters
        ----------
        ident : str
        
        Returns
        -------
        list of str

        Raises
        ------
        LookupError
            If there are no paths with given identifier registered.
        """
        try:
            return self._paths[ident]
        except KeyError:
            raise LookupError

    def get(self, ident):
        """ Gets first path registered with given identifier.
        
        Parameters
        ----------
        ident : str
        
        Returns
        -------
        str

        Raises
        ------
        LookupError
            If there is no path with given identifier registered.
        """
        try:
            paths = self.getAll(ident)
        except LookupError:
            raise
        if not paths:
            raise LookupError
        return paths[0]

    def getFullPathToFile(self, pathIdent, filename):
        """ Gets full path (with filename) to a given file.
        
        Parameters
        ----------
        pathIdent : str
        
        filename : str
            Name of the file to get, should not include any paths.
            Should include file extension.
        
        Returns
        -------
        str
        
        Raises
        ------
        LookupError
            If given file cannot be found in any of the paths registered
            under given ident.
        """
        try:
            paths = self.getAll(pathIdent)
        except LookupError:
            raise
        
        for path in paths:
            fullPath = os.path.join(path, filename)
            if os.path.isfile(fullPath):
                return fullPath
        
        raise LookupError

    def generateFullFilenamePath(self, pathIdent, filename):
        """ Generates full filename for a file with a given name and path.
        
        Parameters
        ----------
        pathIdent : str
            Ident of a path (c.Path.XXX).
            If there are multiple paths under the ident the first path is used.
        
        filename : str
            Name of the file (with extension).

        Raises
        ------
        LookupError
            When bad path ident was passed.
        """
        try:
            paths = self.getAll(pathIdent)
        except LookupError:
            raise
        
        return os.path.join(paths[0], filename)

    # -------- Private methods
    
    def _setDefaultPaths(self):
        self.register(c.Path.MAIN, self.MAIN_PATH)
        self.register(c.Path.CONFIGS, os.path.join(self.MAIN_PATH, 'Configs'))
        self.register(c.Path.TEMP_FILES, os.path.join(self.MAIN_PATH, 'Temp'))
        self.register(c.Path.SCRIPTS, os.path.join(self.MAIN_PATH, 'Scripts'))
        self.register(c.Path.PRESETS, os.path.join(self.MAIN_PATH, 'Presets'))
        self.register(c.Path.RIGS, os.path.join(self.MAIN_PATH, 'Presets', 'Rigs'))
        self.register(c.Path.MODULES, os.path.join(self.MAIN_PATH, 'Presets', 'Modules'))
        self.register(c.Path.MODULES_INTERNAL, os.path.join(self.MAIN_PATH, 'Presets_Internal', 'Modules'))
        self.register(c.Path.PRESETS_INTERNAL, os.path.join(self.MAIN_PATH, 'Presets_Internal'))
        self.register(c.Path.PIECES, os.path.join(self.MAIN_PATH, 'Presets_Internal', 'Pieces'))
        self.register(c.Path.THUMBNAILS, os.path.join(self.MAIN_PATH, 'Thumbnails'))

    def __init__(self):
        self._paths = {}
        self._setDefaultPaths()
    
    def __getitem__(self, ident):
        return self.get(ident)

path = Path()