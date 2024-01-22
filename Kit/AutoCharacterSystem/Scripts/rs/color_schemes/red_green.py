
""" Standard and dark red | green color schemes.
"""


from ..color_scheme import ColorScheme
from ..color_scheme import ColorAttributes as a
from ..color_scheme import ColorValues


# -------- Individual color values

# Controller tricolor 1
from .red_blue import ctrl1WireRight
from .red_blue import ctrl1WireCenter
ctrl1WireLeft = (0.22, 0.6, 0.28)

from .red_blue import ctrl1FillRight
from .red_blue import ctrl1FillCenter
ctrl1FillLeft = (0.42, 0.8, 0.48)

# Controllers single color
from .red_blue import ctrlSingle1
from .red_blue import ctrlSingle2

# Bind joint tricolor
from .red_blue import bindWireRight
from .red_blue import bindWireCenter
bindWireLeft = (0.3, 0.49, 0.35)

from .red_blue import bindFillRight
from .red_blue import  bindFillCenter
bindFillLeft = (0.5, 0.69, 0.54)

# Guide colors
from .red_blue import guide1Fill

# Plug colors
from .red_blue import plugWire
from .red_blue import plugFill

# Socket colors
from .red_blue import socketWire
from .red_blue import socketFill

# Retarget joint
from .red_blue import retargetWire
from .red_blue import retargetFill

# Extra colors
from .red_blue import ikWire

# -------- Scheme Color definitions

primaryWireController = {
a.IDENTIFIER: 'ctrlPrimWire',
a.USERNAME: 'Controller (Tricolor Wireframe)',
a.WIRE_COLORS: ColorValues(ctrl1FillRight, ctrl1FillCenter, ctrl1FillLeft),
}

primarySolidController = {
a.IDENTIFIER: 'ctrlPrimSolid',
a.USERNAME: 'Controller (Tricolor Solid)',
a.WIRE_COLORS: ColorValues(ctrl1WireRight, ctrl1WireCenter, ctrl1WireLeft),
a.FILL_COLORS: ColorValues(ctrl1FillRight, ctrl1FillCenter, ctrl1FillLeft)
}

wireController1 = {
a.IDENTIFIER: 'ctrl1Wire',
a.USERNAME: 'Controller (Wireframe 1)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle1),
}

wireController2 = {
a.IDENTIFIER: 'ctrl2Wire',
a.USERNAME: 'Controller (Wireframe 2)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle2),
}

bindJoint = {
a.IDENTIFIER: 'bindJoint',
a.USERNAME: 'Bind Joint',
a.WIRE_COLORS: ColorValues(bindWireRight, bindWireCenter, bindWireLeft),
a.FILL_COLORS: ColorValues(bindFillRight, bindFillCenter, bindFillLeft)
}

guide1 = {
a.IDENTIFIER: 'guide1',
a.USERNAME: 'Guide (Primary)',
a.WIRE_COLORS: ColorValues(center=guide1Fill),
a.FILL_COLORS: ColorValues(center=guide1Fill)
}

from .red_blue import plug
from .red_blue import socket

retargetJoint = {
a.IDENTIFIER: 'retargetJoint',
a.USERNAME: 'Retarget Joint (Primary)',
a.WIRE_COLORS: ColorValues(center=retargetWire),
a.FILL_COLORS: ColorValues(center=retargetFill)
}

ikMarker = {
a.IDENTIFIER: 'ik',
a.USERNAME: 'IK Chain',
a.WIRE_COLORS: ColorValues(center=ikWire),
}


class RedGreenColorScheme(ColorScheme):
    
    descIdentifier = 'rgstd'
    descUsername = 'Red | Green Standard'
    descSchemeIconColorRight = ctrl1FillRight
    descSchemeIconColorLeft = ctrl1FillLeft
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


class RedGreenDarkerColorScheme(RedGreenColorScheme):
    
    descIdentifier = 'rgdrk'
    descUsername = 'Red | Green Dark'
    descBrightnessFactor = 0.75
    descSaturationFactor = 1.25
