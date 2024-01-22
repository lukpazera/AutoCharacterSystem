

import copy
import colorsys

import lx

from . import const as c
from .sys_component import SystemComponent
from .log import log


class PopupIcon(object):
    
    # Width and height of individual colors popup icons.
    COLOR_WIDTH = 48
    COLOR_HEIGHT = 8
    
    # Size of icon used in color schemes popup.
    SCHEME_WIDTH = 32
    SCHEME_HEIGHT = 8

    SAMPLE_WIDTH = 8
    LEFT_MARGIN = 12

    # Shape of color sample that is used in icons.
    MAP = {
    0: (0, 0, 0, 0, 0, 0, 0, 0),
    1: (0, 0, 1, 1, 1, 0, 0, 0),
    2: (0, 1, 1, 1, 1, 1, 0, 0),
    3: (1, 1, 1, 1, 1, 1, 1, 0),
    4: (1, 1, 1, 1, 1, 1, 1, 0),
    5: (1, 1, 1, 1, 1, 1, 1, 0),
    6: (0, 1, 1, 1, 1, 1, 0, 0),
    7: (0, 0, 1, 1, 1, 0, 0, 0),
    }


class ColorAttributes(object):
    """ Attributes used to define a scheme color.
    
    Client needs to intialise dictionary with these attributes as keys
    and subsequently the dictionary is used to initialise color object.
    
    Attributes
    ----------
    IDENTIFIER : str
        Unique identifier for a color. Colors are recognized by identifiers
        so if different schemes use the same identifiers color schemes will
        be compatible - changing scheme will preserve color settings.

    USERNAME : str
        User friendly string that will be used in UI.

    WIRE_COLORS : ColorValues
        Color values object with 1 or 3 colors defined, depending on whether
        defined color is single color or tricolor(see ColorValues docstring
        for more info). Values define wireframe colors for affected items.

    FILL_COLORS : ColorValues, optional
        Same as above but for items fill color.
    """
    IDENTIFIER = 1
    USERNAME = 2
    WIRE_COLORS = 3
    FILL_COLORS = 4


class ColorValues(object):
    """ Defines color values for all 3 sides (right, center, left).
    
    You can either define 3 colors or single color if the item is not
    changing its color when its side changes. In such case - initialise
    center color values only.

    Values should be tuples with 3 float values in 0.0-1.0 range.
    
    Parameters
    ----------
    right : tuple
        Tuple defining color values used for right side items.
    center : tuple
        Tuple defining color values used for centered items (and also
        for right and left sides if these are not defined).
    left : tuple
        Tuple defining color values for left side items.
    """

    @property
    def evalRight(self):
        """ Returns evaluated right side color.
        
        It'll simply be right side color if one is defined and
        center color otherwise.
        
        Returns
        -------
        tuple
        """
        if self.right is not None:
            return self.right
        return self.center

    @property
    def evalLeft(self):
        """ Returns evaluated left side color.
    
        It'll simply be left side color if one is defined and
        center color otherwise.

        Returns
        -------
        tuple
        """
        if self.left is not None:
            return self.left
        return self.center

    @property
    def isDefined(self):
        """ Tests whether this color values object is defined.
        
        Returns
        -------
        bool
            True if any of the values is set.
        """
        return self.right is not None or self.center is not None or self.left is not None
    
    @property
    def isTricolor(self):
        """ Tests if right and left side color values are defined.
        
        Returns
        -------
        bool
        """
        return self.right is not None and self.left is not None

    def applyProcessing(self, hsvFactors=(1.0, 1.0, 1.0), gammaPower=1.0):
        """ Applies HSV processing to all defined colors.
        
        Parameters
        ----------
        hsvFactors : tuple, list
            Either a tuple or a list with hue, saturation and value factors.
            Colors will be multiplied by these factors.
            Using HSV factors you can change hue, saturation and/or value of colors.
        """
        saturationFactor = hsvFactors[1]
        brightnessFactor = hsvFactors[2]

        if saturationFactor == 1.0 and brightnessFactor == 1.0 and gammaPower == 1.0:
            return

        if self.right is not None:
            hsv = list(colorsys.rgb_to_hsv(self.right[0], self.right[1], self.right[2]))
            hsv[1] *= saturationFactor
            hsv[2] *= brightnessFactor
            self.right = list(colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2]))
            self.right[0] = pow(self.right[0], gammaPower)
            self.right[1] = pow(self.right[1], gammaPower)
            self.right[2] = pow(self.right[2], gammaPower)
        if self.center is not None:
            hsv = list(colorsys.rgb_to_hsv(self.center[0], self.center[1], self.center[2]))
            hsv[1] *= saturationFactor
            hsv[2] *= brightnessFactor
            self.center = list(colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2]))
            self.center[0] = pow(self.center[0], gammaPower)
            self.center[1] = pow(self.center[1], gammaPower)
            self.center[2] = pow(self.center[2], gammaPower)
        if self.left is not None:
            hsv = list(colorsys.rgb_to_hsv(self.left[0], self.left[1], self.left[2]))
            hsv[1] *= saturationFactor
            hsv[2] *= brightnessFactor
            self.left = list(colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2]))
            self.left[0] = pow(self.left[0], gammaPower)
            self.left[1] = pow(self.left[1], gammaPower)
            self.left[2] = pow(self.left[2], gammaPower)

    # -------- Private methods
        
    def __init__(self, right=None, center=None, left=None):
        self.right = right
        self.center = center
        self.left = left


class Color(object):
    """ Defines a single color in a color scheme.
    
    Parameters
    ----------
    colorDefinition : dict
        Color is initialised from a dictionary of color attributes such as:
        colorDefinition = {Color.Attr.identifier : 'controllerColor'}
        See ColorAttributes docstring for a list of attributes and type of
        values they should have.
    
    hsvFactors : tuple, list of 3 floats
        All color values will be multiplied by factors in the hsvFactors tuple or list.
        The 3 floats are: hue factor, saturation factor and value factor.
    
    Attributes
    ----------
    identifier : str
        Unique identifier of a color within the color scheme.
        
    username : str
        User friendly name of a color to show in UI.
    """

    Attributes = ColorAttributes

    @property
    def isTricolor(self):
        """ Tests whether this color is a tricolor one.
        
        Returns
        -------
        bool
        """
        return self.wire.isDefined and self.wire.isTricolor

    @property
    def wire(self):
        """ Gets color values for the wireframe (tri)color.
        
        Returns
        -------
        ColorValues
        """
        return self._wire
    
    @property
    def fill(self):
        """ Gets color values for the fill (tri)color.
    
        Returns
        -------
        ColorValues
        """
        return self._fill

    # -------- Private methods

    def __init__(self, colorDefinition, hsvFactors=(1.0, 1.0, 1.0), gammaPower=1.0):
        try:
            self.identifier = colorDefinition[self.Attributes.IDENTIFIER]
            self.username = colorDefinition[self.Attributes.USERNAME]
        except KeyError:
            raise TypeError
        
        self._wire = ColorValues()
        self._fill = ColorValues()
        
        try:
            self._wire = copy.copy(colorDefinition[self.Attributes.WIRE_COLORS])
        except KeyError:
            pass
        else:
            self._wire.applyProcessing(hsvFactors, gammaPower)

        try:
            self._fill = copy.copy(colorDefinition[self.Attributes.FILL_COLORS])
        except KeyError:
            pass
        else:
            self._fill.applyProcessing(hsvFactors, gammaPower)

        self.iconImage = None

    def __eq__(self, other):
        if isinstance(other, Color):
            return self.identifier == other.identifier
        elif isinstance(other, str):
            return self.identifier == other
        return False


class ColorScheme(SystemComponent):
    """ Defines a color scheme to use across the rig.
    
    All the icons required for representing color scheme get generated
    when ColorScheme class is instantiated.
    
    Attributes
    ----------
    descSchemeIconColorRight : tuple
        Tuple of 3 floats in range 0.0-1.0 that defines the color for right
        side swatch in the color scheme icon.
    
    descSaturationFactor : float
        A multiplier for saturation for all the colors in the scheme.
        Using saturation factor you can easily boost or take down saturation across
        entire scheme.

    descBrightnessFactor : float
        A multiplier for brightness for all the colors in the scheme.
        Using brightness factor you can easily increase or decrease brightness of
        entire color scheme.
    """

    Icon = PopupIcon

    # -------- Description Attributes
    
    descIdentifier = ''
    descUsername = ''
    descColors = []
    descSaturationFactor = 1.0
    descBrightnessFactor = 1.0
    descGammaPower = 1.0

    descSchemeIconColorRight = (1, 0 ,0)
    descSchemeIconColorLeft = (0, 0, 1)

    # -------- System Component
    
    @classmethod
    def sysType(cls):
        return c.SystemComponentType.COLOR_SCHEME

    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
    
    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Color Scheme'
    
    @classmethod
    def sysSingleton(cls):
        """ Sets color scheme as singleton.
        
        Singleton system components get instantiated upon registering.
        This is required for color schemes as they need to generate all the icons
        before they can be used properly.
        """
        return True
    
    # -------- Public methods

    @property
    def iconImage(self):
        return self._schemeIconImage

    @property
    def colors(self):
        """ Returns list of colors.
        """
        return self._colors

    def getColorByIndex(self, index):
        """ Gets color by its index in the scheme.
        
        Returns
        -------
        Color
        
        Raises
        ------
        IndexError
            When bad index was passed.
        """
        try:
            return self._colors[index]
        except IndexError:
            pass
        raise IndexError
            
    # ---- Private methods
    
    def _renderSchemeIcon(self):
        """ Renders main scheme icon.
        
        This icon is used in the color schemes popup in main rig properties.
        
        Returns
        -------
        lx.object.Image
        """
        iconImage = self._imageService.Create(PopupIcon.SCHEME_WIDTH, PopupIcon.SCHEME_HEIGHT, lx.symbol.iIMP_RGBAFP, 0)
        iconImageWrite = lx.object.ImageWrite(iconImage)
        
        iconColor = ColorValues(left=self.descSchemeIconColorLeft, right=self.descSchemeIconColorRight)
        iconColor.applyProcessing(self._hsvFactors, self.descGammaPower)
        
        self._clearIconImage(iconImageWrite, PopupIcon.SCHEME_WIDTH, PopupIcon.SCHEME_HEIGHT)
        self._renderColorSample(iconImageWrite, iconColor.right, 10)
        self._renderColorSample(iconImageWrite, iconColor.left, 17)

        return iconImage
    
    def _initColors(self):
        """ Initialises colors list from color definitions.
        """
        self._colors = []
        for colorDefinition in self.descColors:
            self._colors.append(Color(colorDefinition, self._hsvFactors, self.descGammaPower))

    def _renderColorIcons(self):
        """ Renders icon image for each color in the scheme.
        
        Color is taken from wireframe color values by default unless
        fill color values are defined - then fill color values are taken.
        """
        for color in self.colors:
            colorValues = color.wire

            if color.fill.isDefined:
                colorValues = color.fill
                
            if not colorValues.isDefined:
                continue

            color.iconImage = self._renderColorIconImage(colorValues.right, colorValues.center, colorValues.left)

    def _clearIconImage(self, iconImageWrite, width, height):
        """ Clears existing icon image to contain black and transparent pixels.
        
        Parameters
        ----------
        iconImageWrite : lx.object.ImageWrite
            Image to clear, editable interface version.
            
        width : int
            Width of pixels to clear.
            
        height : int
            Height of pixels to clear.
        """
        emptyPixel = lx.object.storage()
        emptyPixel.setType('f')
        emptyPixel.setSize(4)
        emptyPixel.set((0.0, 0.0, 0.0, 0.0))

        for row in range(height):
            for column in range(width):
                iconImageWrite.SetPixel(column, row, lx.symbol.iIMP_RGBAFP, emptyPixel)

    def _renderColorIconImage(self, rightColorTuple, centerColorTuple, leftColorTuple):
        """ Renders new icon image.
        
        The icon will have up to 3 color samples placed next to each other.
        Samples can be set to None to skip them during rendering.
        
        Paramters
        ---------
        rightColorTuple : tuple of 3 float values
            Color to use as right side color in the icon.
            
        centerColorTuple : tuple of 3 float values
            Color to use as center (no side) color in the icon.
        
        leftColorTuple : tuple of 3 float values
            Color to use as left side color in the icon.

        Returns
        -------
        iconImage : lx.object.Image
        """
        iconImage = self._imageService.Create(PopupIcon.COLOR_WIDTH, PopupIcon.COLOR_HEIGHT, lx.symbol.iIMP_RGBAFP, 0)
        iconImageWrite = lx.object.ImageWrite(iconImage)

        self._clearIconImage(iconImageWrite, PopupIcon.COLOR_WIDTH, PopupIcon.COLOR_HEIGHT)
        self._renderColorSample(iconImageWrite, rightColorTuple, PopupIcon.LEFT_MARGIN)
        self._renderColorSample(iconImageWrite, centerColorTuple, PopupIcon.LEFT_MARGIN + 10)
        self._renderColorSample(iconImageWrite, leftColorTuple, PopupIcon.LEFT_MARGIN + 20)

        return iconImage

    def _renderColorSample(self, iconImageWrite, colorTuple, leftMargin):
        """ Renders single color sample to the given image.
        
        Parameters
        ----------
        iconImageWrite : lx.object.ImageWrite
            Editable image to render color sample to.
        
        colorTuple : tuple of 3 float values
            Color of the rendered sample.
            
        leftMargin : int
            Offset in pixels from image's left side where the sample will be rendered.
        """
        if colorTuple is None:
            return

        pixel = lx.object.storage()
        pixel.setType('f')
        pixel.setSize(4)
        
        r = (colorTuple[0])
        g = (colorTuple[1])
        b = (colorTuple[2])
        a = 1.0
        pixel.set((r, g, b, a))

        for row in range(PopupIcon.COLOR_HEIGHT):
            for column in range(PopupIcon.SAMPLE_WIDTH):
                pixelValue = PopupIcon.MAP[row][column]
                if pixelValue <= 0:
                    continue
                iconImageWrite.SetPixel(column + leftMargin, row, lx.symbol.iIMP_RGBAFP, pixel)

    def _initHSVFactors(self):
        hsvf = [1.0, 1.0, 1.0]
        hsvf[1] = self.descSaturationFactor
        hsvf[2] = self.descBrightnessFactor
        return hsvf
        
    def __init__(self):
        self._imageService = lx.service.Image()
        self._colors = []
        self._iconImages = []
        self._hsvFactors = self._initHSVFactors()
        self._schemeIconImage = self._renderSchemeIcon()
        self._initColors()
        self._renderColorIcons()
    
    def __eq__(self, other):
        if isinstance(other, ColorScheme):
            return self.descIdentifier == other.descIdentifier
        elif isinstance(other, str):
            return self.descIdentifier == other
        return False

    def __getitem__(self, key):
        for col in self.colors:
            if col.identifier == key:
                return col
        raise LookupError