

import lx
import modo
import modox

from .items.guide import ReferenceGuideItem
from .item_features.guide import GuideItemFeature
from .item_features.controller import ControllerItemFeature
from .log import log
from .util import run
from .debug import debug


class GuideMatcher(object):
    """ Allows for matching items to their guides.
    
    This class presents a set of methods that need to be called
    in right order during guide application process.
    """
    
    DEBUG = debug.output

    def scanItem(self, modoItem):
        """ Tests the item to see if it should be matched to a guide.
        
        This needs to be called for every item in the rig.
        
        Parameters
        ----------
        modoItem : modo.Item
        """
        try:
            bufferGuide = ReferenceGuideItem(modoItem)
        except TypeError:
            pass
        else:
            self._bufferGuides.append(bufferGuide)

        try:
            guideFeature = GuideItemFeature(modoItem)
        except TypeError:
            return
        
        if guideFeature.guide is not None:
            self._guidedItemsFeatures.append(guideFeature)
    
    def match(self):
        """ Performs matching of an item to its guide.
        """
        if self.DEBUG:
            log.out("-------- Match Guided Items to Guide")
            log.startChildEntries()

        local = True
        if local:
            if self.DEBUG:
                log.out('Applying transforms to buffer guides:')
                log.startChildEntries()
            
            # Local matching
            for guideItem in self._bufferGuides:
                modoItem = guideItem.modoItem
                ident = modoItem.id
                if self.DEBUG:
                    log.out('Applying transforms to buffer guide: %s' % modoItem.name)
                run('item.apply pos {%s}' % ident)
                run('item.apply rot {%s}' % ident)

            if self.DEBUG:
                log.stopChildEntries()
                log.out('Copying local transforms from buffer guides:')
                log.startChildEntries()

            zeroVec = modo.Vector3(0.0, 0.0, 0.0)
            for feature in self._guidedItemsFeatures:
                guidedModoItem = feature.modoItem
                
                guideItem = feature.guide
                
                # Local transforms need to be grabbed from edit action because that's where
                # the applied transforms went. It's either that or apply edit first and then
                # get values from setup action.
                pos = modox.LocatorUtils.getItemPosition(guideItem.modoItem, action=lx.symbol.s_ACTIONLAYER_EDIT)
                rot = modox.LocatorUtils.getItemRotation(guideItem.modoItem, action=lx.symbol.s_ACTIONLAYER_EDIT)

                # set either primary or zero positions
                if feature.zeroTransforms:
                    # We have to guarantee that zero transform items are present on the guided item.
                    # So first we set guided transforms on primary transform items
                    # then we zero these transforms - this will create zero transforms if needed.
                    modo.Scene().select(guidedModoItem)
                    if not modox.LocatorUtils.hasZeroPosition(guidedModoItem):
                        modox.LocatorUtils.setItemPosition(guidedModoItem, pos, action=lx.symbol.s_ACTIONLAYER_SETUP)
                        run('transform.zero translation')

                    if not modox.LocatorUtils.hasZeroRotation(guidedModoItem):
                        modox.LocatorUtils.setItemRotation(guidedModoItem, rot, action=lx.symbol.s_ACTIONLAYER_SETUP)
                        run('transform.zero rotation')

                    # This is crucial. We have to guarantee that the zero transform rotation order and reference guide
                    # transform rotation order are the same.
                    # If they are different the zeroed transforms will be translated wrong when taken from
                    # zeroed out primary transform.
                    # For this reason we set zero rotation to exact same values as on the reference guide manually
                    # (knowing that zero rotation now exists for sure) and then we also make sure the zero transform
                    # rotation order is the same as in the reference guide.

                    # Note that it's not guaranteed zero transforms will be in place here
                    # because if the matched transforms are zero vectors MODO will not create zero transforms.
                    # So I still need to check that zero transforms exist.
                    if modox.LocatorUtils.hasZeroPosition(guidedModoItem):
                        modox.LocatorUtils.setZeroPosition(guidedModoItem, pos, action=lx.symbol.s_ACTIONLAYER_SETUP)
                    if modox.LocatorUtils.hasZeroRotation(guidedModoItem):
                        modox.LocatorUtils.setZeroRotation(guidedModoItem, rot, action=lx.symbol.s_ACTIONLAYER_SETUP)
                        order = modox.LocatorUtils.getPrimaryRotationOrder(guideItem.modoItem)
                        modox.LocatorUtils.setZeroRotationOrder(guidedModoItem, order)
                else:
                    modox.LocatorUtils.setItemPosition(guidedModoItem, pos, action=lx.symbol.s_ACTIONLAYER_SETUP)
                    modox.LocatorUtils.setItemRotation(guidedModoItem, rot, action=lx.symbol.s_ACTIONLAYER_SETUP)

                if self.DEBUG:
                    log.out('Transforms copied: %s ---> %s' % (guideItem.modoItem.name, guidedModoItem.name))

            if self.DEBUG:
                log.stopChildEntries()
        else:
            
            # World matching
            # Cache world transforms of the guide first.
            if self.DEBUG:
                log.out('Applying transforms to buffer guides:')
                log.startChildEntries()
            
            bufGuides = {}
            for guideItem in self._bufferGuides:
                wpos = modox.LocatorUtils.getItemWorldPositionVector(guideItem.modoItem)
                wrotm3 = modox.LocatorUtils.getItemWorldRotation(guideItem.modoItem)
                bufGuides[guideItem.modoItem.id] = [wpos, wrotm3]

            for feature in self._guidedItemsFeatures:
                guidedModoItem = feature.modoItem
                
                guideItem = feature.guide
                refGuideIdent = guideItem.modoItem.id
                
                # World transforms
                try:
                    xfrms = bufGuides[refGuideIdent]
                except KeyError:
                    if self.DEBUG:
                        log.out('BAD GUIDE REF')
                    continue
                
                #modox.TransformUtils.applyTransform(guidedModoItem,
                                                    #xfrms[0], 
                                                    #xfrms[1],
                                                    #mode=lx.symbol.iLOCATOR_WORLD,
                                                    #action=lx.symbol.s_ACTIONLAYER_SETUP)
                lx.eval('item.match item pos item:%s itemTo:%s' % (guidedModoItem.id, refGuideIdent))
                lx.eval('item.match item rot item:%s itemTo:%s' % (guidedModoItem.id, refGuideIdent))

                if self.DEBUG:
                    log.out('World transforms applied: %s ---> %s' % (guideItem.modoItem.name, guidedModoItem.name))

        if self.DEBUG:
            log.stopChildEntries()

    def post(self):
        """ Call when matching is complete.
        """
        self._updateRestValues()
        self._cleanUp()

    # -------- Private methods

    def _zeroTransforms(self):
        """
        Zeroing transforms for all items that have Zero Transforms on in guide reference feature properties.

        ********************************************************************************
        THIS WAS CALLED FROM post() AS FIRST FUNCTION BUT IT'S NOT USED ANYMORE!
        WE ARE NOW MATCHING TRANSFORMS DIRECTLY TO ZERO TRANSFORMS
        TO AVOID ISSUES WHEN MAIN AND ZERO TRANSFORMS HAVE DIFFERENT ROTATION ORDER!!!
        ********************************************************************************
        """
        if self.DEBUG:
            log.out("Zero transforms for items:")
            log.startChildEntries()
        selection = [feature.modoItem for feature in self._guidedItemsFeatures if feature.zeroTransforms]
        if not selection:
            return
        
        zeroVec = modo.Vector3()
        for modoItem in selection:
            if self.DEBUG:
                log.out(modoItem.name)
            modox.LocatorUtils.setZeroPosition(modoItem, zeroVec, action=lx.symbol.s_ACTIONLAYER_SETUP)
            modox.LocatorUtils.setZeroRotation(modoItem, zeroVec, action=lx.symbol.s_ACTIONLAYER_SETUP)

        modo.Scene().select(selection)
        lx.eval('!transform.zero')

        if self.DEBUG:
            log.stopChildEntries()

    def _updateRestValues(self):
        for feature in self._guidedItemsFeatures:
            modoItem = feature.modoItem
            try:
                controller = ControllerItemFeature(modoItem)
            except TypeError:
                continue
            controller.updateRestValues()

    def _cleanUp(self):
        del self._guidedItemsFeatures
        del self._bufferGuides
        
    def _initData(self):
        self._guidedItemsFeatures = []
        self._bufferGuides = [] # GuideItem list

    def _debugOutput(self, modoItem, guideModoItem):
        scene = modo.Scene()

        pwpos = modox.LocatorUtils.getItemParentWorldPosition(modoItem)
        pwrot = modox.LocatorUtils.getItemParentWorldOrientation(modoItem)
        
        newItem = scene.addItem('locator', modoItem.name + ' PARENT SPACE LOC')
        modox.TransformUtils.applyTransform(newItem, modo.Vector3(pwpos), pwrot)

    def __init__(self):
        self._initData()
