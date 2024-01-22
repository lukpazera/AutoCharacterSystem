

import lx
import modo
import modox

import rs


KEY_ITEM_SOCKET_PATH = 'pathSocket'
KEY_ITEM_SOCKET_BODY = 'mainSocket'
KEY_ITEM_PATH_MESH = 'pathMesh'


class BodyModule(rs.Module):

    _CHAN_WIDTH = 'Width'
    _CHAN_HEIGHT = 'Height'
    _CHAN_LENGTH = 'Length'

    @property
    def dimensions(self):
        """
        Gets width, height and length of the body.

        Returns
        -------
        float, float, float
            width, height, length.
        """
        # Values we need are evaluated values of guide assembly outputs.
        guideAssm = self.guideAssembly
        if guideAssm is None:
            return 1.8, 1.4, 4.5

        width = guideAssm.modoItem.channel(self._CHAN_WIDTH).get(0.0, None)
        height = guideAssm.modoItem.channel(self._CHAN_HEIGHT).get(0.0, None)
        length = guideAssm.modoItem.channel(self._CHAN_LENGTH).get(0.0, None)

        return width, height, length

    @property
    def pathMeshChannel(self):
        """
        Gets mesh channel from the mesh that holds the path to follow.

        Returns
        -------
        modo.Channel
        """
        return self.getKeyItem(KEY_ITEM_PATH_MESH).modoItem.channel('mesh')

    @property
    def pathMesh(self):
        """
        Gets path mesh rig item.

        Returns
        -------
        Item
        """
        return self.getKeyItem(KEY_ITEM_PATH_MESH)


class PropFrontAxle(rs.base_ModuleProperty):
    """
    Boolean toggle to add/remove front axle with wheels.
    """

    _SUBMODULE_ID = 'frontAxle'
    _SUBMODULE_FILENAME = 'Path Car Front Axle'
    _KEY_ITEM_PLUG_AXLE = 'axlePlug'
    _KEY_ITEM_EDIT_GUIDE = 'gdWheel'
    _KEY_ITEM_PATH_CONSTRAINT = 'pathCns'

    descIdentifier = 'pfrontaxle'
    descUsername = 'frontAxle'
    descValueType = lx.symbol.sTYPE_BOOLEAN
    descScope = rs.base_ModuleProperty.Scope.GLOBAL
    descApplyGuide = True
    descRefreshContext = rs.c.Context.GUIDE
    descTooltipMsgTableKey = 'carFrontAxle'
    
    def onQuery(self):
        """
        Returns
        -------
        bool
        """
        subModules = self.module.getSubmodulesWithIdentifier(self._SUBMODULE_ID)
        return len(subModules) > 0

    def onSet(self, state):
        """ Toggles front axle for this car rig.

        Parameters
        ----------
        state : bool
        """
        if state == self.onQuery():
            return

        updateGuide = False

        if state:
            bodyModule = BodyModule(self.module.rootItem)
            axleModule = self._addAxle()
            self._connectInputsToBody(axleModule, bodyModule)
            self._connectPathConstraint(axleModule, bodyModule)
            self._placeAxle(axleModule, bodyModule)
            updateGuide = True
        else:
            self._removeAxle()

        return updateGuide

    def _addAxle(self):
        rs.service.globalState.ControlledDrop = True
        moduleOp = rs.ModuleOperator(self.module.rigRootItem)
        newModule = moduleOp.addModuleFromPreset(self._SUBMODULE_FILENAME)
        self.module.addSubmodule(newModule, self._SUBMODULE_ID)
        rs.service.globalState.ControlledDrop = False

        # Attach module
        plug = newModule.getKeyItem(self._KEY_ITEM_PLUG_AXLE)
        socket = self.module.getKeyItem(KEY_ITEM_SOCKET_PATH)
        plug.connectToSocket(socket)

        return newModule

    def _connectPathConstraint(self, axleModule, bodyModule):
        """
        Path constraint has to be connected to the path mesh that is part of the body module.
        """
        pathMeshChannel = bodyModule.pathMeshChannel
        pathConstraintItem = axleModule.getKeyItem(self._KEY_ITEM_PATH_CONSTRAINT)
        meshInput = pathConstraintItem.modoItem.channel('mesh')
        pathMeshChannel >> meshInput

    def _connectInputsToBody(self, axleModule, bodyModule):
        """
        Connect front axle module to body by connecting input/output channels between
        modules.
        """
        modox.Assembly.autoConnectOutputsToInputs(bodyModule.assemblyModoItem, axleModule.assemblyModoItem)

    def _placeAxle(self, axleModule, bodyModule):
        """
        Place dropped axle module in default position.

        This really means placing the sole edit guide for the wheel.
        We place it in some default position based on car body dimensions.
        """
        width, height, length = bodyModule.dimensions

        wheelGuide = axleModule.getKeyItem(self._KEY_ITEM_EDIT_GUIDE)
        pos = modo.Vector3()
        pos.x = width * -0.5  # place guide on the right (negative) side
        pos.y = height * 0.3  # let wheel be 1/3 of the car height by default
        pos.z = length * 0.35

        modox.LocatorUtils.setItemPosition(wheelGuide.modoItem,
                                           pos,
                                           action=lx.symbol.s_ACTIONLAYER_SETUP)

    def _removeAxle(self):
        subModules = self.module.getSubmodulesWithIdentifier(self._SUBMODULE_ID)
        if len(subModules) > 0:
            subModules[0].selfDelete()


class PropRearAxles(rs.base_ModuleProperty):
    """
    Number of rear axles this car has.
    """

    _SUBMODULE_ID = 'rearAxle'
    _SUBMODULE_FILENAME = 'Path Car Rear Axle'
    _KEY_ITEM_PLUG_AXLE = 'axlePlug'
    _KEY_ITEM_EDIT_GUIDE = 'gdWheel'

    descIdentifier = 'prearaxles'
    descUsername = 'rearAxles'
    descValueType = lx.symbol.sTYPE_INTEGER
    descScope = rs.base_ModuleProperty.Scope.GLOBAL

    descApplyGuide = True
    descRefreshContext = True

    descTooltipMsgTableKey = 'carRearAxles'

    def onQuery(self):
        """

        Returns
        -------
        int
        """
        subModules = self.module.getSubmodulesWithIdentifier(self._SUBMODULE_ID)
        return len(subModules)

    def onSet(self, number):
        """ Sets new number of rear axles for this car rig.

        Parameters
        ----------
        number : int
        """
        axlesList = self.module.getSubmodulesWithIdentifier(self._SUBMODULE_ID)
        currentCount = len(axlesList)

        if number == currentCount:
            return False

        updateGuide = False

        if number > currentCount:
            # Add more axles.
            self._addNewAxles(number - currentCount, axlesList)
            updateGuide = True
        else:
            # Remove extra axles.
            self._removeAxles(number, axlesList)

        return updateGuide

    def _addNewAxles(self, axleCount, axlesList):
        bodyModule = BodyModule(self.module.rootItem)

        # Index will be used to number rear axles
        index = len(axlesList)

        for x in range(axleCount):
            index += 1
            axleModule = self._addAxle(index)
            self._connectInputsToBody(axleModule, bodyModule)
            self._placeAxle(axleModule, axlesList, bodyModule)

            axlesList.append(axleModule)

    def _addAxle(self, index):
        rs.service.globalState.ControlledDrop = True
        moduleOp = rs.ModuleOperator(self.module.rigRootItem)
        newModule = moduleOp.addModuleFromPreset(self._SUBMODULE_FILENAME)
        self.module.addSubmodule(newModule, self._SUBMODULE_ID)
        rs.service.globalState.ControlledDrop = False

        # Attach module
        plug = newModule.getKeyItem(self._KEY_ITEM_PLUG_AXLE)
        socket = self.module.getKeyItem(KEY_ITEM_SOCKET_PATH)
        plug.connectToSocket(socket)

        if index > 1:
            newModule.name = newModule.name + str(index)

        return newModule

    def _connectInputsToBody(self, axleModule, bodyModule):
        """
        Connect rear axle module to body by connecting input/output channels between
        modules.
        """
        modox.Assembly.autoConnectOutputsToInputs(bodyModule.assemblyModoItem, axleModule.assemblyModoItem)

    def _placeAxle(self, axleModule, axlesList, bodyModule):
        if len(axlesList) > 0:
            lastAxle = axlesList[-1]
            lastWheelGuide = lastAxle.getKeyItem(self._KEY_ITEM_EDIT_GUIDE)
            pos = modox.LocatorUtils.getItemPosition(lastWheelGuide.modoItem, action=lx.symbol.s_ACTIONLAYER_SETUP)
            pos.z -= pos.y * 2.5
        else:
            width, height, length = bodyModule.dimensions
            pos = modo.Vector3()
            pos.x = width * -0.5  # place guide on the right (negative) side
            pos.y = height * 0.3  # let wheel be 1/3 of the car height by default
            pos.z = length * -0.35

        wheelGuide = axleModule.getKeyItem(self._KEY_ITEM_EDIT_GUIDE)
        modox.LocatorUtils.setItemPosition(wheelGuide.modoItem,
                                           pos,
                                           action=lx.symbol.s_ACTIONLAYER_SETUP)

    def _removeAxles(self, targetCount, axlesList):
        removeCount = len(axlesList) - targetCount
        for x in range(removeCount):
            modToRemove = axlesList.pop(-1)
            modToRemove.selfDelete()


class CmdSelectPathMesh(rs.base_ModuleCommand):

    descIdentifier = 'cmdselpmesh'
    descUsername = 'selPathMesh'
    descScope = rs.base_ModuleProperty.Scope.GLOBAL
    descTooltipMsgTableKey = 'carSelPathMesh'

    def run(self, arguments):
        bodyModule = BodyModule(self.module.rootItem)
        meshItem = bodyModule.pathMesh.modoItem
        lx.out('mesh item %s' % meshItem.name)
        modox.ItemSelection().set(meshItem, selMode=modox.SelectionMode.ADD)


class CmdSetPathFromSelected(rs.base_ModuleCommand):

    descIdentifier = 'cmdsetpath'
    descUsername = 'setPathFromMesh'
    descScope = rs.base_ModuleProperty.Scope.GLOBAL
    descTooltipMsgTableKey = 'carSetPathFromMesh'

    def run(self, arguments):
        itemSel = modox.ItemSelection()
        selectedMeshes = itemSel.getOfTypeModo(modo.c.MESH_TYPE)
        if not selectedMeshes:
            return
        sourceMesh = selectedMeshes[0]

        bodyModule = BodyModule(self.module.rootItem)
        targetMesh = bodyModule.pathMesh.modoItem

        itemSel.set(sourceMesh, selMode=modox.SelectionMode.REPLACE)
        rs.run('select.type polygon')
        rs.run('copy')

        itemSel.set(targetMesh, selMode=modox.SelectionMode.REPLACE)
        rs.run('select.type polygon')
        rs.run('delete')
        rs.run('paste')


class CarOnPathModule(rs.base_FeaturedModule):

    descIdentifier = 'std.pathCarBody'
    descUsername = 'Car Body'
    descFeatures = [PropFrontAxle,
                    PropRearAxles,
                    modox.c.FormCommandList.DIVIDER,
                    CmdSelectPathMesh,
                    CmdSetPathFromSelected]
