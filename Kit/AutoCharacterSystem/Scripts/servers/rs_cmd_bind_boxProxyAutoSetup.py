
import lx
import lxu
import modo
import modox

import rs


class CmdBoxProxyAutoSetup(rs.RigCommand):

    ARG_RESOLUTION_NAME = 'name'
    ARG_SIZE_FROM = 'sizeFrom'

    SIZE_FROM_HINTS = ((0, 'length'),
                       (1, 'link'),
                       (2, 'mesh'))

    def arguments(self):
        superArgs = rs.RigCommand.arguments(self)

        resNameArg = rs.cmd.Argument(self.ARG_RESOLUTION_NAME, 'string')
        resNameArg.defaultValue = 'Box Proxy'

        sizeArg = rs.cmd.Argument(self.ARG_SIZE_FROM, 'integer')
        sizeArg.defaultValue = 0
        sizeArg.hints = self.SIZE_FROM_HINTS

        return [resNameArg, sizeArg] + superArgs

    def execute(self, msg, flags):
        """ Main command execution code.

        Note that I'm using commands for setting and clearing vertex map selection.
        This is because using vertex map selection class from modox is somehow
        getting MODO in a bad state and eventually causing crash.
        """
        scene = modo.Scene()
        resolutionName = self.getArgumentValue(self.ARG_RESOLUTION_NAME)

        editRig = self.firstRigToEdit

        attachments = rs.Attachments(editRig)
        resolutions = rs.Resolutions(editRig.rootItem)
        resolutions.addResolution(resolutionName)
        bindSkeleton = rs.BindSkeleton(editRig)

        for bindloc in bindSkeleton.items:
            if bindloc.modoItem.childCount() == 0:
                continue

            #if not bindloc.isEffector:
            #    continue

            # Add unit cube mesh
            lx.eval('item.create mesh')
            mesh = scene.selected[0]
            mesh.name = "BoxProxy_" + bindloc.referenceUserName
            # Put unit cube into the layer
            lx.eval('script.run "macro.scriptservice:32235710027:macro"')

            child = bindloc.modoItem.childAtIndex(0, asSubType=False)

            itemWPos = modox.LocatorUtils.getItemWorldPositionVector(bindloc.modoItem)
            childWPos = modox.LocatorUtils.getItemWorldPositionVector(child)

            itemToChildVec = childWPos - itemWPos
            jointLength = itemToChildVec.length()

            boxPos = itemWPos + (itemToChildVec * 0.5)
            modox.LocatorUtils.setItemPosition(mesh, boxPos, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_EDIT)

            itemWRot = modox.LocatorUtils.getItemWorldRotation(bindloc.modoItem, transpose=False)
            eulerAnglesList = itemWRot.asEuler() # zxy order, in radians
            eulerAngles = modo.Vector3(eulerAnglesList[0], eulerAnglesList[1], eulerAnglesList[2])
            modox.LocatorUtils.setItemRotation(mesh, eulerAngles, 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_EDIT)

            # Set scale
            scaleZ = jointLength

            sizeFrom = self.getArgumentValue(self.ARG_SIZE_FROM)
            if sizeFrom == 0: # size from length:
                width = scaleZ * 0.3
                height = scaleZ * 0.3
            elif sizeFrom == 1: # from link
                if bindloc.modoItem.internalItem.PackageTest('glLinkShape'):
                    width = bindloc.modoItem.channel('lsWidth').get()
                    height = bindloc.modoItem.channel('lsHeight').get()
                else:
                    width = scaleZ * 0.3
                    height = scaleZ * 0.3
            elif sizeFrom == 2: # from mesh
                width = scaleZ * 0.3
                height = scaleZ * 0.3

            modox.LocatorUtils.setItemScale(mesh, modo.Vector3(width, height, scaleZ), 0.0, key=False, action=lx.symbol.s_ACTIONLAYER_EDIT)

            # Need to freeze scale before attaching
            # Attachments cannot have scale applied - or non uniform scale at least?
            modox.LocatorUtils.freezeTransforms(mesh, scale=True)

            # Attach to bind skeleton joint
            proxyRigItem = attachments.attachItem(mesh, bindloc.modoItem, rs.c.ComponentType.BIND_PROXIES)
            proxyRigItem.addToResolution(resolutionName)

        rs.Scene().contexts.refreshCurrent()

rs.cmd.bless(CmdBoxProxyAutoSetup, 'rs.bind.boxProxyAutoSetup')
