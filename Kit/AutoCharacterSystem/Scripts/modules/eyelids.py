

import lx
import modo
import modox

import rs


PIECE_ID_CORRECTIVE_MORPHS = 'corrective'


class EyelidsModuleFunctionality(object):

    @property
    def module(self):
        return self._module

    @property
    def correctiveMorphInfluences(self):
        try:
            piece = self.module.getFirstPieceByIdentifier(PIECE_ID_CORRECTIVE_MORPHS)
        except LookupError:
            raise

        deformFolder = piece.getKeyItem(rs.c.KeyItem.DEFORM_FOLDER)
        morphInfluences = modox.DeformersStack.getDeformTree(deformFolder.modoItem, includeRoot=False)
        return [modox.MorphInfluence(modoItem) for modoItem in morphInfluences]

    def __init__(self, module):
        self._module = module


class PropAddCorrectiveMorphs(rs.base_ModuleProperty):

    descIdentifier = 'pcmorph'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descUsername = 'eSetupCMorphs'
    descTooltipMsgTableKey = 'elidAddMorph'

    def onQuery(self):
        try:
            self.module.getFirstPieceByIdentifier(PIECE_ID_CORRECTIVE_MORPHS)
        except LookupError:
            return False

        return True

    def onSet(self, state):
        currentState = self.onQuery()
        if state == currentState:
            return False

        result = False
        if not state:
            self.module.removePiece(PIECE_ID_CORRECTIVE_MORPHS)
        else:
            piece = self.module.addPiece(PIECE_ID_CORRECTIVE_MORPHS, updateItemNames=True)
            deformFolder = piece.getKeyItem(rs.c.KeyItem.DEFORM_FOLDER)
            deformStack = rs.DeformStack(self.module.rigRootItem)
            deformStack.addToStack(deformFolder, order=rs.DeformStack.Order.POST_MORPHS)

        return result


class PropInitCorrectiveMorphsForSelectedMeshes(rs.base_ModuleCommand):

    descIdentifier = 'initcmorph'
    descUsername = 'eInitCMorphs'
    descTooltipMsgTableKey = 'elidInitMorph'

    def run(self, arguments=[]):
        # Make sure corrective morphs are enabled
        enabledProp = PropAddCorrectiveMorphs(self.module)
        if not enabledProp.onQuery():
            enabledProp.onSet(True)

        meshes = modox.ItemSelection().getOfTypeModo(modo.c.MESH_TYPE)
        if not meshes:
            return

        # Connect selected meshes to morph influences
        eyelidsFunc = EyelidsModuleFunctionality(self.module)
        morphDeformers = eyelidsFunc.correctiveMorphInfluences

        if not morphDeformers:
            return

        for morphDeform in morphDeformers:
            morphDeform.meshes = meshes

        # Make sure morph maps are there and set them on the morph influences.
        for mesh in meshes:
            with modo.Mesh(mesh.internalItem).geometry as geo:
                for morphDeform in morphDeformers:
                    itemName = rs.Item.getFromModoItem(morphDeform.modoItem).renderNameFromTokens(
                        [rs.c.NameToken.SIDE, rs.c.NameToken.MODULE_NAME, rs.c.NameToken.BASE_NAME])
                    mapName = itemName + ' (Corrective)'
                    geo.vmaps.addMorphMap(name=mapName, static=False)
                    morphDeform.mapName = mapName


class PropEnableCorrectiveMorphs(rs.base_ModuleProperty):

    descIdentifier = 'enablemorph'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descUsername = 'eEnableCMorphs'
    descSetupMode = None
    descTooltipMsgTableKey = 'elidEnableMorph'

    def onQuery(self):
        try:
            piece = self.module.getFirstPieceByIdentifier(PIECE_ID_CORRECTIVE_MORPHS)
        except LookupError:
            return False

        folder = piece.getKeyItem(rs.c.KeyItem.DEFORM_FOLDER)
        return modox.DeformFolder(folder.modoItem).enabled

    def onSet(self, state):
        currentState = self.onQuery()
        if state == currentState:
            return False

        addSetupProp = PropAddCorrectiveMorphs(self.module)
        if not addSetupProp.onQuery():
            return False

        try:
            piece = self.module.getFirstPieceByIdentifier(PIECE_ID_CORRECTIVE_MORPHS)
        except LookupError:
            return False

        folder = piece.getKeyItem(rs.c.KeyItem.DEFORM_FOLDER)
        modox.DeformFolder(folder.modoItem).enabled = state


class base_PropEditEyelidCorrectiveMorph(rs.base_ModuleCommand):

    descSetupMode = None
    descSupportSymmetry = False
    descMorphInfIdent = ''

    def run(self, arguments=[]):
        piece = self.module.getFirstPieceByIdentifier(PIECE_ID_CORRECTIVE_MORPHS)
        morph = piece.getKeyItem(self.descMorphInfIdent)

        morphInf = modox.MorphInfluence(morph.modoItem)
        meshes = morphInf.meshes

        # If there are no meshes plugged, do nothing.
        if not meshes:
            return

        selection = meshes + [morphInf.modoItem]
        modox.ItemSelection().set(selection, selMode=modox.SelectionMode.REPLACE)
        rs.run('item.componentMode polygon true')


class PropEditUpperEyelidCorrectiveMorph(base_PropEditEyelidCorrectiveMorph):

    descIdentifier = 'editupcmorph'
    descUsername = 'eEditUpCMorph'
    descMorphInfIdent = 'morphup'
    descTooltipMsgTableKey = 'elidEditUpMorph'


class PropEditLowerEyelidCorrectiveMorph(base_PropEditEyelidCorrectiveMorph):

    descIdentifier = 'editlowcmorph'
    descUsername = 'eEditLowCMorph'
    descMorphInfIdent = 'morphlow'
    descTooltipMsgTableKey = 'elidEditLowMorph'


class PropExitCorrectiveMorphEdit(rs.base_ModuleCommand):

    descIdentifier = 'editmorphout'
    descUsername = 'eEditCMorphExit'
    descSetupMode = None
    descTooltipMsgTableKey = 'elidExitEditMorph'

    def run(self, arguments=[]):
        rs.run('!select.type item')
        modox.ItemSelection().set(self.module.rootModoItem, selMode=modox.SelectionMode.REPLACE)


class PropMirrorMorphs(rs.base_ModuleCommand):

    descIdentifier = 'mirmoprh'
    descUsername = 'eCMorphMirror'
    descSetupMode = None
    descSupportSymmetry = False
    descTooltipMsgTableKey = 'elidMirrorMorph'
    
    def run(self, arguments=[]):
        eyelidsFunc = EyelidsModuleFunctionality(self.module)
        morphDeformers = eyelidsFunc.correctiveMorphInfluences

        for morphInf in morphDeformers:
            sourceMapName = morphInf.mapName
            morphInfRigItem = rs.Item.getFromModoItem(morphInf.modoItem)
            fromSide = morphInfRigItem.side
            targetSide = rs.c.Side.LEFT
            if fromSide == rs.c.Side.LEFT:
                targetSide = rs.c.Side.RIGHT

            rig = rs.Rig(self.module.rigRootItem)
            nameOp = rs.NamingSchemeOperator(rig.namingScheme)

            nameTokens = {rs.c.NameToken.SIDE: targetSide,
                          rs.c.NameToken.MODULE_NAME: self.module.name,
                          rs.c.NameToken.BASE_NAME: morphInfRigItem.name}
            targetMapName = nameOp.renderName(nameTokens) + ' (Corrective)'

            for mesh in morphInf.meshes:
                cmd = '!rs.vertMap.mirror type:morph fromSide:%s mesh:{%s} sourceMap:{%s} targetMap:{%s}'
                allstring = (cmd % (fromSide, mesh.id, sourceMapName, targetMapName))
                rs.run(allstring)


class EyelidsModule(rs.base_FeaturedModule):

    descIdentifier = 'std.eyelids'
    descUsername = 'Eyelids'
    descFeatures = [PropAddCorrectiveMorphs,
                    PropInitCorrectiveMorphsForSelectedMeshes,
                    modox.c.FormCommandList.DIVIDER,
                    PropEnableCorrectiveMorphs,
                    modox.c.FormCommandList.DIVIDER,
                    PropEditUpperEyelidCorrectiveMorph,
                    PropEditLowerEyelidCorrectiveMorph,
                    modox.c.FormCommandList.DIVIDER,
                    PropExitCorrectiveMorphEdit,
                    modox.c.FormCommandList.DIVIDER,
                    PropMirrorMorphs,
                    ]
