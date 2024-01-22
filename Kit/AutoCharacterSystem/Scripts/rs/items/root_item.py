
""" Core rig item module.

    Core item stores rig level properties and is a root and a link
    to all other items that build the rig.
"""


import lx
import modo

from .. import const as c
from ..item import Item
from ..core import service
from ..naming_scheme import NamingScheme
from ..color_scheme import ColorScheme
from ..component_setups.rig import RigComponentSetup


class RootPropertyChannels(object):
    CHAN_GAME_EXPORT_FOLDER = 'rsGameExportFolder'


class RootItem(Item):

    PropertyChannels = RootPropertyChannels

    ACCESS_LEVEL_HINT_TO_INT = {'dev': 0, 'edit': 1, 'anim': 2}

    CHAN_NAMING_SCHEME = 'rsNamingScheme'
    CHAN_COLOR_SCHEME = 'rsColorScheme'
    CHAN_ACCESS_LEVEL = 'rsAccessLevel'
    CHAN_SELECTED = 'rsSelected'
    CHAN_REFERENCE_SIZE = 'rsRefSize'
    SETTING_SSET = 'sset'
    SETTING_STRETCH = 'stretch'

    descType = 'rootitem'
    descUsername = 'Root Item'
    descModoItemType = 'rs.root'
    descExportModoItemType = 'groupLocator'
    descDefaultName = 'Rig'
    descPackages = []
    descSelectable = False
    
    @classmethod
    def getFromOther(cls, initObject):
        """ Automatically initialises root item from given object.
        
        Parameters
        ----------
        initObject : RootItem, modo.Item, str
        
        Returns
        -------
        RootItem
        
        Raises
        ------
        TypeError
            When bad initObject was passed.
        """
        if isinstance(initObject, RootItem):
            return initObject

        if isinstance(initObject, str):
            try:
                initObject = modo.Scene().item(initObject)
            except LookupError:
                raise TypeError
        
        try:
            rootItem = RootItem(initObject)
        except TypeError:
            raise TypeError
        return rootItem

    @classmethod
    def testModoItem(cls, modoItem):
        """ Custom base item validity test.
        
        This overrides default testing method to use modo item type
        instead of an item tag.
        """
        if modoItem.type != cls.descModoItemType:
            return False
        return True

    def onAdd(self, subtype):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor white')

    # -------- Custom methods

    @property
    def namingScheme(self):
        """ Returns naming scheme object.
        
        Returns
        -------
        NamingScheme or None
        """
        schemeId = self.getChannelProperty(self.CHAN_NAMING_SCHEME)
        try:
            return service.systemComponent.get(NamingScheme.sysType(), schemeId)
        except LookupError:
            return None
        return None

    @namingScheme.setter
    def namingScheme(self, identifier):
        """ Sets new naming scheme.
        
        Parameters
        ----------
        identifier : NamingScheme or str
            Either string identifier or NamingScheme object for a scheme to be set.
        """
        if isinstance(identifier, NamingScheme):
            identifier = identifier.descIdentifier
        self.setChannelProperty(self.CHAN_NAMING_SCHEME, identifier)
    
    @property
    def colorScheme(self):
        """ Returns color scheme object.

        Returns
        -------
        ColorScheme or None if color scheme is not set.
        """
        schemeId = self.getChannelProperty(self.CHAN_COLOR_SCHEME)
        try:
            return service.systemComponent.get(c.SystemComponentType.COLOR_SCHEME, schemeId)
        except LookupError:
            return None
        return None

    @colorScheme.setter
    def colorScheme(self, identifier):
        """ Sets new color scheme.
        
        Parameters
        ----------
        identifier : ColorScheme or str
            Either string identifier or ColorScheme object itself.
        """
        if isinstance(identifier, ColorScheme):
            identifier = identifier.descIdentifier
        self.setChannelProperty(self.CHAN_COLOR_SCHEME, identifier)

    @property
    def accessLevel(self):
        """ Access level tells what can be done with a rig.
        
        Returns
        -------
        int
            one of Rig.AccessLevel constants.
        """
        # Channel has hints so it returns a string.
        # We need to convert it.
        hint = self.getChannelProperty(self.CHAN_ACCESS_LEVEL)
        conv = {'dev': 0,
                'edit': 1,
                'anim': 2}
        return conv[hint]

    @accessLevel.setter
    def accessLevel(self, level):
        """ Sets access level.
        
        Parameters
        ----------
        level : int, str
            Access level either as int constant (one of Rig.AccessLevel) or
            a hint string.
        """
        if isinstance(level, str):
            try:
                level = self.ACCESS_LEVEL_HINT_TO_INT[level]
            except KeyError:
                return
        self.setChannelProperty(self.CHAN_ACCESS_LEVEL, level)

    @property
    def selected(self):
        return self.getChannelProperty(self.CHAN_SELECTED)

    @selected.setter
    def selected(self, state):
        self.setChannelProperty(self.CHAN_SELECTED, state)

    @property
    def referenceSize(self):
        return self.getChannelProperty(self.CHAN_REFERENCE_SIZE)

    @referenceSize.setter
    def referenceSize(self, size):
        self.setChannelProperty(self.CHAN_REFERENCE_SIZE, size)

    @property
    def componentSetup(self):
        """ Gets component setup that this root item belongs to.
        
        Returns
        -------
        RigComponentSetup, None
        """
        try:
            return RigComponentSetup(self.modoItem)
        except TypeError:
            pass
        return None
    
    @property
    def controllersSet(self):
        return self.settings.get(self.SETTING_SSET, None)
        
    @controllersSet.setter
    def controllersSet(self, selectionSetName):
        """ Gets/sets selection set filter for rig controllers.
        
        Parameters
        ----------
        selectionSetName : str, None
            When selection set is None no filtering based on selection sets will happen.
        """
        if selectionSetName is None:
            self.settings.delete(self.SETTING_SSET)
        else:
            self.settings.set(self.SETTING_SSET, selectionSetName)

    def linkItems(self, items, graphName):
        """ Links given items to root on a given graph.
        
        Parameters
        ----------
        items : list of modo.Item, Item
        
        graphName : str
        """
        if not graphName:
            return

        if type(items) not in (list, tuple):
            items = [items]

        rigRootGraph = self.modoItem.itemGraph(graphName)
        for item in items:
            if issubclass(item.__class__, Item):
                item = item.modoItem
            itemGraph =item.itemGraph(graphName)
            itemGraph >> rigRootGraph
        
    def getLinkedItems(self, graphName):
        """ Gets a list of items linked by a given graph.
        
        Reverse graph connection is assumed as this is how other items
        should get linked to the root item.
        """
        graph = self._modoItem.itemGraph(graphName)
        return graph.reverse()