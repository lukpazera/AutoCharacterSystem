

import lx
import modo
import modox

from .core import service
from .item import Item
from .util import run
from .log import log
from . import const as c
from . import item_feature_op


class ItemUtils(object):
    """ Set of utility functions working on items.
    """

    @classmethod
    def preStandardize(cls, rigItem):
        """
        Calls onStandardize() on item and its features so they can process
        themselves before getting actually standardized.

        Parameters
        ----------
        rigItem : Item
        """
        featureOp = item_feature_op.ItemFeatureOperator(rigItem)
        featureOp.preStandardizeAllFeatures()

        try:
            rigItem.onStandardise()
        except AttributeError:
            pass

    @classmethod
    def standardize(cls, rigItem):
        """ Standardizes the rig item.
        
        This function is placed in item utils because item doesn't have access to its features
        and for standardize to work correctly item features have to be removed from an item first.
        Ideally, the code is rearranged so it's possible to manage item features from item level.
        Standardize can then be moved to Item level.
        
        Parameters
        ----------
        rigItem : Item
        """
        featureOp = item_feature_op.ItemFeatureOperator(rigItem)
        featureOp.standardizeAllFeatures()
        rigItem.standardise()
        
    @classmethod
    def getItemFromModoItem(cls, modoItem):
        """ Gets proper rig item object from standard modo item.
        
        Parameters
        ----------
        modoItem : modo.Item
            modo item that is the basis of the rig item (has its properties added).
        
        Returns
        -------
        RigItem
        
        Raises
        ------
        TypeError
            if modoItem was not recognized to be of any registered rig item type.
        """
        rigItemType = Item._getType(modoItem) # low level, think it through
        if rigItemType is None:
            raise TypeError
        try:
            itemTypeClass = service.systemComponent.get(c.SystemComponentType.ITEM, rigItemType)
        except LookupError:
            raise TypeError
        return itemTypeClass(modoItem)

    @classmethod
    def sortRigItemsByName(cls, rigItems):
        """
        Sorts given list of rig items by name.

        Parameters
        ----------
        rigItems : [Item]

        Returns
        -------
        [Item]
        """
        d = {}
        for rigItem in rigItems:
            d[rigItem.name] = rigItem
        keys = list(d.keys())
        keys.sort()
        return [d[key] for key in keys]

