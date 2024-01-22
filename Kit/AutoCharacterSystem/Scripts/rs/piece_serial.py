

from .piece import Piece


class SerialPiece(Piece):
    """
    Serial piece is a piece that is installed multiple times within a module and forms a chain of pieces.

    Attributes
    ----------
    descIdentifier : str

    descSerialNameToken : str
        Serial name is part of piece item name that will be replaced/updated when piece is installed.
        Serial name is a string and then piece number is added after that.

    descPieceHierarchy : dict{str : str}
        { parentItemIdentifier : [childItemIdentifier] }
        parentItemIdentifier - identifier of an item from previous piece in chain or from module
            (if first piece in chain is processed).
        childItemIdentifier - identifier of an item from a serial piece that will be parented to
            previous piece item or to a module if this is first piece in chain.

    descModuleHierarchy : dict{str, str}
        Parents piece key items to module items.
        Note that this is done ONLY if piece item was not parented to previous piece during
        piece hierarchy parenting.
        Use this to insert piece items into module hierarchy but each serial piece
        will be parented to the same module item.

    descDeformersHierarchy : dict{str, str}
        { parentItemIdentifier : [childItemIdentifier] }

    descChainGuide : str
        Key of the guide that is controller guide that will be used for aligning guides
        along the line between start and end guide set up in SerialPiecesSetup.
        This guide will also be used to setting up drawing links between chained guides.
    """

    descIdentifier = ''
    descSerialNameToken = ''
    descPieceHierarchy = {}
    descModuleHierarchy = {}
    descDeformersHierarchy = {}
    descChainGuide = ''


class SerialPiecesSetup(object):
    """
    Serial pieces setup is a chain of serial pieces installed within a module.

    This class describes the entire setup.

    Parameters
    ----------
    module : Module

    Attributes
    ----------
    descSerialPieceClass : SerialPiece
        Class of serial pieces that form this serial pieces setup.

    descSequenceStart : int
        Numbering serial pieces will start from this number.
        If module itself contains some segments already set this to number that first serial piece will have.

    descRawCountChannel : str
        Name of the channel on module rig subassembly in which number of pieces from this setup
        will be stored. This can be used within the rig to drive behaviours that are dependent
        on the number of serial pieces in module.

    descCountChannel : str
        This is similar to the above but numbering is using descSequenceStart as first number.

    descModuleHierarchy : {str : [str]}
        Key is identifier of item in the last piece that module items will be parented to.
        If setup is reduced to 0 serial pieces then the key refers to module item rather then first piece item.
        Value is identifier of module items that will be parented to either last serial piece or to another
        module item if serial pieces chain is reduced to 0 pieces.
    """

    descSerialPieceClass = None
    descSequenceStart = 1
    descRawCountChannel = ''
    descCountChannel = ''
    descModuleHierarchy = {}

    descFitGuide = False
    descGuideItemLinks = False
    descGuideChainStart = ''
    descGuideChainEnd = ''

    def onSerialPieceAdded(self, piece, prevPiece=None, nextPiece=None):
        pass

    @property
    def module(self):
        return self._module

    # -------- Private methods

    def __init__(self, module):
        self._module = module