

import lx
import modo
import modox

from ..item_feature import ItemFeature
from ..item import Item
from .. import const as c


class IdentifierFeature(ItemFeature):
    """ Allows for setting an identifier for an item.
    
    Such item can be looked up by its identifier.
    It's also faster to look up identified items.
    """

    GRAPH_IDENTIFIER = 'rs.identifier'
    CHAN_IDENTIFIER = 'rsIdentifier'

    # -------- Description attributes
    
    descIdentifier = c.ItemFeatureType.IDENTIFIER
    descUsername = 'Identifier'

    # -------- Public methods
        
    def onRemove(self):
        """ Clear identifier tag and graph link on remove.
        """
        self.identifier = None
    
    # --- Custom methods
    
    @property
    def identifier(self):
        return self.item.identifier

    @identifier.setter
    def identifier(self, identifier):
        """ Gets/Sets new item identifier.
        
        Item with identifier is linked with module root via a graph.
        This allows for fast lookups of identified items within a module.
        
        Parameters
        ----------
        identifier : str, None
            Pass None to clear identifier.

        Returns
        -------
        str, None
            Identifier string or None if identifier could not be found.
        """
        self.item.identifier = identifier

    # -------- Private methods
    
    def _setIdentifierLink(self):
        """ Adds link between item with identifier and module root.
        
        This is to provide faster lookup of module key items.
        """
        modox.ItemUtils.clearForwardGraphConnections(self.modoItem, self.GRAPH_IDENTIFIER)
        modox.ItemUtils.addForwardGraphConnections(self.modoItem, self.item.moduleRootItem.modoItem, self.GRAPH_IDENTIFIER)
    
    def _removeIdentifierLink(self):
        modox.ItemUtils.clearForwardGraphConnections(self.modoItem, self.GRAPH_IDENTIFIER)