

from collections import OrderedDict

import modo
import modox

from .rig import Rig
from .core import service
from .const import EventTypes as e
from .xfrm_in_mesh import TransformsInMesh
from .item_features.controller_guide import ControllerGuideItemFeature
from .item_features.embed_guide import EmbedGuideFeature
from .item_feature_op import ItemFeatureOperator
from .item_features.item_link import ItemLinkFeature
from .log import log
from .debug import debug
from .module_guide import ModuleGuide
from .debug import debug
from . import const as c


class Guide(object):
    """ Represents guide as a whole.
    
    Main operation on guide is to apply it to the rig.
    
    Parameters
    ----------
    rig : Rig, RigRootItem, modo.Item
        Either rig object or its root rig item or root modo item.
    """

    @classmethod
    def isEditableFast(cls, rigRootItem):
        """ Tests whether guide is editable on a rig.

        Use this classmethod where performance is important.

        Parameters
        ----------
        rigRootItem : RootItem

        Returns
        -------
        bool
        """
        return rigRootItem.settings.get(cls._SETTING_EDIT_GUIDE, True)

    def update(self):
        """ Updates guides themselves.
        
        This is for updating guides which should be mirrors of
        other guides for example. Basically anything that needs to be
        done to a guide behind the scenes after user performed manual
        edits.
        """
        pass
    
    def apply(self, modules=None):
        """ Applies guide to the rig.
        
        Applying guide really is a series of atomic operations.
        In essence, application of a guide sends series of events
        representing subsequent stages of applying guide to the rig.
        All the operations need to be implemented via event handlers.
        
        Parameters
        ----------
        modules : Module, list of Module
            It's possible to apply the guide to chosen modules only.
            Pass either a single module or a list/tuple of modules to
            process. Modules have to belong to the rig the guide object was
            initialised with.
        """
        if debug.output:
            log.out('-------- Apply Guide')
            log.startChildEntries()
        
        setup = modox.SetupMode()
        setup.state = True
        modox.TransformUtils.applyEdit()

        service.events.send(e.ITEM_CHAN_EDIT_BATCH_PRE, rig=self._rig) # This is to unlock channels
        service.events.send(e.GUIDE_APPLY_INIT, rig=self._rig)
        
        if modules is None:
            self._rig.iterateOverItems(self._sendItemScanEvent)
        else:
            if type(modules) not in (list, tuple):
                modules = [modules]
            for module in modules:
                module.iterateOverItems(self._sendItemScanEvent)

        service.events.send(e.GUIDE_APPLY_PRE)
        service.events.send(e.GUIDE_APPLY_DO)
        service.events.send(e.GUIDE_APPLY_POST, rig=self._rig)
        service.events.send(e.GUIDE_APPLY_POST2, rig=self._rig)
        service.events.send(e.ITEM_CHAN_EDIT_BATCH_POST) # This is to lock them again

        if debug.output:
            log.stopChildEntries()

    def setToPosition(self, position, modules=None):
        """ Apply world space offset to the guide.
        
        Note that this method does not apply the guide to the rig automatically.

        Parameters
        ----------
        offset : modo.Vector3
        
        modules : Module, list of Module, optional
        
        Returns
        -------
        True
            When the guide was actually changed, False otherwise.
        """
        if modules is None:
            modules = self._rig.modules.allModules
        else:
            if type(modules) not in (list, tuple):
                modules = [modules]

        result = False
        for module in modules:
            moduleGuide = ModuleGuide(module)
            changed = moduleGuide.setToPosition(position)
            if changed:
                result = True

        return result

    def freezeScale(self):
        """
        Freezes scale on all scaled modules in a guide.
        """
        modules = self._rig.modules.allModules

        factors = []
        moduleGuides = []
        for module in modules:
            moduleGuide = ModuleGuide(module)
            factors.append(moduleGuide.scale)
            moduleGuides.append(moduleGuide)

        for x in range(len(moduleGuides)):
            if factors[x] != 1.0:
                moduleGuides[x].freezeScale(factors[x])

            moduleGuides[x].resetScaleOnNonRoots()

    def applyScaleFactor(self, scaleFactor, modules=None):
        """ Applies scale factor to either entire guide or just module guide.
        
        Parameters
        ----------
        scaleFactor : float
        
        module : Module, list of Module, optional

        Returns
        -------
        bool
            True when scale of the guide was changed.
            This signals that the guide should be updated/applied.
        """
        if modules is None:
            modules = self._rig.modules.allModules
        else:
            if type(modules) not in (list, tuple):
                modules = [modules]
                
        if scaleFactor == 1.0:
            return False
        
        for module in modules:
            moduleGuide = ModuleGuide(module)
            moduleGuide.applyScaleFactor(scaleFactor)
        return True
        
    def embedInMesh(self, meshModoItem):
        """ Embeds guide into a mesh.
        
        Guide has to be controller and it has to have embed guide feature added.
        """
        try:
            xfrmInMesh = TransformsInMesh(meshModoItem)
        except TypeError:
            raise
        
        # Every time we embed we need to clear previous data so there is no clash.
        xfrmInMesh.clearEmbeddedData()

        guides = self._rig.getElements(c.ElementSetType.GUIDES)
        nameTokens = [c.NameToken.MODULE_NAME, c.NameToken.SIDE, c.NameToken.BASE_NAME]

        for modoItem in guides:
            try:
                guideFeature = ControllerGuideItemFeature(modoItem)
            except TypeError:
                continue
            try:
                embedGuideFeature = EmbedGuideFeature(modoItem)
            except TypeError:
                continue
            
            identifier = guideFeature.item.renderNameFromTokens(nameTokens)
            positionSource = embedGuideFeature.positionSource
            if xfrmInMesh.embedItemPosition(modoItem, identifier, positionSource=positionSource):
                if debug.output:
                    log.out('Embedded %s' % identifier)
    
    def setFromMesh(self, meshModoItem):
        """ Extracts and applies guide data from a given mesh.
        """
        try:
            xfrmInMesh = TransformsInMesh(meshModoItem)
        except TypeError:
            raise

        guides = self._getGuidesHierarchy() # Guides HAVE TO BE in hierarchical order!
        nameTokens = [c.NameToken.MODULE_NAME, c.NameToken.SIDE, c.NameToken.BASE_NAME]
        
        itemsToSet = OrderedDict()
        for modoItem in guides:
            try:
                guideFeature = ControllerGuideItemFeature(modoItem)
            except TypeError:
                continue
            identifier = guideFeature.item.renderNameFromTokens(nameTokens)
            itemsToSet[identifier] = modoItem
        
        if itemsToSet:
            xfrmInMesh.readEmbeddedTransforms(itemsToSet)

    def linkGuideTransforms(self, guideFrom, guideTo):
        """
        Links two guides transforms.

        This is not the same as setting the link directly on guide item
        because this is also adding draw transform link item feature to visualize the link.
        Item property doesn't do this.

        Parameters
        ----------
        guideFrom : GuideItem
            The guide that will be linked.

        guideTo : GuideItem
            The driver guide.
        """
        guideFrom.transformLinkedGuide = guideTo

        # Set up link
        itemFeatures = ItemFeatureOperator(guideFrom)
        link = itemFeatures.addFeature(c.ItemFeatureType.DRAW_XFRM_LINK)
        link.linkedItem = guideTo.modoItem
        link.linePattern = ItemLinkFeature.LinePattern.DASH_LONG
        link.lineThickness = 1
        link.enable = True

    def attachGuideToOther(self, guideToAttach, guideTarget):
        """
        Attaches one edit guide's world transform to another edit guide world transform.

        Attached guide is then set to be non-visible and non-selectable
        until it's detached.

        Parameters
        ----------
        guideToAttach : GuideItem

        guideTarget : GuideItem
        """
        guideToAttach.attachTarget = guideTarget
        guideToAttach.setLockFromEdit(True)

    def snapToGround(self, modules=None):
        """
        Snaps all given modules to the ground.

        Parameters
        ----------
        modules : [Module], Module, None
            When None is passed then entire rig will be snapped to ground.
        """

        if modules is None:
            modules = self._rig.modules.allModules

        if type(modules) not in (tuple, list):
            modules = [modules]

        minY = 1000000.0
        modulesToOffset = []
        
        for module in modules:
            # Skip modules that are symmetric to other module, their transforms
            # may be out of date.
            if module.symmetricModule is not None:
                continue
            modGuide = ModuleGuide(module)
            # Skip modules that have no guides!
            if not modGuide.hasControlGuide:
                continue
            # Skip module that is linked to another module that is on the snap to ground list.
            # This avoids double transforms if the module will move anyway because module
            # it's linked to is going to be snapped.
            linkedToModule = modGuide.linkedToModule
            if linkedToModule is not None:
                if linkedToModule in modules:
                    continue

            minV, maxV = modGuide.boundingBox
            if minV.y < minY:
                minY = minV.y
                
            modulesToOffset.append(module)

        yOffset = minY * -1.0
        offset = modo.Vector3(0.0, yOffset, 0.0)

        for module in modulesToOffset:
            ModuleGuide(module).offsetPosition(offset)

    def selfDelete(self, showProgress=True):
        """ Removes entire guide from the rig.
        """
        # No need to delete the guide if it was already deleted.
        if not self.editable:
            return

        allModules = self._rig.modules.allModules
        if showProgress:
            monitor = modox.Monitor(len(allModules) * 2, "Delete Guide")

        # TODO: This should lock the rig from adding more modules to it.
        # Also all module properties should be locked so it's only possible to animate with the rig.

        # CRUCIAL
        # We need to delete the guide in two stages.
        # First is applying guide outputs on all modules.
        # Second is deleting guide assemblies.
        # If applying outputs and deleting assembly is done within same loop
        # bad output values can be applied as they may somehow rely
        # on an already deleted guide assembly.
        # So the safe way is to apply first, to make sure all values are right
        # then delete assemblies.
        for module in allModules:
            moduleGuide = ModuleGuide(module)
            moduleGuide.applyGuideOutputsToRig()
            if showProgress:
                monitor.tick(1)

        for module in allModules:
            moduleGuide = ModuleGuide(module)
            moduleGuide.delete()
            if showProgress:
                monitor.tick(1)

        if showProgress:
            monitor.release()

        self._setEditable(False)

    @property
    def editable(self):
        return self.isEditableFast(self._rig.rootItem)

    # -------- Private methods

    _SETTING_EDIT_GUIDE = 'gdedit'

    def _setEditable(self, state):
        self._rig.rootItem.settings.set(self._SETTING_EDIT_GUIDE, state)

    def _getGuidesHierarchy(self):
        self._guides = []
        self._rig.iterateOverHierarchy(self._testControllerGuide)
        return self._guides
        
    def _testControllerGuide(self, modoItem):
        try:
            ctrl = ControllerGuideItemFeature(modoItem)
        except TypeError:
            return
        self._guides.append(modoItem)

    def _sendItemScanEvent(self, modoItem):
        service.events.send(e.GUIDE_APPLY_ITEM_SCAN, item=modoItem)

    def __init__(self, rig):
        if not isinstance(rig, Rig):
            try:
                rig = Rig(rig)
            except TypeError:
                raise
        if not isinstance(rig, Rig):
            raise TypeError
        self._rig = rig