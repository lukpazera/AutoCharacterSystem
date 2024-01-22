

import lx
import lxu
import modo
import modox

import rs


class CmdNewPiece(rs.Command):
    """
    """

    ARG_NAME = 'name'
    ARG_IDENT = 'ident'
    ARG_FROM_ASSEMBLY = 'fromAssm'
    ARG_ASSEMBLY = 'assm'
    
    def arguments(self):
        name = rs.cmd.Argument(self.ARG_NAME, 'string')
        name.defaultValue = "Piece"

        ident = rs.cmd.Argument(self.ARG_IDENT, 'string')
        ident.defaultValue = ""
        
        fromAssm = rs.cmd.Argument(self.ARG_FROM_ASSEMBLY, 'boolean')
        fromAssm.flags = ['optional', 'hidden']
        fromAssm.defaultValue = False
        
        assm = rs.cmd.Argument(self.ARG_ASSEMBLY, '&item')
        assm.flags = ['optional', 'hidden']
        
        return [name, ident, fromAssm, assm]
    
    def execute(self, msg, flags):
        pieceName = self.getArgumentValue(self.ARG_NAME)
        pieceIdent = self.getArgumentValue(self.ARG_IDENT)
        
        newPiece = rs.Piece.new(pieceName)
        
        # Integrate with the rig by adding to schematic and parenting
        rs.run('schematic.addItem item:{%s} mods:false' % newPiece.assemblyModoItem.id)

        # Schematic link is established but now we need to see to which group
        # and parent to this group as well.
        try:
            parentGroup = newPiece.assemblyModoItem.connectedGroups[0]
        except IndexError:
            pass
        else:
            newPiece.assemblyModoItem.setParent(parentGroup)
        
        # Set up identifier
        features = rs.ItemFeatures(newPiece.assemblyModoItem)
        identFeature = features.addFeature(rs.c.ItemFeatureType.IDENTIFIER)
        identFeature.identifier = pieceIdent

        # Sending out new piece created event.
        # Note that this HAS to be done from command here and not from within
        # Piece.new() because when new piece is created it's not part of the rig yet.
        rs.service.events.send(rs.c.EventTypes.PIECE_NEW, piece=newPiece)

    # -------- Private methods
    
    # THIS CODE IS UNUSED FOR THE TIME BEING
    @property
    def _assembly(self):
        if not self.getArgumentValue(self.ARG_FROM_ASSEMBLY):
            return None

        scene = modo.Scene()

        if self.isArgumentSet(self.ARG_ASSEMBLY):
            assmid = self.getArgumentValue(self.ARG_ASSEMBLY)
            try:
                return scene.item(assmid)
            except LookupError:
                return None
        else:
            for item in scene.selected:
                if item.type == 'assembly':
                    return item
        return None

rs.cmd.bless(CmdNewPiece, 'rs.module.newPiece')


class CmdSavePiece(rs.Command):
    """
    """

    ARG_ASSEMBLY = 'assm'
    
    def arguments(self):
        assm = rs.cmd.Argument(self.ARG_ASSEMBLY, '&item')
        assm.flags = ['optional']
        
        return [assm]
    
    def execute(self, msg, flags):
        scene = rs.Scene()
        scene.contexts.resetChanges()
        
        pieces = self._selectedPieces
        pieceCount = 0
        for piece in pieces:
            try:
                piece.save()
            except RuntimeError:
                continue
            pieceCount += 1

        if len(pieces) > 0 and len(pieces) == pieceCount:
            modo.dialogs.alert("Save Piece", "%d Piece(s) saved." % len(pieces))
        else:
            modo.dialogs.alert("Save Piece", "At least one piece was not saved.\nCheck Event Log for errors.", "error")

    # -------- Private methods

    @property
    def _selectedPieces(self):
        if self.isArgumentSet(self.ARG_ASSEMBLY):
            try:
                item = modo.Item(modox.SceneUtils.findItemFast(self.getArgumentValue(self.ARG_ASSEMBLY)))
            except LookupError:
                return []
            try:
                return [rs.Piece(item)]
            except TypeError:
                return []
            return []
        
        pieces = []
        for item in modo.Scene().selected:
            try:
                pieces.append(rs.Piece(item))
            except TypeError:
                continue
        return pieces

rs.cmd.bless(CmdSavePiece, 'rs.module.savePiece')