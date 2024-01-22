

import lx
import modo
import modox

from . import const as c
from .rig import Rig
from .event_handler import EventHandler
from .const import EventTypes as e


class ShapesOperator(object):
    """ Allows for editing item shapes in the rig.
    
    Parameters
    ----------
    root : Rig, RigRoot, str
        Anything that you can initialise Rig with.
        
    Raises
    ------
    TypeError
        If bad initializer object was passed.
    """

    # Channels that define which shape to use.
    _SHAPE_CHANNEL_SETS = {None: ['drawShape', 'link'],
                           'glItemShape': ['isShape', 'isStyle', 'isAlign', 'isSolid']}

    # Channels that define size, thickness or placement of elements to draw
    _SIZE_CHANNEL_SETS = {'glItemShape': ['isRadius',
                                          'isSize.X', 'isSize.Y', 'isSize.Z',
                                          'isOffset.X', 'isOffset.Y', 'isOffset.Z'],
                          'glLinkShape': ['lsRadius', 'lsWidth', 'lsHeight',
                                         'lsOffsetS', 'lsOffsetE'],
                          'rs.pkg.socket': ['rsskDrawRadius'],
                          'rs.pkg.guide': ['rsgdRadius'],
                          'rs.pkg.itemAxis': ['rsiaWidth', 'rsiaHeight', 'rsiaLength',
                                             'rsiaOffset.X', 'rsiaOffset.Y', 'rsiaOffset.Z',
                                             'rsiaShiftX', 'rsiaShiftY', 'rsiaShiftZ'],
                          'rs.pkg.itemShape': ['rsisWidth', 'rsisThickness', 'rsisRingRadius',
                                              'rsisRectXWidth', 'rsisRectYWidth', 'rsisRectZWidth',
                                              'rsisRectXHeight', 'rsisRectYHeight', 'rsisRectZHeight',
                                              'rsisOffset.X', 'rsisOffset.Y', 'rsisOffset.Z']}



    _ITEM_CHANNEL_SETS = {'widget' : ['size']}

    @property
    def shapeChannels(self):
        """
        Gets all shape channels for all relevant items in the rig.
        This includes all the channels relevant to setting item's shape
        (not just channels the define size of item drawing).

        Returns
        -------
        [modo.Channel]
        """
        items = []
        items.extend(self._rig[c.ElementSetType.CONTROLLERS].elements)
        items.extend(self._rig[c.ElementSetType.BIND_SKELETON].elements)
        items.extend(self._rig[c.ElementSetType.PLUGS].elements)
        items.extend(self._rig[c.ElementSetType.SOCKETS].elements)
        items.extend(self._rig[c.ElementSetType.CONTROLLER_GUIDES].elements)

        idents = [modoItem.id for modoItem in items]

        # Decorators are processed in a different way
        # Since any item can be decorator we need to make sure
        # we are not adding the same item twice, therefore check if decorator
        # is already added by one of previous sets.
        decorators = self._rig[c.ElementSetType.DECORATORS].elements
        for modoItem in decorators:
            if modoItem.id in idents:
                continue
            items.append(modoItem)

        return self._getShapeChannelsForItems(items)

    def applyScaleFactor(self, scaleFactor, module=None):
        """ Applies scale factor to item drawing in entire rig or in single module.
        
        Parameters
        ----------
        scaleFactor : float
        
        module : Module, optional
        """
        if scaleFactor == 1.0:
            return

        self._scaleFactor = scaleFactor
        
        if module is None:
            self._rig.iterateOverHierarchy(self._scaleItemDrawing)
        else:
            module.iterateOverHierarchy(self._scaleItemDrawing)

    def applyScaleFactorToItems(self, items, scaleFactor):
        """
        Applies scale factor to given list of items only.

        Parameters
        ----------
        items : modo.Item

        scaleFactor : float
        """
        self._scaleFactor = scaleFactor
        for modoItem in items:
            self._scaleItemDrawing(modoItem)

    def applyScaleFactorToAssembly(self, assmModoItem, scaleFactor):
        """
        Applies scale factor to given assembly.

        This is iterating through all the assembly items and changing its shape property values.

        Parameters
        ----------
        assmModoItem : modo.Item
            This is the assembly item that needs to be processed.

        scaleFactor : float
        """
        self._scaleFactor = scaleFactor
        modox.Assembly.iterateOverItems(assmModoItem, self._scaleLocatorItemDrawing, includeSubassemblies=True)

    # -------- Private methods

    def _scaleLocatorItemDrawing(self, modoItem):
        if not modox.Item(modoItem.internalItem).isOfXfrmCoreSuperType:
            return
        self._scaleItemDrawing(modoItem)

    def _scaleItemDrawing(self, modoItem):
        itemType = modoItem.type
        if itemType in list(self._ITEM_CHANNEL_SETS.keys()):
            chanNames = self._ITEM_CHANNEL_SETS[itemType]
            self._scaleChannelValues(modoItem, chanNames)
            
        for packageName in list(self._SIZE_CHANNEL_SETS.keys()):
            if not modoItem.internalItem.PackageTest(packageName):
                continue
            self._scaleChannelValues(modoItem, self._SIZE_CHANNEL_SETS[packageName])
    
    def _scaleChannelValues(self, modoItem, channelNames):
        for chanName in channelNames:
            chan = modoItem.channel(chanName)
            if chan is None:
                continue
            v = chan.get(0.0, lx.symbol.s_ACTIONLAYER_EDIT)
            v2 = v * self._scaleFactor
            chan.set(v2, 0.0, False, lx.symbol.s_ACTIONLAYER_EDIT)

    def _getShapeChannelsForItems(self, items):
        chans = []

        for modoItem in items:
            itemType = modoItem.type
            if itemType in list(self._ITEM_CHANNEL_SETS.keys()):
                chanNames = self._ITEM_CHANNEL_SETS[itemType]
                itemChans = [modoItem.channel(name) for name in chanNames]
                chans.extend(itemChans)

            # Get all the channels that influence item shape drawing
            for packageSet in [self._SIZE_CHANNEL_SETS, self._SHAPE_CHANNEL_SETS]:
                for packageName in list(packageSet.keys()):
                    if packageName is not None and not modoItem.internalItem.PackageTest(packageName):
                        continue
                    for chanName in packageSet[packageName]:
                        chan = modoItem.channel(chanName)
                        if chan is None:
                            continue
                        chans.append(chan)

        return chans

    def __init__(self, rigInitializer):
        if isinstance(rigInitializer, Rig):
            self._rig = rigInitializer
        else:
            try:
                self._rig = Rig(rigInitializer)
            except TypeError:
                raise


class ShapesOperatorEventHandler(EventHandler):
    """ Handles events that prompt updating rig shapes.
    """

    descIdentifier = 'shapeop'
    descUsername = 'Shape Operator'

    @property
    def eventCallbacks(self):
        return {e.MODULE_GUIDE_SCALED: self.event_moduleGuideScaled,
                }

    def event_moduleGuideScaled(self, **kwargs):
        """
        Event fired after module is dropped into the scene and before drop action will be applied.
        """
        try:
            module = kwargs['module']
            factor = kwargs['factor']
        except KeyError:
            return

        shapeop = ShapesOperator(module.rigRootItem)
        shapeop.applyScaleFactor(factor, module)