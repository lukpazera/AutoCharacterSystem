

import lx
import modo
import modox

from . import preset
from . import const as c
from .preset_thumb import PresetThumbnail
from .item_features.controller_guide import ControllerGuideItemFeature
from .rig_size_op import RigSizeOperator
from .shape_op import ShapesOperator


class GuidePresetThumbnail(PresetThumbnail):
    
    descIdentifier = 'guide'
    descUsername = 'Guide'
    descWindowLayout = 'rs_SaveGuideThumb_Layout'
    descWindowTitle = 'Save Guide'
    descButtonName = 'Save Guide'


class GuidePreset(preset.Preset):

    _REFERENCE_SIZE_SETTING = 'refsize'

    descIdentifier = 'guide'
    descUsername = 'Guide'
    descValuesType = preset.Preset.ValuesType.STATIC
    descSourceAction = lx.symbol.s_ACTIONLAYER_EDIT
    descTargetAction = lx.symbol.s_ACTIONLAYER_SETUP
    descPresetDescription = 'ACS Guide'
    descThumbnailClass = GuidePresetThumbnail
    descContext = c.Context.GUIDE

    @property
    def channels(self):
        guidesElementSet = self.rig[c.ElementSetType.CONTROLLER_GUIDES]
        ctrls = guidesElementSet.elements
        channels = []
        for ctrlModoItem in ctrls:
            try:
                ctrl = ControllerGuideItemFeature(ctrlModoItem)
            except TypeError:
                continue
            channels.extend(ctrl.editChannels)
        return channels
    
    @property
    def descSettings(self):
        refSize = RigSizeOperator(self.rig).referenceSize
        return {self._REFERENCE_SIZE_SETTING: refSize}

    def postLoad(self, settings={}):
        # After guide preset is loaded rig reference size needs to be set.
        # The setting was saved with guide preset so it's reapplied here.
        # All shapes drawing is scaled accordingly.
        try:
            refSize = settings[self._REFERENCE_SIZE_SETTING]
        except KeyError:
            return

        sizeOp = RigSizeOperator(self.rig)
        currentRefSize = sizeOp.referenceSize\

        drawingSizeFactor = refSize / currentRefSize

        sizeOp.referenceSize = refSize
        ShapesOperator(self.rig).applyScaleFactor(drawingSizeFactor)