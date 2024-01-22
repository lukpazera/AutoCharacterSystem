
import lx
import modo
import modox

from . import preset
from . import const as c
from .preset_thumb import PresetThumbnail
from .item_features.controller_guide import ControllerGuideItemFeature
from .shape_op import ShapesOperator


class ShapesPresetThumbnail(PresetThumbnail):

    descIdentifier = 'shapes'
    descUsername = 'Shapes'
    descWindowLayout = 'rs_SaveShapesThumb_Layout'
    descWindowTitle = 'Save Shapes'
    descButtonName = 'Save Shapes'


class ShapesPreset(preset.Preset):
    """
    Shapes preset contains information about locator drawing shapes.
    """

    descIdentifier = 'shapes'
    descUsername = 'Shapes'
    descValuesType = preset.Preset.ValuesType.STATIC
    descSourceAction = lx.symbol.s_ACTIONLAYER_EDIT
    descTargetAction = lx.symbol.s_ACTIONLAYER_SETUP
    descPresetDescription = 'ACS Shapes'
    descThumbnailClass = ShapesPresetThumbnail

    @property
    def channels(self):
        """
        Shapes preset stores shapes for:
        bind skeleton, plugs, sockets, controllers, decorators
        """
        shapeOp = ShapesOperator(self.rig)
        return shapeOp.shapeChannels


