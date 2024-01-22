

from .item import Item
from .module import Module
from .log import log


class SelectionUtils(object):

    @classmethod
    def getModulesFromItems(cls, items):
        """
        Gets all modules that passed items belong to.

        Parameters
        ----------
        items : [modo.Item], [lxu.object.Item], [Item], modo.Item, lxu.object.Item, Item
        """
        modules = []

        if type(items) not in (list, tuple):
            items = [items]

        for item in items:
            try:
                rigItem = Item.getFromOther(item)
            except TypeError:
                continue
            # It's possible that rig item does not belong to any modules,
            # such as all kinds of meshes for example.
            # So I need to check for that.
            try:
                thisMod = Module(rigItem.moduleRootItem)
            except TypeError:
                continue

            if thisMod not in modules:
                modules.append(thisMod)

        return modules

    @classmethod
    def getItemTypesFromItems(cls, items):
        """
        Gets all rig item types that appear in given list of items.

        Parameters
        ----------
        items : [modo.Item], [lxu.object.Item], [Item], modo.Item, lxu.object.Item, Item
        """
        rigItemTypes = []

        if type(items) not in (list, tuple):
            items = [items]

        for item in items:
            rigItemType = Item.getTypeFromModoItem(item)
            if rigItemType is not None and rigItemType not in rigItemTypes:
                rigItemTypes.append(rigItemType)

        return rigItemTypes

