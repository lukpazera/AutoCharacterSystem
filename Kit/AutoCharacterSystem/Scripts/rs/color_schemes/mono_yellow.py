
""" Monochromatic yellow color scheme.
"""


from ..color_scheme import ColorScheme
from ..color_scheme import ColorAttributes as a
from ..color_scheme import ColorValues
from .red_blue import *

# -------- Individual color values

yellowMono = (0.88, 0.8, 0.18)
bindWire = (0.6, 0.38, 0.27)
bindFill = (1.0, 0.58, 0.3)

# -------- Scheme Color definitions

primaryWireController = {
a.IDENTIFIER: 'ctrlPrimWire',
a.USERNAME: 'Controller (Tricolor Wireframe)',
a.WIRE_COLORS: ColorValues(yellowMono, yellowMono, yellowMono),
}

primarySolidController = {
a.IDENTIFIER: 'ctrlPrimSolid',
a.USERNAME: 'Controller (Tricolor Solid)',
a.WIRE_COLORS: ColorValues(yellowMono, yellowMono, yellowMono),
a.FILL_COLORS: ColorValues(yellowMono, yellowMono, yellowMono)
}

wireController1 = {
a.IDENTIFIER: 'ctrl1Wire',
a.USERNAME: 'Controller (Wireframe 1)',
a.WIRE_COLORS: ColorValues(center=yellowMono),
}

wireController2 = {
a.IDENTIFIER: 'ctrl2Wire',
a.USERNAME: 'Controller (Wireframe 2)',
a.WIRE_COLORS: ColorValues(center=yellowMono),
}

bindJoint = {
a.IDENTIFIER: 'bindJoint',
a.USERNAME: 'Bind Joint',
a.WIRE_COLORS: ColorValues(bindWire, bindWire, bindWire),
a.FILL_COLORS: ColorValues(bindFill, bindFill, bindFill)
}


class MonoYellowColorScheme(ColorScheme):
    
    descIdentifier = 'ymono'
    descUsername = 'Yellow Mono'
    descSchemeIconColorRight = yellowMono
    descSchemeIconColorLeft = yellowMono
    descColors = [primaryWireController,
                  primarySolidController,
                  wireController1,
                  wireController2,
                  bindJoint,
                  guide1,
                  plug,
                  socket,
                  retargetJoint,
                  ikMarker]

