

import lx
import modo
import modox

from . import const as c
from .module import Module
from .item import Item
from .item_cache import ItemCache
from .items.guide import GuideItem
from .items.guide import ReferenceGuideItem
from .items.module_sub import GuideAssembly
from .item_features.identifier import IdentifierFeature
from .item_features.controller_guide import ControllerGuideItemFeature
from .element_sets.guides import ControllerGuidesElementSet
from .log import log
from .core import service


class ModuleGuide(object):
    """ Module guide allows for operating on various aspects of a guide within module.
    """
    
    _SETTING_REFSIZE = 'gdrefsize'
    
    @property
    def module(self):
        return self._module
    
    @property
    def controllerGuides(self):
        """
        Returns
        -------
        [ControllerGuide] (item feature)
        """
        if self._ctrls is None:
            self._scanGuides()
        return self._ctrls
    
    @property
    def rootControllerGuides(self):
        """ Root controller guides are ones that are direct children of the edit guide folder item.
        
        Returns
        -------
        list of ControllerGuide (item feature)
        """
        if self._rootCtrls is None:
            self._scanGuides()
        return self._rootCtrls

    @property
    def firstRootControllerGuide(self):
        """
        Gets first root controller guide.

        Returns
        -------
        ControllerGuide (item feature), None
        """
        rootCtrls = self.rootControllerGuides
        if not rootCtrls:
            return None
        return rootCtrls[0]

    @property
    def hasControlGuide(self):
        """
        Tests whether this module has any controller guide setup.

        Returns
        -------
        bool
        """
        return self.firstRootControllerGuide is not None

    @property
    def childControllerGuides(self):
        """
        Gets a list of all controller guides apart from root ones.

        Returns
        -------
        list of ControllerGuide (item feature)
        """
        if self._childCtrls is None:
            self._scanGuides()
        return self._childCtrls

    @property
    def editGuideFolder(self):
        """ Gets an item that is the parent of the edit guide setup.
        
        Returns
        -------
        Item
        
        Raises
        ------
        LookupError
        """
        return self._module.getKeyItem(c.KeyItem.EDIT_GUIDE_FOLDER)
    
    @property
    def referenceGuides(self):
        """ Gets a list of reference guides.
        
        Returns
        -------
        list of ReferenceGuideItem
        """
        # WROOONG GETTING REFERENCES HAS TO GO IN HIERARCHICAL ORDER!!!
        # 
        if self._references is None:
            self._scanGuides()
        return self._references
    
    @property
    def guideAssemblies(self):
        """ Returns guide assemblies.
        
        These are assemblies which contain parts of the guide setup.
        
        Returns
        -------
        list of Item
        """
        if self._guideAssms is None:
            self._scanAssemblies()
        return self._guideAssms

    @property
    def isLinked(self):
        """
        Tests whether this module is linked to another one.

        Returns
        -------
        bool
        """
        root = self.firstRootControllerGuide
        if root is None:
            return False
        return root.item.isTransformLinked

    @property
    def linkedToModule(self):
        """
        Gets module this module is linked to.

        Returns
        -------
        Module, None
            None is returned when this module is not linked to any other module.
        """
        root = self.firstRootControllerGuide
        if root is None:
            return None
        guideLinkedTo = root.item.transformLinkedGuide # this gives MODO item
        if guideLinkedTo is None:
            return None
        try:
            guideItem = Item.getFromOther(guideLinkedTo.internalItem)
        except TypeError:
            return None
        try:
            return Module(guideItem.moduleRootItem)
        except TypeError:
            pass
        return None

    def applyGuideOutputsToRig(self):
        """ Applies outputs from guide assemblies to the rig.

        Bakes the links between guide assemblies and the rig in other words.
        This is mandatory to have the rig still working correctly after guide is gone!!!
        So always do this prior to deleting module guide assemblies.
        """
        for assmItem in self.guideAssemblies:
            ItemCache().applyOutputs(assmItem.modoItem)

    def delete(self):
        """ Deletes guide from module.

        NOTE: Be sure to call applyGuideOutputsToRig first
        if you want guide output values to be preserved in the rig!!!

        Can be used to optimise the size of the rig when there's no more need
        for guide readjustments.
        """
        for assmItem in self.guideAssemblies:
            modox.Assembly.delete(assmItem.modoItem)

    @property
    def referenceSize(self):
        return self._module.settings.get(self._SETTING_REFSIZE, c.DefaultValue.REFERENCE_SIZE)
    
    @referenceSize.setter
    def referenceSize(self, value):
        """ Gets/sets reference size of the module.
        
        When module is saved the reference size of the rig it is saved from is stored in the module.
        This is then used to scale the module accordingly when dropping onto another rig that might have
        different reference size.
        
        If module has no reference size set a default value is assumed.
        """
        self._module.settings.set(self._SETTING_REFSIZE, value)

    @property
    def firstRootGuidePosition(self):
        rootGuides = self.rootControllerGuides
        if not rootGuides:
            return False
    
        return modox.LocatorUtils.getItemPosition(rootGuides[0].modoItem)
        
    def offsetPosition(self, offsetVec):
        """ Offsets module guide by given vector in world space.
        
        This simply offsets all the root guides by a given vector.
        
        Paramters
        ---------
        offsetVec : modo.Vector3
        """
        rootGuides = self.rootControllerGuides
        if not rootGuides:
            return False

        # If there are more guides offset them.
        for ctrlGuideFeature in rootGuides:
            loc = modo.LocatorSuperType(ctrlGuideFeature.modoItem.internalItem)
            curPos = modo.Vector3(loc.position.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_SETUP))
            newPos = curPos + offsetVec
            loc.position.set((newPos.x, newPos.y, newPos.z), time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

        return True

    def setToPosition(self, position):
        """ Sets guide to a given position in world space.
        
        Parameters
        ----------
        position : modo.Vector3
            World position to set guide root to.
            If any of components is set to None current position will be used.
            This allows for setting world position in chosen axis only.

        Returns
        -------
        bool
            True when guide position was changed, False otherwise.
        """
        rootGuides = self.rootControllerGuides
        if not rootGuides:
            return False
 
        firstRootGuide = rootGuides[0]
        
        # Get current root position.
        rootLoc = modo.LocatorSuperType(firstRootGuide.modoItem.internalItem)
        rootCurrentPos = modo.Vector3(rootLoc.position.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_EDIT))
        
        # We need to put some constraints on the allowed position of module in 3d space.
        # Center module always lands on X=0.
        if self._module.side == c.Side.CENTER:
            position.x = 0.0
        else:
            # keep module X if it's sided module and x from mouse is 0.
            if position.x == 0.0:
                position.x = rootCurrentPos.x

        # We set position on the first (root) guide and offset positions of all other guides.

        # Set new position for a root
        rootLoc.position.set((position.x, position.y, position.z), time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
        
        offset = position - rootCurrentPos
        
        # If there are more guides offset them.
        # Start from index 1 to skip the first root guide.
        for x in range(1, len(rootGuides), 1):
            loc = modo.LocatorSuperType(rootGuides[x].modoItem.internalItem)
            curPos = modo.Vector3(loc.position.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_SETUP))
            newPos = curPos + offset
            loc.position.set((newPos.x, newPos.y, newPos.z), time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)
            
        return True

    def setSize(self, size, silent=False):
        """ Sets size for the module guide.
        
        It calculates scale factor and applies it.

        Parameters
        ----------
        size : float

        silent : bool
            When True setting module guide size will not send the ModuleGuideScaled event out.
            False is the default so other parts of the rig can be notified about guide scale change.
        """
        refsize = self.referenceSize
        if int(refsize * 1000) == int(size * 1000):
            return
        scaleFactor = size / refsize
        self.applyScaleFactor(scaleFactor)
        self.referenceSize = size
    
    def getScaleFactorFromReferenceSize(self, size):
        """ Calculates scale factor based on given size and module reference size.
        
        Parameters
        ----------
        size : float
        
        Returns
        -------
        float
        """
        refsize = self.referenceSize
        if int(refsize * 1000) == int(size * 1000):
            return 1.0
        return size / refsize

    @property
    def scale(self):
        """
        Gets scale factor for a module guide.

        We assume there is only one root guide and scale of this guide (or its parent space)
        determines the scale factor for entire module guide.

        Returns
        -------
        float
            Scale should always be uniform so this returns single float.
        """
        rootGuide = self.firstRootControllerGuide
        if rootGuide is None:
            return 1.0

        # We assume scale only scaling on Y is allowed to make sure scaling is uniform.
        worldScale = modox.LocatorUtils.getItemWorldScaleVector(rootGuide.modoItem)
        return worldScale.y

    def resetScaleOnNonRoots(self):
        """
        Resets scale on all guides that have scaling enabled and are not root guides.
        A hand guide in biped arm module is an example.
        """
        for ctrlGuide in self.controllerGuides:
            if ctrlGuide.item.isRootGuide:
                continue
            if modox.c.TransformChannels.ScaleY in ctrlGuide.editChannelNames:
                modox.LocatorUtils.setItemScale(ctrlGuide.modoItem,
                                                modo.Vector3(1.0, 1.0, 1.0),
                                                action=lx.symbol.s_ACTIONLAYER_SETUP)

    def freezeScale(self, factor=None):
        """
        Freezes scale on a guide - provided any is applied.

        Note that this works correctly only if all other modules guides are frozen.
        So although this is on module guide level things need to be always frozen
        on entire guide at once. Don't call this function in isolation.
        """
        rootGuide = self.firstRootControllerGuide
        if rootGuide is None:
            return

        if factor is None:
            factor = self.scale

        modox.LocatorUtils.setItemScale(rootGuide.modoItem,
                                        modo.Vector3(1.0, 1.0, 1.0),
                                        action=lx.symbol.s_ACTIONLAYER_SETUP)

        ctrlGuides = self.controllerGuides
        guidesToFreeze = []
        rootGuidesToFreeze = {}

        # This is very convoluted overall but the goal is that we need to scale all
        # regular edit guides by a factor that is this module's world scale.
        # Root guides are exception to this.
        # Root guide transform is scaled only by its parent scale.
        # This way root guide will preserve correct transform relative to its parent
        # (which is a module its linked to) after the parent has its scale frozen too.
        # This is why this method works only if all modules guides are frozen at the same time.
        # Scale will go off otherwise.
        for ctrlGuide in ctrlGuides:
            if not ctrlGuide.item.isRootGuide:
                guidesToFreeze.append(ctrlGuide)
                continue
            # Root guides may or may not need to be frozen.
            # If root guide is not linked - skip it, we do not need to scale its transforms.
            if not ctrlGuide.item.isTransformLinked:
                continue

            # If root guide is transform linked then we need to see if its parent space is scaled.
            # If it is - we have to apply just that scale.
            parentScale = modox.LocatorUtils.getItemParentWorldScaleVector(ctrlGuide.modoItem)
            if parentScale.y == 1.0:
                continue

            # Freeze just the scale
            if parentScale.y in rootGuidesToFreeze:
                rootGuidesToFreeze[parentScale.y].append(ctrlGuide)
            else:
                rootGuidesToFreeze[parentScale.y] =[ctrlGuide]

        # Apply scale to root first.
        # This needs to be done silently as to not send module guide scaled event.
        for factor in rootGuidesToFreeze:
            self._applyScaleFactorToGuides(rootGuidesToFreeze[factor], factor, silent=True)

        # And now apply scale to the rest, this time it's not silent as we do want
        # to send the event out.
        self._applyScaleFactorToGuides(guidesToFreeze, factor)

    def applyScaleFactor(self, factor, silent=False):
        """ Applies given scale factor to the guide.
        
        This goes through all the ctrl guides in a module and scales their local position transforms
        uniformly by a given factor. Has an effect of uniformly scaling the guide up/down
        without using scale.

        Parameters
        ----------
        factor : float

        silent : bool
            When True setting module guide size will not send the ModuleGuideScaled event out.
            False is the default so other parts of the rig can be notified about guide scale change.

        skipRoots : bool
            When True scale factor will not be applied to root controller guides.
            This switch has no effect on roots that have linked transforms though, these
            are always scaled regardless of skipRoots value.
        """
        if factor == 1.0:
            return

        ctrlGuides = self.controllerGuides
        self._applyScaleFactorToGuides(ctrlGuides, factor, silent)

    def _applyScaleFactorToGuides(self, ctrlGuides, factor, silent=False):
        """
        Applies scale factor to given list of guides only.

        Parameters
        ----------
        ctrlGuides : [ControllerGuide]

        factor : float

        silent : bool
            When True - guide scaled event will not be sent out.
        """
        for ctrlGuide in ctrlGuides:

            loc = modo.LocatorSuperType(ctrlGuide.modoItem.internalItem)
            pos = modo.Vector3(loc.position.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_SETUP))
            newPos = pos * factor
            loc.position.set((newPos[0], newPos[1], newPos[2]), time=0.0, key=False, action=lx.symbol.s_ACTIONLAYER_SETUP)

        if not silent:
            service.events.send(c.EventTypes.MODULE_GUIDE_SCALED, module=self.module, factor=factor)

    def snapToGround(self):
        """ Offsets entire module guide to snap its bottom to ground.
        """
        minV, maxV = self.boundingBox
        yOffset = minV.y * -1.0
        offset = modo.Vector3(0.0, yOffset, 0.0)
        self.offsetPosition(offset)

    def setToPositionAndFitToGround(self, position=None):
        """
        Moves guide to a given position and scales it so it rests on ground.

        Note that this works only for positions that are about 0 on Y.

        Parameters
        ----------
        position : modo.Vector3, None
            If you pass None then guide position will not be changed, it will simply
            be scaled to rest on ground.

        Returns
        -------
        float
            Factor by which the guide was scaled to fit it to the ground.
        """
        currentPosition = self.firstRootGuidePosition

        if position is None:
            position = self.firstRootGuidePosition

        y = position.y

        # If Y is below 0 simply rest the module on the ground
        if y <= 0.0:
            self.snapToGround()
            return 1.0 # scale was not changed in any way

        # Take current dimensions of the guide and calculate scale factor based
        # on this and the new expected size (which is really just Y values of the new
        # root position.
        w, h, d = self.dimensions
        scaleFactor = y / h

        self.applyScaleFactor(scaleFactor)
        self.setToPosition(position)

        return scaleFactor

    @property
    def boundingBox(self):
        """ Gets bounding box for the module guide.
        
        Returns
        -------
        modo.Vector3, modo.Vector3
            Min and max bounding box vertices as modo.Vector3
        """
        return self._calculateBoundingBoxCoords()

    @property
    def boundingBoxDiagonalLength(self):
        """
        Gets length of the diagonal of bounding box.
        This could be used to estimate size of the module to compare to other modules.

        Returns
        -------
        float
        """
        min, max = self.boundingBox
        v = max - min
        return v.length()

    @property
    def dimensions(self):
        """ Gets dimensions of the module guide.
        
        Returns
        -------
        3 floats
            width(x), height(y), depth(z)
        """
        minvec, maxvec = self._calculateBoundingBoxCoords()
        return abs(maxvec.x - minvec.x), abs(maxvec.y - minvec.y), abs(maxvec.z - minvec.z)

    # -------- Private methods
        
    def _calculateBoundingBoxCoords(self):
        ctrlset = ControllerGuidesElementSet(self._module.rigRootItem)
        guidesList = ctrlset.getElementsFilteredByModule(self._module)
        if not guidesList:
            return 0, 0, 0
        
        minX = 1000000.0
        maxX = -1000000.0
        minY = 1000000.0
        maxY = -1000000.0
        minZ = 1000000.0
        maxZ = -1000000.0
        
        for guideModoItem in guidesList:
            pos = modox.LocatorUtils.getItemWorldPosition(guideModoItem)
            
            if pos[0] < minX:
                minX = pos[0]
            if pos[0] > maxX:
                maxX = pos[0]
                
            if pos[1] < minY:
                minY = pos[1]
            if pos[1] > maxY:
                maxY = pos[1]

            if pos[2] < minZ:
                minZ = pos[2]
            if pos[2] > maxZ:
                maxZ = pos[2]
        
        return modo.Vector3(minX, minY, minZ), modo.Vector3(maxX, maxY, maxZ)

    def _scanGuides(self):
        """ Scans module in search of guides.
        """
        self._rootCtrls = [] # ControllerGuideItemFeature
        self._ctrls = [] # ControllerGuideItemFeature
        self._childCtrls = [] # ControllerGuideItemFeature
        self._references = [] # ReferenceGuideItem
                
        self._module.iterateOverHierarchy(self._collectGuide)
    
    def _collectGuide(self, modoItem):
        # If it's buffer guide grab it and return.
        try:
            self._references.append(ReferenceGuideItem(modoItem))
            return
        except TypeError:
            pass

        # Skip the item if it doesn't have controller feature added.
        try:
            ctrl = ControllerGuideItemFeature(modoItem)
        except TypeError:
            return
        
        self._ctrls.append(ctrl)
        
        # Check if it's root controller guide.
        # A root guide will be guide that is parented to edit guide folder item.
        parentItem = modoItem.parent
        if parentItem is None:
            return

        try:
            parentRigItem = Item.getFromModoItem(parentItem)
        except TypeError:
            self._childCtrls.append(ctrl)
            return
        
        if parentRigItem.identifier == c.KeyItem.EDIT_GUIDE_FOLDER:
            self._rootCtrls.append(ctrl)
        else:
            self._childCtrls.append(ctrl)

    def _scanAssemblies(self):
        """ Scans module subassemblies in search for all the guide assemblies.
        """
        self._guideAssms = []

        self._module.setup.iterateOverSubassemblies(self._collectGuideAssembly)
    
    def _collectGuideAssembly(self, modoItem):
        try:
            guideAssmItem = GuideAssembly(modoItem)
        except TypeError:
            return
        self._guideAssms.append(guideAssmItem)
        
    def __init__(self, moduleInitializer):
        if not isinstance(moduleInitializer, Module):
            try:
                self._module = Module(moduleInitializer)
            except TypeError:
                raise
        else:
            self._module = moduleInitializer

        self._rootCtrls = None
        self._ctrls = None
        self._childCtrls = None
        self._references = None
        self._guideAssms = None