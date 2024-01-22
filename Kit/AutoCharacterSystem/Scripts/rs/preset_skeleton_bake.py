
import lx
import modo
import modox

from . import preset
from . import const as c
from .bind_skel import BindSkeleton


class SkeletonBakePreset(preset.Preset):
    """
    This preset stores export names for bind locators.
    """

    descIdentifier = 'skelbake'
    descUsername = 'Skeleton Bake'
    descValuesType = preset.Preset.ValuesType.STATIC
    descSourceAction = lx.symbol.s_ACTIONLAYER_EDIT
    descTargetAction = lx.symbol.s_ACTIONLAYER_SETUP
    descPresetDescription = 'ACS Skeleton Bake'
    descThumbnailClass = None
    descDefaultThumbnailFilename = 'SkeletonBake.png'
    descContext = None  # no need to change the context

    @property
    def channels(self):
        """
        Channels stored in a preset are export name channels from entire bind skeleton.
        """
        bindSkeleton = BindSkeleton(self.rig)
        channels = []
        for bindLocator in bindSkeleton.items:
            channels.extend(bindLocator.bakeSettingsChannels)

        return channels
