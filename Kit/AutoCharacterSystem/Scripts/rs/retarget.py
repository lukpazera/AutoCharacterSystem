

import os.path
import collections

import lx
import modo
import modox

from .rig import Rig
from .util import run
from .item import Item
from .core import service
from .item_features.controller import ControllerItemFeature
from .log import log


class Retargeting(object):
    """
    Retargeting implementation. Works in tandem with the retargeting module.
    """

    # Lists of matching bvh items need to be all lowercase.
    # We skip hips.
    _RETARGET_MAP = collections.OrderedDict()
    _RETARGET_MAP['CHead_1'] = ['head']
    _RETARGET_MAP['CNeck_1'] = ['neck', 'neck1']

    _RETARGET_MAP['CVertebra_4'] = ['spine4', 'spine2', 'spine1', 'chest3', 'chest']
    _RETARGET_MAP['CVertebra_1'] = ['spine', 'abdomen', 'chest']
    _RETARGET_MAP['CVertebra_2'] = ['spine3', 'spine2', 'spine1', 'chest2']

    _RETARGET_MAP['RShoulder_Base'] = ['rightcollar', 'rightshoulder', 'rcollar']
    _RETARGET_MAP['RArm'] = ['rightshoulder', 'rightarm', 'rshldr']
    _RETARGET_MAP['RForearm'] = ['rightelbow', 'rightforearm', 'rforearm']
    _RETARGET_MAP['RHand'] = ['righthand', 'rhand']

    _RETARGET_MAP['RThumb_1'] = ['righthandthumb1', 'rightfinger1metacarpal']
    _RETARGET_MAP['RThumb_2'] = ['righthandthumb2', 'rightfinger1proximal']
    _RETARGET_MAP['RThumb_3'] = ['righthandthumb3', 'rightfinger1distal']
    _RETARGET_MAP['RIndex_1'] = ['righthandindex1', 'rightfinger2proximal']
    _RETARGET_MAP['RIndex_2'] = ['righthandindex2', 'rightfinger2medial']
    _RETARGET_MAP['RIndex_3'] = ['righthandindex3', 'rightfinger2distal']
    _RETARGET_MAP['RMiddle_1'] = ['righthandmiddle1', 'rightfinger3proximal']
    _RETARGET_MAP['RMiddle_2'] = ['righthandmiddle2', 'rightfinger3medial']
    _RETARGET_MAP['RMiddle_3'] = ['righthandmiddle3', 'rightfinger3distal']
    _RETARGET_MAP['RRing_1'] = ['righthandring1', 'rightfinger4proximal']
    _RETARGET_MAP['RRing_2'] = ['righthandring2', 'rightfinger4medial']
    _RETARGET_MAP['RRing_3'] = ['righthandring3', 'rightfinger4distal']
    _RETARGET_MAP['RPinky_1'] = ['righthandpinky1', 'rightfinger5proximal']
    _RETARGET_MAP['RPinky_2'] = ['righthandpinky2', 'rightfinger5medial']
    _RETARGET_MAP['RPinky_3'] = ['righthandpinky3', 'rightfinger5distal']

    _RETARGET_MAP['LShoulder_Base'] = ['leftcollar', 'leftshoulder', 'lcollar']
    _RETARGET_MAP['LArm'] = ['leftshoulder', 'leftarm', 'lshldr']
    _RETARGET_MAP['LForearm'] = ['leftelbow', 'leftforearm', 'lforearm']
    _RETARGET_MAP['LHand'] = ['lefthand', 'lhand']

    _RETARGET_MAP['LThumb_1'] = ['lefthandthumb1', 'leftfinger1metacarpal']
    _RETARGET_MAP['LThumb_2'] = ['lefthandthumb2', 'leftfinger1proximal']
    _RETARGET_MAP['LThumb_3'] = ['lefthandthumb3', 'leftfinger1distal']
    _RETARGET_MAP['LIndex_1'] = ['lefthandindex1', 'leftfinger2proximal']
    _RETARGET_MAP['LIndex_2'] = ['lefthandindex2', 'leftfinger2medial']
    _RETARGET_MAP['LIndex_3'] = ['lefthandindex3', 'leftfinger2distal']
    _RETARGET_MAP['LMiddle_1'] = ['lefthandmiddle1', 'leftfinger3proximal']
    _RETARGET_MAP['LMiddle_2'] = ['lefthandmiddle2', 'leftfinger3medial']
    _RETARGET_MAP['LMiddle_3'] = ['lefthandmiddle3', 'leftfinger3distal']
    _RETARGET_MAP['LRing_1'] = ['lefthandring1', 'leftfinger4proximal']
    _RETARGET_MAP['LRing_2'] = ['lefthandring2', 'leftfinger4medial']
    _RETARGET_MAP['LRing_3'] = ['lefthandring3', 'leftfinger4distal']
    _RETARGET_MAP['LPinky_1'] = ['lefthandpinky1', 'leftfinger5proximal']
    _RETARGET_MAP['LPinky_2'] = ['lefthandpinky2', 'leftfinger5medial']
    _RETARGET_MAP['LPinky_3'] = ['lefthandpinky3', 'leftfinger5distal']

    _RETARGET_MAP['RThigh'] = ['righthip', 'rightupleg', 'rthigh', 'rightthigh']
    _RETARGET_MAP['RShin'] = ['rightknee', 'rightleg', 'rshin', 'rightshin']
    _RETARGET_MAP['RFoot'] = ['rightankle', 'rightfoot', 'rfoot', 'rightfoot']
    _RETARGET_MAP['RFootToes'] = ['righttoe', 'righttoebase', 'righttoe']

    _RETARGET_MAP['LThigh'] = ['lefthip', 'leftupleg', 'lthigh', 'leftthigh']
    _RETARGET_MAP['LShin'] = ['leftknee', 'leftleg', 'lshin', 'leftshin']
    _RETARGET_MAP['LFoot'] = ['leftankle', 'leftfoot', 'lfoot', 'leftfoot']
    _RETARGET_MAP['LFootToes'] = ['lefttoe', 'lefttoebase', 'lefttoe']

    _RETARGET_MODULE_ID = 'std.bipedRetarget'
    _RETARGET_RIG_ID = 'std.bipedRetarget'

    _HINGE_RETARGET_JOINTS = [
        'RThumb_2',
        'RThumb_3',

        'RIndex_2',
        'RIndex_3',

        'RMiddle_2',
        'RMiddle_3',

        'RRing_2',
        'RRing_3',

        'RPinky_2',
        'RPinky_3',

        'LThumb_2',
        'LThumb_3',

        'LIndex_2',
        'LIndex_3',

        'LMiddle_2',
        'LMiddle_3',

        'LRing_2',
        'LRing_3',

        'LPinky_2',
        'LPinky_3'
    ]

    RetargetRigIdentifier = _RETARGET_RIG_ID

    @classmethod
    def isRetargetingRig(cls, rig):
        """
        Tests whether given rig is a rig that has biped retarget identifier.

        Parameters
        ----------
        rig : Rig

        Returns
        -------
        bool
        """
        return rig.identifier == cls._RETARGET_RIG_ID

    @property
    def retargetingModule(self):
        """
        Gets retargeting module object.

        Returns
        -------
        BipedRetargetingModule
        """
        return self._retargetModule

    @property
    def skeletonModoItems(self):
        """
        Gets a list of retarget skeleton items as modo item objects.

        Returns
        -------
        [modo.Item]
        """
        items = modox.ItemUtils.getHierarchyRecursive(self._skeletonRoot.modoItem, includeRoot=True)
        for x in range(len(items)):
            if items[x].type == modox.c.ItemType.IK_FULL_BODY:
                items.pop(x)
                break
        return items

    @property
    def skeletonItems(self):
        """
        Gets a list of retarget skeleton items as rig item objects.

        Returns
        -------
        [Item]
        """
        modoItems = self.skeletonModoItems
        rigItems = []
        for modoItem in modoItems:
            try:
                rigItem = Item.getFromModoItem(modoItem)
            except TypeError:
                continue
            rigItems.append(rigItem)
        return rigItems

    @property
    def skeletonItemsByReferenceName(self):
        """
        Gets a list of retarget skeleton items in a dictionary keyed by items' reference names.

        Returns
        -------
        {str : Item}
        """
        items = self.skeletonItems
        itemsByRefName = {}
        for item in items:
            refName = item.getReferenceName(side=True, moduleName=False, basename=True)
            itemsByRefName[refName] = item
        return itemsByRefName

    @property
    def skeletonVisibility(self):
        """
        Gets visibility of the retarget skeleton.

        Returns
        -------
        bool
        """
        return not self._skeletonRoot.hidden

    @skeletonVisibility.setter
    def skeletonVisibility(self, state):
        """
        Sets visibility for the retarget skeleton joints.

        Parameters
        ----------
        state : bool
        """
        for rigItem in self.skeletonItems:
            rigItem.hidden = not state

    @property
    def skeletonLocked(self):
        """
        Tests whether retarget skeleton should be locked from keyframe editing.

        Returns
        -------
        bool
        """
        return ControllerItemFeature(self._skeletonRoot).locked

    @skeletonLocked.setter
    def skeletonLocked(self, state):
        """
        Sets locked state for retarget skeleton.

        Locked skeleton is not editable via keyframe editing tools.

        Parameters
        ----------
        state : bool
        """
        for rigItem in self.skeletonItems:
            ControllerItemFeature(rigItem).locked = state

    @property
    def retargetSkeletonRoot(self):
        """ Returns retarget skeleton root item.

        Returns
        -------
        Item
        """
        return self._skeletonRoot

    @property
    def sourceSkeletonRoot(self):
        """ Returns an item that is linked to retarget skeleton root.

        Returns
        -------
        modo.Item, None
            None is returned when there is no item linked.
        """
        return self._getSourceItemForRetargetJoint(self._skeletonRoot.modoItem)

    @property
    def sourceSkeletonItems(self):
        root = self.sourceSkeletonRoot
        return modox.ItemUtils.getHierarchyRecursive(root, includeRoot=True)

    def initialize(self, sourceRootModoItem, overrideDialogs=False):
        """
        Initializes retargeting process.

        Parameters
        ----------
        sourceRootModoItem : modo.Item
            Root item of the skeleton with the motion that you want to be retargeted to ACS rig.
        """
        # We need to be in setup mode
        setup = modox.SetupMode()
        setup.state = True

        if not self._setIK(self._skeletonRoot.modoItem):
            return
        #self._addRetargetSkeletonToActor()
        self._tuneIKSettings()
        self.skeletonVisibility = True

        modo.Scene().select([sourceRootModoItem, self._skeletonRoot.modoItem], add=False)

        # If there's a valid retarget map file set we use it.
        # If not we run retargeting without suppressing the dialog asking
        # for retargeting map file.
        retargetMapFile = service.userValue.get('rs.retargetMapFile')
        if retargetMapFile and os.path.isfile(retargetMapFile):
            run('!retarget.enable 1')
            # Can't do that, MODO crashes.
            # Also, it looks like loading actor map after retargeting tool is initialized
            # does not work properly if links are not cleared.
            # run('!actor.mapLoad fileName:{%s}' % retargetMapFile)
        else:
            if overrideDialogs:
                run('!retarget.enable 1')
            else:
                run('retarget.enable 1')

    def bake(self, firstFrame, lastFrame, actionName):
        """
        Bakes retargeted motion onto the retarget skeleton.

        Parameters
        ----------
        firstFrame : int

        lastFrame : int

        actionName : str
            Name for the action that will be created before baking process.
            Baking always goes to the new action.
        """
        retargetMod = self.retargetingModule
        skeletonRoot = retargetMod.skeletonRoot

        # Do baking first
        modo.Scene().select(skeletonRoot.modoItem, add=False)
        setupMode = modox.SetupMode()
        setupMode.state = False

        self._setupAction(actionName)

        run('!retarget.bake frameS:%d frameE:%d' % (firstFrame, lastFrame))
        self._cleanUpBakedChannels()
        self._removeSetupFromRetargetSkeleton()
        run('group.current {%s} actr' % self._rig.actor.id)

    def reduceKeys(self):
        """
        Runs the hidden reduce keys command on all retarget skeleton animated channels.
        """
        channels = self._getSkeletonChannels()
        for channel in channels:
            run('!select.channel {%s:%s} mode:set' % (channel.item.id, channel.name))
            run('!channel.keyReduce')

    def setLinks(self):
        """
        Tries to find links between source and retarget skeleton joints automatically.
        """
        sourceSkeletonJointsByRefName = self._collectSourceJointsByReferenceName()
        mapKeys = list(self._RETARGET_MAP.keys())
        sourceSkeletonKeys = list(sourceSkeletonJointsByRefName.keys())
        connected = []

        # Links have to be set in an order set by the _RETARGET_MAP keys order.
        # This is crucial for correct linking with various naming conventions.
        # First we create retarget map where we put all retarget skeleton joints
        # mapped by their ref names.
        retargetSkeletonMap = {}
        skeletonRoot = self._skeletonRoot.modoItem
        for retargetJoint in self.skeletonItems:
            # Do not touch the root.
            if retargetJoint.modoItem == skeletonRoot:
                continue
            refName = retargetJoint.getReferenceName(side=True, moduleName=False, basename=True)
            if refName not in mapKeys:
                continue
            retargetSkeletonMap[refName] = retargetJoint

        # Now we go through all the keys in retarget map
        # meaning all retarget skeleton joints and we try to match a link for them.
        for mapKey in mapKeys:
            for match in self._RETARGET_MAP[mapKey]:
                if match not in sourceSkeletonKeys:
                    continue
                # If connection was already made on some other item - skip it.
                # This is used for spine joints where with different naming
                # conventions if a chest connection was made a spine1
                # connection to the same joint won't be made.
                if match in connected:
                    continue

                # Need to skip non-existent references.
                # That's because the spine maybe shorter and missing one joint.
                try:
                    if self._setLink(sourceSkeletonJointsByRefName[match], retargetSkeletonMap[mapKey].modoItem):
                        connected.append(match)
                        break
                except KeyError:
                    continue
        return True

    def clearMapping(self):
        """ Clears all retarget links in one go.
        """
        for retargetJoint in self.skeletonModoItems:
            # Skip root.
            if retargetJoint == self._skeletonRoot.modoItem:
                continue
            sourceItem = self._getSourceItemForRetargetJoint(retargetJoint)
            if not sourceItem:
                continue

            run('!ikfb.retarget {%s} {%s} 0 0' % (sourceItem.id, retargetJoint.id))
        return True

    def cancel(self):
        # To toggle retargeting off you need to select source and target
        # skeleton roots.
        sourceSkeletonRoot = self.sourceSkeletonRoot
        if sourceSkeletonRoot is None:
            return
        modo.Scene().select([sourceSkeletonRoot, self._skeletonRoot.modoItem], add=False)
        run('!retarget.enable 0')

    def cleanUp(self):
        """
        Removes Full Body IK from the retargeting skeleton.
        Removes retarget skeleton items from control rig actor.
        """
        self.cancel()
        self._removeSetupFromRetargetSkeleton()

    # -------- Private methods

    def _removeSetupFromRetargetSkeleton(self):
        """
        Use this function to remove temporary stuff that needs to be there for retargeting to work
        on the retarget skeleton.
        """
        self._removeIK()
        #self._removeRetargetSkeletonFromActor()

    def _setupAction(self, actionName):
        actor = self._rig.actor
        actionClip = actor.addAction(actionName)
        actionClip.active = True

    def _cleanUpBakedChannels(self):
        """
        Removes keyframes from position and scale channels.
        Position is not removed from root item only.
        """
        skeletonHierarchy = modox.ItemUtils.getHierarchyRecursive(self._skeletonRoot.modoItem, includeRoot=True)
        skeletonRootModoItem = self._skeletonRoot.modoItem

        for joint in skeletonHierarchy:
            if joint != skeletonRootModoItem:
                for channelName in modox.c.TransformChannels.PositionAll:
                    xfrmItem = modox.LocatorUtils.getTransformItem(joint, modox.c.TransformType.POSITION)
                    srcChannel = xfrmItem.channel(channelName)
                    modox.ChannelUtils.clearAnimation(srcChannel)

            for channelName in modox.c.TransformChannels.ScaleAll:
                xfrmItem = modox.LocatorUtils.getTransformItem(joint, modox.c.TransformType.SCALE)
                srcChannel = xfrmItem.channel(channelName)
                modox.ChannelUtils.clearAnimation(srcChannel)

    def _getSkeletonChannels(self):
        channels = []
        skeletonHierarchy = modox.ItemUtils.getHierarchyRecursive(self._skeletonRoot.modoItem, includeRoot=True)
        for joint in skeletonHierarchy:
            # Add position for root item only
            if joint == self._skeletonRoot.modoItem:
                xfrmItem = modox.LocatorUtils.getTransformItem(joint, modox.c.TransformType.POSITION)
                channels.append(xfrmItem.channel(modox.c.TransformChannels.PositionX))
                channels.append(xfrmItem.channel(modox.c.TransformChannels.PositionY))
                channels.append(xfrmItem.channel(modox.c.TransformChannels.PositionZ))

            xfrmItem = modox.LocatorUtils.getTransformItem(joint, modox.c.TransformType.ROTATION)
            channels.append(xfrmItem.channel(modox.c.TransformChannels.RotationX))
            channels.append(xfrmItem.channel(modox.c.TransformChannels.RotationY))
            channels.append(xfrmItem.channel(modox.c.TransformChannels.RotationZ))

        return channels

    def _setIK(self, rootModoItem):
        """ Set IK on the retarget skeleton.
        If the retarget root has ik.package then it is assumed the IK
        is already assigned.
        TODO: Might need better checking.
        """
        if rootModoItem.internalItem.PackageTest('ik.package'):
            return True

        run('!ikfb.assign {%s}' % rootModoItem.id)
        return True

    def _removeIK(self):
        children = self._skeletonRoot.modoItem.children(recursive=False, itemType=modox.c.ItemType.IK_FULL_BODY)
        if not children:
            log.out("Full Body IK solver was not found, can't remove IK from retarget skeleton.", log.MSG_ERROR)
            return
        ikSolverItem = children[0]
        run('!ikfb.remove {%s}' % ikSolverItem.id)

    def _addRetargetSkeletonToActor(self):
        skeletonItems = self.skeletonModoItems
        actorGroup = self._rig.actor

        # When adding items to actor make sure not to add
        # full body IK solver item.
        for modoItem in skeletonItems:
            actorGroup.addItems(modoItem)

    def _removeRetargetSkeletonFromActor(self):
        self._rig.actor.removeItems(self.skeletonModoItems)

    def _tuneIKSettings(self):
        skeletonMap = self.skeletonItemsByReferenceName
        for refName in self._HINGE_RETARGET_JOINTS:
            try:
                item = skeletonMap[refName]
            except KeyError:
                continue

            run('!item.channel ikAxisYRotEnable false item:{%s}' % item.modoItem.id)
            run('!item.channel ikAxisZRotEnable false item:{%s}' % item.modoItem.id)

    def _getSourceItemForRetargetJoint(self, retargetJointModoItem):
        return modox.ItemUtils.getFirstReverseGraphConnection(retargetJointModoItem, 'ikRetarget')

    def _getTargetItemForSourceJoint(self, sourceJointModoItem):
        return modox.ItemUtils.getFirstForwardGraphConnection(sourceJointModoItem, 'ikRetarget')

    def _setLink(self, sourceItem, targetItem):
        """ Set retargeting link between two items.
        Check if there's an existing link that's valid. If it's valid,
        leave it. If not - delete it and set new one.

        Parameters
        ----------
        sourceItem : modo.Item

        targetItem : modo.Item
        """
        currentlyLinkedSource = self._getSourceItemForRetargetJoint(targetItem)
        if currentlyLinkedSource is not None:
            if currentlyLinkedSource == sourceItem:
                # There's a good link already.
                return True
            # Delete the link, it's not what we want.
            # We only set up rotation links (type 0).
            # Remove is mode = 0.
            try:
                lx.eval('!ikfb.retarget {%s} {%s} 0 0' % (currentlyLinkedSource.id, targetItem.id))
            except RuntimeError:
                return False

        # We also need to test forward links for the source skeleton item.
        # Source skeleton item can already be plugged into something and if
        # that's the case we need to cancel that link too.
        currentlyLinkedTarget = self._getTargetItemForSourceJoint(sourceItem)
        if currentlyLinkedTarget:
            try:
                lx.eval('!ikfb.retarget {%s} {%s} 0 0' % (sourceItem.id, currentlyLinkedTarget.id))
            except RuntimeError:
                return False

        # Set a new link.
        try:
            lx.eval('!ikfb.retarget {%s} {%s} 0' % (sourceItem.id, targetItem.id))
        except RuntimeError:
            return False
        else:
            return True

    def _collectSourceJointsByReferenceName(self):
        """
        Scans source skeleton and puts joints into dictionary keyed by reference name.

        This name will be used to match retarget skeleton to source skeleton automatically.
        """
        collection = {}
        for joint in self.sourceSkeletonItems:
            name = joint.name

            # Chuck off what comes before ':'
            # This will remove rig name in Mixamo skeleton
            nameTmp = name.split(':')
            nameTmp = nameTmp[-1]

            # Do the same as above with the '-' character
            nameTmp = nameTmp.split('-')
            nameTmp = nameTmp[-1]

            # If we have parenthesis we take everything prior to parenthesis
            nameTmp = nameTmp.split('(')[0]

            # Remove spaces and underscores.
            nameTmp = nameTmp.replace(' ', '')
            nameTmp = nameTmp.replace(' ', '')

            # Convert name to all lowercase.
            nameKey = str(nameTmp).lower()
            collection[nameKey] = joint
        return collection

    def __init__(self, rigInitializer):
        if not isinstance(rigInitializer, Rig):
            try:
                self._rig = Rig(rigInitializer)
            except TypeError:
                raise
        else:
            self._rig = rigInitializer

        self._retargetModule = self._rig.modules.getFeaturedModule(self._RETARGET_MODULE_ID)
        if self._retargetModule is None:
            raise TypeError

        self._skeletonRoot = self._retargetModule.skeletonRoot