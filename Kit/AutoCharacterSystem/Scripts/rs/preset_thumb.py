
""" Preset thumbnail module.
"""

import os.path

import lx
from . import const as c
from .core import service
from .log import log as log
from . import sys_component


class PresetThumbnail(sys_component.SystemComponent):
    """ This class is used to grab and set GL thumbnails for presets.
    """

    descIdentifier = ''
    descUsername = ''
    descWindowLayout = ''
    descWindowTitle = ''
    descButtonName = ''
    descThumbViewportTag = 'rsGlThumbCaptureView'
    descThumbWidth = 512
    descThumbHeight = 512
    descHorizontalMargin = 0
    descVerticalMargin = 55
    
    PATH = service.path[c.Path.TEMP_FILES]
    CAPTURE_FILENAME = os.path.join(PATH, 'thumb.png')
    
    # -------- System Component
    
    @classmethod
    def sysType(cls):
        return c.SystemComponentType.PRESET_THUMBNAIL

    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
    
    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Preset Thumbnail'
    
    @classmethod
    def sysSingleton(cls):
        return True

    # -------- Public methods

    def openWindow(self):
        """ Toggles UI that contains GL view to grab thumbnail from.
        """
        frameWidth = self.descThumbWidth + self.descHorizontalMargin
        frameHeight = self.descThumbHeight + self.descVerticalMargin
        frameWidth += 8
        frameHeight += 8
        
        cmd = 'layout.createOrClose {rsSaveThumbLayout} {%s} true {%s} width:%d height:%d style:palette'
        lx.eval(cmd % (self.descWindowLayout, self.descWindowTitle, frameWidth, frameHeight))
        
        # What is this for?
        try:
            lx.eval('!view3d.projection psp')
        except RuntimeError:
            pass
    
    def capture(self):
        """ Captures the thumbnail.
        
        The thumbnail is captured to a temp file.
        setOnPreset() needs to be called to apply captured file to a preset.
        """
        # No need to capture the thumb is thumbnail file is set to an existing file.
        if self._thumbFilename != self.CAPTURE_FILENAME:
            return True

        lx.eval('!select.viewportWithTag {%s} anyFrame:true' % self.descThumbViewportTag)
        tag = lx.eval('viewport.tag ?')
    
        if not tag or tag != self.descThumbViewportTag:
            log.out("Viewport capture failed.", log.MSG_ERROR)
            return False
    
        glmeterState = lx.eval('glmeter ?')
        lx.eval('glmeter 0')
        lx.eval('!gl.snapshot {%s} {PNG}' % self.CAPTURE_FILENAME)
        lx.eval('glmeter %d' % glmeterState)
        return True

    def setThumbnailDirectly(self, name):
        """
        Sets thumbnail directly.

        It will be used to find default thumbnail png file in thumbnails path
        and if present will make capturing the thumb redundant.
        Even if capture() is called it won't capture thumbnail if
        thumbnail file is set directly.
        """
        thumbsDefaultPath = service.path[c.Path.THUMBNAILS]
        name += '.png'
        filename = os.path.join(thumbsDefaultPath, name)
        if os.path.isfile(filename):
            self._thumbFilename = filename

    def setOnPreset(self, filename):
        if not os.path.isfile(self._thumbFilename):
            return False

        if not self.setThumbnailImageOnPreset(filename, self._thumbFilename):
            return False

        self._cleanUp()
        
        return True

    @classmethod
    def setThumbnailImageOnPreset(cls, presetFilename, thumbnailFilename):
        """
        Sets thumbnail on a particular preset file.

        Parameters
        ----------
        presetFilename : str
            Full path to preset filename.

        thumbnailFilename : str
            Full path to thumbnail filename
        """
        try:
            lx.eval('!preset.thumbReplace {%s} {%s}' % (presetFilename, thumbnailFilename))
        except RuntimeError:
            return False
        return True

    # -------- Private methods

    def __init__(self):
        self._thumbFilename = self.CAPTURE_FILENAME

    def _cleanUp(self):
        if os.path.isfile(self.CAPTURE_FILENAME):
            os.remove(self.CAPTURE_FILENAME)