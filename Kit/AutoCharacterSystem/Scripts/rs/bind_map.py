

import lx
import modo
import modox

from . import notifier
from . import const as c
from .item_settings import SettingsTag


class BindMap(object):
    
    _SETTING_BIND_MAP = 'bmap'
    
    _BING_MAP_TAG = 'RPBM' # RP stands for "rig permanent" - a tag that doesn't get removed when item is standardized.
    
    def clear(self):
        """ Clears all mappings.
        """
        self._settingsTag.clear()

    def get(self):
        """ Gets entire map as dictionary.
        
        Returns
        -------
        dict {str: str}
            bindLocatorKey : weightMapName
            Bind locator key is a string from name: side+moduleName+baseName
        """
        return self._settingsTag.get(str, str)

    def getMapping(self, bindLocatorItem):
        """ Gets weight map mapping for particular bind locator.
        
        Parameters
        ----------
        bindLocatorItem : BindLocatorItem

        Returns
        -------
        str
        
        Raises
        ------
        LookupError
            When bind locator key is not in the bind map.
        """
        bmap = self.get()
        try:
            return bmap[self._getKey(bindLocatorItem)]
        except KeyError:
            pass
        raise LookupError
        
    def setMapping(self, bindLocatorItem, weightMapName=None):
        """ Sets new mapping for a bind locator.
        
        Parameters
        ----------
        bindLocatorItem : BindLocatorItem
        
        weightMapName : str, None
            When None is passed it clears bind locator item from bind map.
        """
        bmap = self.get()
        if weightMapName is not None:
            bmap[self._getKey(bindLocatorItem)] = weightMapName
        else:
            del bmap[self._getKey(bindLocatorItem)]
        self._settingsTag.set(bmap)
    
    # -------- Private methods

    def _getKey(self, bindLocatorItem):
        return bindLocatorItem.renderNameFromTokens([c.NameToken.SIDE, c.NameToken.MODULE_NAME, c.NameToken.BASE_NAME])
                                                
    def __init__(self, bindMeshItem):
        self._bmesh = bindMeshItem
        self._settingsTag = SettingsTag(bindMeshItem.modoItem, self._BING_MAP_TAG)


class NotifierBindMapUI(notifier.Notifier):
    """ Notify when bind map properties have to be refreshed.
    """

    descServerName = c.Notifier.BIND_MAP_UI
    descUsername = 'Bind Map UI Update'