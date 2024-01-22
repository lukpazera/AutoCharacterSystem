

import lx
import modo
import modox

import rs
from rs.const import EventTypes as e


RETARGET_MODULE_ID = 'std.bipedRetarget'

# This maps joints in the retarget skeleton to rig controllers.
# key is retarget skeleton joint name, value is rig controller reference name.
SKELETON_MAP = {

    # Center
    'CRoot': 'CRootMain',
    'CVertebra_1': 'CSpineSeg1',
    'CVertebra_2': 'CSpineSeg2',
    'CVertebra_3': 'CSpineSeg3',
    'CVertebra_4': 'CChestMain',

    'CNeck_1': 'CNeckSeg1',
    'CHead_1': 'CHeadFKMain',

    # Right Arm
    'RShoulder_Base': 'RShoulderMain',
    'RArm': 'RArmArm',
    'RForearm': 'RArmForearm',
    'RHand': 'RArmHand',

    'RThumb_1': 'RThumbSeg1',
    'RThumb_2': 'RThumbSeg2',
    'RThumb_3': 'RThumbSeg3',

    'RIndex_1': 'RIndexSeg1',
    'RIndex_2': 'RIndexSeg2',
    'RIndex_3': 'RIndexSeg3',

    'RMiddle_1': 'RMiddleSeg1',
    'RMiddle_2': 'RMiddleSeg2',
    'RMiddle_3': 'RMiddleSeg3',

    'RRing_1': 'RRingSeg1',
    'RRing_2': 'RRingSeg2',
    'RRing_3': 'RRingSeg3',

    'RPinky_1': 'RPinkySeg1',
    'RPinky_2': 'RPinkySeg2',
    'RPinky_3': 'RPinkySeg3',

    # Left Arm
    'LShoulder_Base': 'LShoulderMain',
    'LArm': 'LArmArm',
    'LForearm': 'LArmForearm',
    'LHand': 'LArmHand',

    'LThumb_1': 'LThumbSeg1',
    'LThumb_2': 'LThumbSeg2',
    'LThumb_3': 'LThumbSeg3',

    'LIndex_1': 'LIndexSeg1',
    'LIndex_2': 'LIndexSeg2',
    'LIndex_3': 'LIndexSeg3',

    'LMiddle_1': 'LMiddleSeg1',
    'LMiddle_2': 'LMiddleSeg2',
    'LMiddle_3': 'LMiddleSeg3',

    'LRing_1': 'LRingSeg1',
    'LRing_2': 'LRingSeg2',
    'LRing_3': 'LRingSeg3',

    'LPinky_1': 'LPinkySeg1',
    'LPinky_2': 'LPinkySeg2',
    'LPinky_3': 'LPinkySeg3',

    # Right Leg
    'RThigh': 'RLegThigh',
    'RShin': 'RLegShin',
    'RFoot': 'RLegFoot',
    'RFootToes': 'RLegFootToes',

    # Left Leg
    'LThigh': 'LLegThigh',
    'LShin': 'LLegShin',
    'LFoot': 'LLegFoot',
    'LFootToes': 'LLegFootToes',
}


class CmdInitialize(rs.base_ModuleCommand):
    """
    This command connects retarget skeleton local transforms to
    special transforms on the control rig.
    These transforms are created on the fly if they're not there on the rig yet.
    """

    descIdentifier = 'init'
    descUsername = 'Attach To Rig'

    def run(self, arguments):

        rig = rs.Rig(self.module.rigRootItem)

        # Get controllers and put them in dictionary based on their reference names.
        ctrls = rig[rs.c.ElementSetType.CONTROLLERS].elements
        ctrlsByReferenceName = {}
        for ctrlModoItem in ctrls:
            try:
                ctrlRigItem = rs.Item.getFromModoItem(ctrlModoItem)
            except TypeError:
                continue
            rs.log.out(ctrlRigItem.getReferenceName())
            ctrlsByReferenceName[ctrlRigItem.getReferenceName()] = ctrlRigItem

        retargetMod = rig.modules.getFeaturedModule(RETARGET_MODULE_ID)
        skeletonRoot = retargetMod.skeletonRoot
        skeletonHierarchy = modox.ItemUtils.getHierarchyRecursive(skeletonRoot.modoItem, includeRoot=True)

        for joint in skeletonHierarchy:
            try:
                rigJoint = rs.Item.getFromModoItem(joint)
            except TypeError:
                continue

            jointRefName = rigJoint.getReferenceName(side=True, moduleName=False, basename=True)
            try:
                ctrlRefName = SKELETON_MAP[jointRefName]
            except KeyError:
                rs.log.out("Cannot find controller for %s retarget skeleton joint!" % jointRefName)
                continue

            try:
                controllerItem = ctrlsByReferenceName[ctrlRefName]
            except KeyError:
                rs.log.out("%s - bad controller reference!" % ctrlRefName)
                continue

            ctrlModoItem = controllerItem.modoItem
            self._addPreTransformItem(joint, ctrlModoItem, modox.c.TransformType.ROTATION)

            if joint == skeletonRoot.modoItem:
                self._addPreTransformItem(joint, ctrlModoItem, modox.c.TransformType.POSITION)

    def _addPreTransformItem(self, jointModoItem, ctrlModoItem, xfrmType):
        xfrmItem = modox.LocatorUtils.getTransformItem(ctrlModoItem, xfrmType)
        xfrmItem.select(replace=True)
        loc = modo.LocatorSuperType(ctrlModoItem.internalItem)
        newxfrm = loc.transforms.insert(xfrmType, 'pre') # seems to reversed.
        newxfrm.name = "Retarget"
        if xfrmType == modox.c.TransformType.POSITION:
            newxfrm.name += "Position"
        elif xfrmType == modox.c.TransformType.ROTATION:
            newxfrm.name += "Rotation"

        srcXfrmItem = modox.LocatorUtils.getTransformItem(jointModoItem, xfrmType)
        srcChannel = srcXfrmItem.channel('matrix')

        # Test if the channel outputs to matrix channel effect.
        # If it does we want to output from matrix channel effect.
        xfrmOutChannel = modox.ChannelUtils.getOutputChannel(srcChannel, 0)
        if xfrmOutChannel is not None and xfrmOutChannel.item.type == modox.c.ItemType.MATRIX_CHANNEL_EFFECT:
            srcChannel = xfrmOutChannel.item.channel('output')

        dstChannel = newxfrm.channel('matrix')
        srcChannel >> dstChannel


class CmdDetachFromRig(rs.base_ModuleCommand):
    """
    This command detaches retargeting skeleton from the control rig.
    It does it by deleting all transforms on rig controllers that have names starting with "Retarget".
    """

    descIdentifier = 'detach'
    descUsername = 'Detach From Rig'

    def run(self, arguments):
        rig = rs.Rig(self.module.rigRootItem)
        ctrls = rig[rs.c.ElementSetType.CONTROLLERS].elements
        scene = modo.Scene()
        itemsToDelete = []
        for ctrl in ctrls:
            try:
                loc = modo.LocatorSuperType(ctrl.internalItem)
            except TypeError:
                rs.log.out("Controller is not locator: %s" % ctrl.name)
                continue
            for xfrm in loc.transforms:
                if xfrm.name.startswith("Retarget"):
                    itemsToDelete.append(xfrm)
        scene.removeItems(itemsToDelete, children=False)


class BipedRetargetingModule(rs.base_FeaturedModule):

    descIdentifier = RETARGET_MODULE_ID
    descUsername = 'Biped Retargeting'
    descFeatures = [CmdInitialize, CmdDetachFromRig]

    @property
    def skeletonRoot(self):
        """
        Returns
        -------
        Item
        """
        return self.module.getKeyItem('root')


class RetargetingModuleEventHandler(rs.EventHandler):
    """ Handles events concerning retargeting module.
    """

    descIdentifier = 'retargetmod'
    descUsername = 'Retargeting Module'

    @property
    def eventCallbacks(self):
        return {e.GUIDE_APPLY_POST: self.event_guideApplyPost,
                }

    def event_guideApplyPost(self, **kwargs):
        """ Updates retarget skeleton together with the guide.
        """
        try:
            rig = kwargs['rig']
        except KeyError:
            return

        retargetMod = rig.modules.getFeaturedModule(RETARGET_MODULE_ID)
        # Don't do anything if there's no retarget module in the rig.
        if retargetMod is None:
            return

        # Get controllers and put them in dictionary based on their reference names.
        ctrls = rig[rs.c.ElementSetType.CONTROLLERS].elements
        ctrlsByReferenceName = {}
        for ctrlModoItem in ctrls:
            try:
                ctrlRigItem = rs.Item.getFromModoItem(ctrlModoItem)
            except TypeError:
                continue
            ctrlsByReferenceName[ctrlRigItem.getReferenceName()] = ctrlRigItem

        skeletonRoot = retargetMod.skeletonRoot
        skeletonHierarchy = modox.ItemUtils.getHierarchyRecursive(skeletonRoot.modoItem, includeRoot=True)

        itemSelection = modox.ItemSelection()

        for joint in skeletonHierarchy:
            try:
                rigJoint = rs.Item.getFromModoItem(joint)
            except TypeError:
                continue

            jointRefName = rigJoint.getReferenceName(side=True, moduleName=False, basename=True)
            try:
                ctrlRefName = SKELETON_MAP[jointRefName]
            except KeyError:
                rs.log.out("Cannot find controller for %s retarget skeleton joint!" % jointRefName)
                continue

            try:
                controllerItem = ctrlsByReferenceName[ctrlRefName]
            except KeyError:
                rs.log.out("%s - bad controller reference!" % ctrlRefName)
                continue

            lx.eval('item.match item pos item:%s itemTo:%s' % (joint.id, controllerItem.modoItem.id))
            lx.eval('item.match item rot item:%s itemTo:%s' % (joint.id, controllerItem.modoItem.id))

            itemSelection.set(joint, modox.SelectionMode.REPLACE)
            lx.eval('!transform.zero type:translation')
            lx.eval('!transform.zero type:rotation')
