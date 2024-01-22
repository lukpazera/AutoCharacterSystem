

import lx
import lxu
import modo


class ItemFeatureSettings(object):
    """ Use this class to get/set feature list on an item.
    
    This is simple interface that handles item features list
    that is stored in a tag on an item for fast features lookup.
    This interface does NOT deal with item features themselves!
    """
    
    _TAG_ITEM_FEATURES = 'RSIF'
    _TAG_ITEM_FEATURES_CODE = lxu.lxID4(_TAG_ITEM_FEATURES)
    _SEPARATOR = ';'
    
    # -------- Class methods
    
    @classmethod
    def isFeatureAddedFast(cls, identifier, rawItem):
        """ Tests whether given item has item feature added.
        
        Parameters
        ----------
        identifier : str
            String identifier of a feature
            
        rawItem : lx.object.Item
        """
        # Val will be None if there is no tag?
        val = rawItem.GetTag(cls._TAG_ITEM_FEATURES_CODE)
        if val is None:
            return False

        return identifier in val.split(cls._SEPARATOR)

    # -------- Public methods
    
    @property
    def featureIdentifiers(self):
        try:
            val = self._modoItem.readTag(self._TAG_ITEM_FEATURES)
        except LookupError:
            return []
        return val.split(self._SEPARATOR)
    
    @featureIdentifiers.setter
    def featureIdentifiers(self, identsList):
        """ Gets/sets a list of feature identifiers on an item.
        
        Parameters
        ----------
        identsList : list of str
            List of feature identifiers to be stored on an item.
        
        Returns
        -------
        list of str
            Returns list of feature identifiers.
        """
        if len(identsList) > 0:
            tagVal = self._buildIdentifiersTagValue(identsList)
        else:
            tagVal = None
        self._modoItem.setTag(self._TAG_ITEM_FEATURES, tagVal)

    def addFeatureIdent(self, identifier):
        idents = self.featureIdentifiers
        if identifier in idents:
            return False
        idents.append(identifier)
        self.featureIdentifiers = idents
        return True
    
    def removeFeatureIdent(self, identifier):
        if identifier not in self.featureIdentifiers:
            return False
        idents = self.featureIdentifiers
        idents.remove(identifier)
        self.featureIdentifiers = idents
        return True

    # -------- Private methods
    
    def _buildIdentifiersTagValue(self, identsList):
        v = ''
        for ident in identsList:
            v += ident + self._SEPARATOR
        return v[:-1]

    def __init__(self, modoItem):
        self._modoItem = modoItem