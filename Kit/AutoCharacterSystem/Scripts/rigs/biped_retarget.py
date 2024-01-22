

import lx
import modo
import modox

import rs
from modules import fk_chain
from rs.const import EventTypes as e


RETARGET_RIG_ID = 'std.bipedRetarget'
RETARGET_MODULE_ID = 'std.bipedRetarget'


class Cmd3JointSpine(rs.base_RigCommand):
    """
    This command connects retarget skeleton local transforms to
    special transforms on the control rig.
    These transforms are created on the fly if they're not there on the rig yet.
    """

    descIdentifier = '3jntspine'
    descUsername = 'Set 3 Joints Spine'

    def run(self, arguments):
        if self._isAlreadyApplied():
            rs.log.out("The spine already has 3 joints only.")
            return False

        # The order is crucial hiere since setting spine to 3 joints
        # on motion rig will apply guide and refresh retarget skeleton.
        # In reverse order retarget skeleton rest pose won't get refreshed.
        self._removeVertebra3FromRetargetSkeleton()
        self._setSpineTo3JointsOnRig()
        return True

    # -------- Private methods

    def _isAlreadyApplied(self):
        """
        Tests whether the command was already applied to rig.

        If there are less then 2 piece segments it means that spine chain
        is 2 segments already.
        """
        moduleOp = rs.ModuleOperator(self.rig.rootItem)

        spineModule = moduleOp.getModuleByName("Spine")
        segmentPieces = spineModule.getPiecesByIdentifierOrdered(fk_chain.SegmentPiece.descIdentifier)

        if len(segmentPieces) < 2:
            return True
        return False

    def _removeVertebra3FromRetargetSkeleton(self):
        retargeting = rs.Retargeting(self.rig)

        vert2 = None
        vert3 = None
        vert4 = None

        for rigItem in retargeting.skeletonItems:
            name = rigItem.name
            if name == "Vertebra_2":
                vert2 = rigItem
            elif name == "Vertebra_3":
                vert3 = rigItem
            elif name == "Vertebra_4":
                vert4 = rigItem

            if vert2 is not None and vert3 is not None and vert4 is not None:
                break

        rs.run('!item.parent item:{%s} parent:{%s} inPlace:0' % (vert4.modoItem.id, vert2.modoItem.id))
        rs.run('!item.delete item:{%s}' % vert3.modoItem.id)

    def _setSpineTo3JointsOnRig(self):
        # Disconnect chest first
        moduleOp = rs.ModuleOperator(self.rig.rootItem)
        chestModule = moduleOp.getModuleByName("Chest")
        chestPlug = chestModule.getRigItemsOfType(rs.c.RigItemType.PLUG)[0]
        rs.run('rs.item.disconnectPlug item:{%s}' % chestPlug.modoItem.id)

        # Change number of spine joints
        spineModule = moduleOp.getModuleByName("Spine")
        rs.run('rs.module.property std.fkChain psegs 2 rootItem:{%s}' % spineModule.rootModoItem.id)
        # NOTE FOR WHENEVER - for some reason after executing command above we're out of setup mode.

        # plug chest to spine.
        segmentPieces = spineModule.getPiecesByIdentifierOrdered(fk_chain.SegmentPiece.descIdentifier)
        socket = segmentPieces[-1].getKeyItem(fk_chain.SegmentPiece.SOCKET_IDENTIFIER)
        rs.run('rs.item.connectPlug plug:{%s} socket:{%s}' % (chestPlug.modoItem.id, socket.modoItem.id))

class BipedRetargetRig(rs.base_FeaturedRig):

    descIdentifier = RETARGET_RIG_ID
    descUsername = 'Biped Retarget'
    descFeatures = [Cmd3JointSpine]



