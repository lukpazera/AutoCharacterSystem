
""" Module root item.
"""


import math

import lx
from ..item import Item
from ..const import *


class ModuleRoot(Item):
    
    CHAN_SIDE = 'rsSide'
    CHAN_DROP_ACTION = 'rsDropAction'
    
    _CHAN_FILENAME = "rsFilename"
    _CHAN_SIDE_INV = "rsSideInv"
    _CHAN_FIRST_SIDE = "rsFirstSide"
    _CHAN_SIDE_MIRROR_ANGLE_OFFSET = "rsMAngleOffset"
    _CHAN_SIDE_IS_RIGHT = "rsIsRight"
    _CHAN_SIDE_IS_LEFT = "rsIsLeft"
    _CHAN_IS_MIRRORED = "rsIsMirror"
    _CHAN_SIDE_RIGHT_NEG_FACTOR = "rsRNegFactor"
    _CHAN_SIDE_LEFT_NEG_FACTOR = "rsLNegFactor"
    _CHAN_DEFAULT_THUMBNAIL = "rsDefaultThumb"
    _SIDE_HINT_TO_INT = {Side.CENTER: 0, Side.LEFT: 1, Side.RIGHT: -1}
    
    descType = RigItemType.MODULE_ROOT
    descUsername = 'Module Root Item'
    descModoItemType = 'rs.module'
    descExportModoItemType = 'groupLocator'
    descDefaultName = 'Module'
    descPackages = []
    descSelectable = False
    
    # -------- Public interface

    def onAdd(self, subtype):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor grey')

    # -------- Custom methods

    @property
    def side(self):
        """ Returns module side.
        
        Returns
        -------
        str
            Side is an integer value with text hints.
            A text hint is returned, rs.c.Side.XXX constant.
        """
        return self.getChannelProperty(self.CHAN_SIDE)
    
    @side.setter
    def side(self, side):
        """ Sets new module side.

        Parameters
        ----------
        side : str
            rs.c.Side.XXX constant.
        """
        if side not in [Side.CENTER, Side.LEFT, Side.RIGHT]:
            return False
        
        self.setChannelProperty(self.CHAN_SIDE, side)
        self._setSideExtras(side)

    @property
    def firstSide(self):
        """
        Get module's first side - a side it was built on.

        Returns
        -------
        str
            Side is an integer value with text hints.
            A text hint is returned here, a rs.c.Side.XXX constant.
        """
        return self.getChannelProperty(self._CHAN_FIRST_SIDE)

    @property
    def dropAction(self):
        """ Gets a module drop action as text hint.
        
        Returns
        -------
        str
            One of rs.c.ModuleDropAction constants/hints.
        """
        return self.getChannelProperty(self.CHAN_DROP_ACTION)

    @property
    def filename(self):
        """ Gets filename for module preset.
        
        If this property is set it will be used as filename for module quick save
        and as default filename for save with dialog.
        
        Returns
        -------
        str
        """
        return self.getChannelProperty(self._CHAN_FILENAME)

    @filename.setter
    def filename(self, filename):
        self.setChannelProperty(self._CHAN_FILENAME, filename)

    @property
    def defaultThumbnailName(self):
        return self.getChannelProperty(self._CHAN_DEFAULT_THUMBNAIL)

    @defaultThumbnailName.setter
    def defaultThumbnailName(self, name):
        self.setChannelProperty(self._CHAN_DEFAULT_THUMBNAIL, name)

    # -------- Private methods
    
    def _setSideExtras(self, side):
        """ Sets extra channels that need to update when side is changed.

        Parameters
        ----------
        side : str
        """
        sideInt = self._SIDE_HINT_TO_INT[side]

        # Set inverted side channel
        self.setChannelProperty(self._CHAN_SIDE_INV, sideInt * -1)
        
        angleOffset = 0.0
        onLeft = False
        leftNegFactor = 1

        # Set left side related channels
        if sideInt == SideInt.LEFT:
            onLeft = True
            leftNegFactor = -1

        self.setChannelProperty(self._CHAN_SIDE_IS_LEFT, onLeft)
        self.setChannelProperty(self._CHAN_SIDE_LEFT_NEG_FACTOR, leftNegFactor)

        onRight = False
        rightNegFactor = 1

        if sideInt == SideInt.RIGHT:
            onRight = True
            rightNegFactor = -1
        self.setChannelProperty(self._CHAN_SIDE_IS_RIGHT, onRight)
        self.setChannelProperty(self._CHAN_SIDE_RIGHT_NEG_FACTOR, rightNegFactor)

        angleOffset = 0.0
        isMirrored = False

        if side != Side.CENTER:
            firstSide = self.firstSide  # this gets string hint
            if firstSide != Side.CENTER and firstSide != side:
                angleOffset = math.pi
                isMirrored = True

        self.setChannelProperty(self._CHAN_SIDE_MIRROR_ANGLE_OFFSET, angleOffset)
        self.setChannelProperty(self._CHAN_IS_MIRRORED, isMirrored)
