
""" Standard and drak red | blue color schemes.
"""


from ..color_scheme import ColorScheme
from ..color_scheme import ColorAttributes as a
from ..color_scheme import ColorValues


# -------- Individual color values

# Controller tricolor 1
ctrl1WireRight = (0.7, 0.2, 0.29) # red
ctrl1WireCenter = (0.6, 0.6, 0.6) # light grey
ctrl1WireLeft = (0.2, 0.37, 0.71) # blue

ctrl1FillRight = (0.9, 0.4, 0.49)
ctrl1FillCenter = (0.8, 0.8, 0.8)
ctrl1FillLeft = (0.4, 0.57, 0.91)

ctrl1FillRightV = (0.9, 0.05, 0.13) # vivid red
ctrl1FillCenterV = (0.2, 0.64, 0.17) # vivid light green
ctrl1FillLeftV = (0.0, 0.71, 0.98) # vivid blue

# Controllers single color
ctrlSingle1 = (0.7, 0.7, 0.7) # Light Grey
ctrlSingle2 = (0.85, 0.85, 0.55) # pale yellow
ctrlSingle3 = (.68, 1.0, .73) # pale green
ctrlSingle4 = (.33, .87, .8) # cyan
ctrlSingle5 = (1.00, 0.8, 0.05) # yellow
ctrlSingle6 = (0.5, 1.0, 0.31) # green
ctrlSingle7 = (0.9, 0.9, 0.9) # White

ctrlSingle1V = ctrl1FillCenterV
ctrlSingle2V = ctrl1FillCenterV

# Bind joint tricolor
bindWireRight = (0.55, 0.33, 0.38) 
bindWireCenter = (0.35, 0.5, 0.5)
bindWireLeft = (0.25, 0.35, 0.55)

bindFillRight = (0.75, 0.5, 0.58)
bindFillCenter = (0.66, 0.7, 0.7)
bindFillLeft = (0.49, 0.55, 0.75)

bindFillRightV = (1.0, 0.31, 0.5)
bindFillCenterV = (0.37, 0.78, 0.7)
bindFillLeftV = (0.38, 0.5, 1.0)

# Guide colors
guide0Fill = (1.00, 0.26, 0.70) # root
guide1Fill = (0.75, 0.35, 0.98) # purple
guide2Fill = (0.25, 0.45, 0.85) # blue
guide3Fill = (0.24, 0.67, 0.76) # cyan

# Plug
plugWire = (1.0, 0.21, 0.21)
plugFill = plugWire

# Socket
socketWire = (0.21, 0.6, 1.0)
socketFill = socketWire

# Retarget joint
retargetWire = (0.23, 0.38, 0.6)
retargetFill = (0.21, 0.58, 0.7)

# Extra colors
ikWire = (0.44, 0.72, 0.73)

# -------- Scheme Color definitions

primaryWireController = {
a.IDENTIFIER: 'ctrlPrimWire',
a.USERNAME: 'Controller (Tricolor Wireframe)',
a.WIRE_COLORS: ColorValues(ctrl1FillRight, ctrl1FillCenter, ctrl1FillLeft),
}

primarySolidController = {
a.IDENTIFIER: 'ctrlPrimSolid',
a.USERNAME: 'Controller (Tricolor Solid)',
a.WIRE_COLORS: ColorValues(ctrl1FillRight, ctrl1FillCenter, ctrl1FillLeft),
a.FILL_COLORS: ColorValues(ctrl1FillRight, ctrl1FillCenter, ctrl1FillLeft)
}

# Light grey
wireController1 = {
a.IDENTIFIER: 'ctrl1Wire',
a.USERNAME: 'Controller (Light Grey)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle1),
a.FILL_COLORS: ColorValues(center=ctrlSingle1),
}

# Pale yellow
wireController2 = {
a.IDENTIFIER: 'ctrl2Wire',
a.USERNAME: 'Controller (Pale Yellow)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle2),
a.FILL_COLORS: ColorValues(center=ctrlSingle2),
}

# Pale Green
wireController3 = {
a.IDENTIFIER: 'ctrl3Wire',
a.USERNAME: 'Controller (Pale Green)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle3),
}

# Cyan
wireController4 = {
a.IDENTIFIER: 'ctrl4Wire',
a.USERNAME: 'Controller (Cyan)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle4),
}

# Yellow
wireController5 = {
a.IDENTIFIER: 'ctrl5Wire',
a.USERNAME: 'Controller (Yellow)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle5),
}

# Green
wireController6 = {
a.IDENTIFIER: 'ctrl6Wire',
a.USERNAME: 'Controller (Green)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle6),
}

# Cyan
wireController7 = {
a.IDENTIFIER: 'ctrl7Wire',
a.USERNAME: 'Controller (White)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle7),
}

bindJoint = {
a.IDENTIFIER: 'bindJoint',
a.USERNAME: 'Bind Joint',
a.WIRE_COLORS: ColorValues(bindWireRight, bindWireCenter, bindWireLeft),
a.FILL_COLORS: ColorValues(bindFillRight, bindFillCenter, bindFillLeft)
}

guide0 = {
a.IDENTIFIER: 'guide0',
a.USERNAME: 'Guide (Root)',
a.WIRE_COLORS: ColorValues(center=guide0Fill),
a.FILL_COLORS: ColorValues(center=guide0Fill)
}

guide1 = {
a.IDENTIFIER: 'guide1',
a.USERNAME: 'Guide (Purple)',
a.WIRE_COLORS: ColorValues(center=guide1Fill),
a.FILL_COLORS: ColorValues(center=guide1Fill)
}

guide2 = {
a.IDENTIFIER: 'guide2',
a.USERNAME: 'Guide (Blue)',
a.WIRE_COLORS: ColorValues(center=guide2Fill),
a.FILL_COLORS: ColorValues(center=guide2Fill)
}

guide3 = {
a.IDENTIFIER: 'guide3',
a.USERNAME: 'Guide (Cyan)',
a.WIRE_COLORS: ColorValues(center=guide3Fill),
a.FILL_COLORS: ColorValues(center=guide3Fill)
}

plug = {
a.IDENTIFIER: 'plug',
a.USERNAME: 'Plug',
a.WIRE_COLORS: ColorValues(center=plugWire),
a.FILL_COLORS: ColorValues(center=plugFill)
}

socket = {
a.IDENTIFIER: 'socket',
a.USERNAME: 'Socket',
a.WIRE_COLORS: ColorValues(center=socketWire),
a.FILL_COLORS: ColorValues(center=socketFill)}

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


class RedBlueColorScheme(ColorScheme):
    
    descIdentifier = 'rbstd'
    descUsername = 'Red | Blue Standard'
    descSchemeIconColorRight = ctrl1FillRight
    descSchemeIconColorLeft = ctrl1FillLeft
    descColors = [primaryWireController,
                  primarySolidController,
                  wireController1,
                  wireController7,
                  wireController2,
                  wireController5,
                  wireController3,
                  wireController6,
                  wireController4,
                  bindJoint,
                  guide0,
                  guide1,
                  guide2,
                  guide3,
                  plug,
                  socket,
                  retargetJoint,
                  ikMarker]


class RedBlueDarkerColorScheme(RedBlueColorScheme):
    
    descIdentifier = 'rbdrk'
    descUsername = 'Red | Blue (AVP)'
    descBrightnessFactor = 1.0
    descSaturationFactor = 1.0
    descGammaPower = 1.6


primaryWireControllerV = {
a.IDENTIFIER: 'ctrlPrimWire',
a.USERNAME: 'Controller (Tricolor Wireframe)',
a.WIRE_COLORS: ColorValues(ctrl1FillRightV, ctrl1FillCenterV, ctrl1FillLeftV),
}

primarySolidControllerV = {
a.IDENTIFIER: 'ctrlPrimSolid',
a.USERNAME: 'Controller (Tricolor Solid)',
a.WIRE_COLORS: ColorValues(ctrl1FillRightV, ctrl1FillCenterV, ctrl1FillLeftV),
a.FILL_COLORS: ColorValues(ctrl1FillRightV, ctrl1FillCenterV, ctrl1FillLeftV)
}

wireController1V = {
a.IDENTIFIER: 'ctrl1Wire',
a.USERNAME: 'Controller (Wireframe 1)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle1V),
}

wireController2V = {
a.IDENTIFIER: 'ctrl2Wire',
a.USERNAME: 'Controller (Wireframe 2)',
a.WIRE_COLORS: ColorValues(center=ctrlSingle2V),
}

bindJointV = {
a.IDENTIFIER: 'bindJoint',
a.USERNAME: 'Bind Joint',
a.WIRE_COLORS: ColorValues(bindWireRight, bindWireCenter, bindWireLeft),
a.FILL_COLORS: ColorValues(bindFillRightV, bindFillCenterV, bindFillLeftV)
}

class RedBlueVividColorScheme(RedBlueColorScheme):
    
    descIdentifier = 'rbvvd'
    descUsername = 'Red | Blue Vivid'

    descSchemeIconColorRight = ctrl1FillRightV
    descSchemeIconColorLeft = ctrl1FillLeftV
    descColors = [primaryWireControllerV,
                  primarySolidControllerV,
                  wireController1V,
                  wireController2V,
                  bindJointV,
                  guide0,
                  guide1,
                  guide2,
                  guide3,
                  plug,
                  socket,
                  retargetJoint,
                  ikMarker]
