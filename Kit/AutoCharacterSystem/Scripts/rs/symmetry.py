

from . import const as c
from .module import Module
from .item import Item


class SymmetryUtils(object):

    @classmethod
    def buildSymmetryMap(cls, items):
        """ Builds symmetry map from given list of items.

        Parameters
        ----------
        items : [Item], [modo.Item]

        Returns
        -------
        Symmetry map is a dictionary of dictionaries containing all the items
        from the list split into 3 categories - left side, right side, center.
        To access items from map you can do:

        map[side][module+item names] = Item

        where side is one of rs.c.SIDE
        """
        symmap = {}
        symmap[c.Side.CENTER] = {}
        symmap[c.Side.RIGHT] = {}
        symmap[c.Side.LEFT] = {}

        for rigItem in items:
            if not issubclass(rigItem.__class__, Item):
                try:
                    rigItem = Item.getFromModoItem(rigItem)
                except TypeError:
                    continue
            side = rigItem.side
            key = rigItem.renderNameFromTokens([c.NameToken.MODULE_NAME, c.NameToken.BASE_NAME])
            symmap[side][key] = rigItem

        # Items that are on one side but not on another need to be removed.
        for itemKey in list(symmap[c.Side.RIGHT].keys()):
            if itemKey not in symmap[c.Side.LEFT]:
                del symmap[c.Side.RIGHT][itemKey]

        for itemKey in list(symmap[c.Side.LEFT].keys()):
            if itemKey not in symmap[c.Side.RIGHT]:
                del symmap[c.Side.LEFT][itemKey]

        return symmap

    @classmethod
    def getSymmetricalItem(cls, item, elementsetId):
        """
        Gets first item that is symmetrical to the given item.

        Parameters
        ----------
        item : Item

        elementsetId : str
            Identifier of the element set that will be searched for symmetrical items.

        Returns
        -------
        Item, None
        """
        if item.side not in [c.Side.LEFT, c.Side.RIGHT]:
            return None

        try:
            module = Module(item.moduleRootItem)
        except TypeError:
            return None

        symmetricalItem = None

        itemClass = item.getClass()
        basename = item.name

        symModules = module.symmetryLinkedModules
        for module in symModules:
            modoItems = module.getElementsFromSet(elementsetId)
            for modoItem in modoItems:
                try:
                    rigItem = itemClass(modoItem)
                except TypeError:
                    continue
                if rigItem.name == basename:
                    symmetricalItem = rigItem
                    break
        return symmetricalItem
