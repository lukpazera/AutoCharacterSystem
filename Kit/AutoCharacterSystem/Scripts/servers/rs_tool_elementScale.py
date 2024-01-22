

import lx
import lxifc
import lxu.attributes
import lxu.select

import modo
import modox

import rs


iPART_SCALE = 1032


class ToolContext(object):
    RIG = 1
    MODULE = 2
    SELECTION = 3


# ------------ EDIT SETS

class base_ToolEditSet(object):

    # -------- Interface to implement
    
    attributes = None

    def getChannelsFromRig(self, rig):
        """ Returns a list of all rig channels that the tool should operate on.

        Returns
        -------
        list[ToolEditChannelData]
        """
        return []

    def getChannelsFromModoItems(self, modoItems):
        """ Returns a list of channels from given modo items that the tools should operate on.

        Returns
        -------
        list[ToolEditChannelData]
        """
        return []


class ToolEditChannelData:
    """
    Contains data about a channel that should be evaluated by the tool
    """

    def __init__(self, item=lx.object.Item(), chanIndex=-1, chanRefValue=None):
        
        self.item = item
        self.chanIndex = chanIndex
        self.chanRefValue = chanRefValue


class GuideResizeEditSet(base_ToolEditSet):
    """
    Edit set for resizing guides.
    """
    def getChannelsFromRig(self, rig):
        guides = rig.getElements(rs.c.ElementSetType.CONTROLLER_GUIDES)
        return self._getChannels(guides, entireGuide=True)

    def getChannelsFromModoItems(self, modoItems):
        """
        This handles item selection.
        What we need to do is scan selection and see to which modules selected items belong.
        Then only scale controller guides from these modules.
        """
        return []

    # -------- Private methods

    def _getChannels(self, modoItems, entireGuide=True):
        channels = []

        for guide in modoItems:

            try:
                guideRigItem = rs.GuideItem(guide)
            except TypeError:
                continue

            # We only want to affect root guides.
            # And only ones that are not linked to another module.
            if not guideRigItem.isRootGuide:
                continue
            if guideRigItem.isTransformLinked:
                continue

            loc = modo.LocatorSuperType(guide.internalItem)

            pos = modo.Vector3(loc.position.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_EDIT))
            scl = modo.Vector3(loc.scale.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_EDIT))

            # Position
            xfrmItem = loc.position
            xfrmInternal = xfrmItem.internalItem
            ix = xfrmItem.channel("pos.X").index
            iy = xfrmItem.channel("pos.Y").index
            iz = xfrmItem.channel("pos.Z").index

            channels.append(ToolEditChannelData(xfrmInternal, ix, pos.x))
            channels.append(ToolEditChannelData(xfrmInternal, iy, pos.y))
            channels.append(ToolEditChannelData(xfrmInternal, iz, pos.z))

            # Scale
            xfrmItem = loc.scale
            xfrmInternal = xfrmItem.internalItem
            ix = xfrmItem.channel("scl.X").index
            iy = xfrmItem.channel("scl.Y").index
            iz = xfrmItem.channel("scl.Z").index

            channels.append(ToolEditChannelData(xfrmInternal, ix, scl.x))
            channels.append(ToolEditChannelData(xfrmInternal, iy, scl.y))
            channels.append(ToolEditChannelData(xfrmInternal, iz, scl.z))

        return channels


class GuideResizeShapesEditSet(base_ToolEditSet):
    """
    Edit set for resizing just guide shapes.
    """

    def getChannelsFromRig(self, rig):
        guides = rig.getElements(rs.c.ElementSetType.CONTROLLER_GUIDES)
        return self._getChannels(guides)

    def getChannelsFromModoItems(self, modoItems):
        """
        This handles item selection.
        What we need to do is scan selection and see to which modules selected items belong.
        Then only scale controller guides from these modules.
        """
        return self._getChannels(modoItems)

    # -------- Private methods

    def _getChannels(self, modoItems):
        channels = []

        for guide in modoItems:

            try:
                guideRigItem = rs.GuideItem(guide)
            except TypeError:
                continue

            chanNames = []
            if guide.internalItem.PackageTest("rs.pkg.guide"):
                chanNames = ['rsgdRadius']

            if guide.internalItem.PackageTest("rs.pkg.itemAxis"):
                chanNames.extend(['rsiaWidth', 'rsiaHeight', 'rsiaLength',
                                  'rsiaOffset.X', 'rsiaOffset.Y', 'rsiaOffset.Z',
                                  'rsiaShiftX', 'rsiaShiftY', 'rsiaShiftZ'])

            if guide.internalItem.PackageTest("glItemShape"):
                chanNames.extend(['isRadius', 'isSize.X', 'isSize.Y', 'isSize.Z',
                                  'isOffset.X', 'isOffset.Y', 'isOffset.Z'])

            for name in chanNames:
                chan = guide.channel(name)
                if chan is None:
                    continue
                v = chan.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_EDIT)
                channels.append(ToolEditChannelData(guide.internalItem, chan.index, v))

        return channels


class ControllersResizeEditSet(base_ToolEditSet):

    def getChannelsFromRig(self, rig):
        ctrls = rig.getElements(rs.c.ElementSetType.CONTROLLERS)
        decorators = rig.getElements(rs.c.ElementSetType.DECORATORS)
        
        return self._getChannelDataFromControllers(ctrls + decorators)

    def getChannelsFromModoItems(self, modoItems):
        ctrls = []
        
        includeMe = False
        
        for modoItem in modoItems:
            try:
                ctrlFeature = rs.Controller(modoItem)
            except TypeError:
                pass
            else:
                includeMe = True
            
            if not includeMe:
                try:
                    decoratorFeature = rs.DecoratorIF(modoItem)
                except TypeError:
                    pass
                else:
                    if rs.c.Context.ANIMATE in decoratorFeature.contexts:
                        includeMe = True
            
            if includeMe:
                ctrls.append(modoItem)
        
        return self._getChannelDataFromControllers(ctrls)

    # -------- Private methods
        
    def _getChannelDataFromControllers(self, ctrls):
        channels = []
        
        for ctrl in ctrls:
            chanNames = []
            if ctrl.internalItem.PackageTest("glItemShape"):
                chanNames = ['isRadius', 'isSize.X', 'isSize.Y', 'isSize.Z', 'isOffset.X', 'isOffset.Y', 'isOffset.Z']
            if ctrl.internalItem.PackageTest("glLinkShape"):
                chanNames.extend(['lsRadius', 'lsWidth', 'lsHeight', 'lsOffsetS', 'lsOffsetE'])

            if chanNames:
                for name in chanNames:
                    chan = ctrl.channel(name)
                    if chan is None:
                        continue
                    v = chan.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_EDIT)
                    channels.append(ToolEditChannelData(ctrl.internalItem, chan.index, v))

        return channels


class SkeletonResizeEditSet(base_ToolEditSet):

    def getChannelsFromRig(self, rig):
        items = rig.getElements(rs.c.ElementSetType.BIND_SKELETON)
        return self.getChannelsFromModoItems(items)
    
    def getChannelsFromModoItems(self, modoItems):
        channels = []

        for modoItem in modoItems:
            chanNames = []

            # try:
            #     rs.BindLocatorItem(modoItem)
            # except TypeError:
            #     continue

            if modoItem.internalItem.PackageTest("glItemShape"):
                chanNames.extend(['isRadius', 'isSize.X', 'isSize.Y', 'isSize.Z', 'isOffset.X', 'isOffset.Y', 'isOffset.Z'])
                
            if modoItem.internalItem.PackageTest("glLinkShape"):
                chanNames.extend(['lsRadius', 'lsWidth', 'lsHeight', 'lsOffsetS', 'lsOffsetE'])
                    
            for name in chanNames:
                chan = modoItem.channel(name)
                if chan is None:
                    continue
                v = chan.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_EDIT)
                channels.append(ToolEditChannelData(modoItem.internalItem, chan.index, v))

        return channels


class PlugsSocketsResizeEditSet(base_ToolEditSet):

    def getChannelsFromRig(self, rig):
        items = rig.getElements(rs.c.ElementSetType.PLUGS)
        items.extend(rig.getElements(rs.c.ElementSetType.SOCKETS))

        return self.getChannelsFromModoItems(items)

    def getChannelsFromModoItems(self, modoItems):
        channels = []

        for modoItem in modoItems:
            chanNames = []

            # Test against plug/socket
            plugOrSocket = False
            try:
                plug = rs.PlugItem(modoItem)
            except TypeError:
                pass
            else:
                plugOrSocket = True

            if not plugOrSocket:
                try:
                    socket = rs.SocketItem(modoItem)
                except TypeError:
                    pass
                else:
                    plugOrSocket = True

            if not plugOrSocket:
                continue

            if plugOrSocket:
                if modoItem.internalItem.PackageTest("rs.pkg.socket"):
                    chanNames.append("rsskDrawRadius")

            if modoItem.internalItem.PackageTest("glItemShape"):
                chanNames.extend(
                    ['isRadius', 'isSize.X', 'isSize.Y', 'isSize.Z', 'isOffset.X', 'isOffset.Y', 'isOffset.Z'])

            if modoItem.internalItem.PackageTest("glLinkShape"):
                chanNames.extend(['lsRadius', 'lsWidth', 'lsHeight', 'lsOffsetS', 'lsOffsetE'])

            for name in chanNames:
                chan = modoItem.channel(name)
                if chan is None:
                    continue
                v = chan.get(time=0.0, action=lx.symbol.s_ACTIONLAYER_EDIT)
                channels.append(ToolEditChannelData(modoItem.internalItem, chan.index, v))

        return channels


# ------------ TOOLS

class base_ElementScaleTool(lxifc.Tool, lxifc.ToolModel, lxu.attributes.DynamicAttributes):
    """
    Base class for all the tools that are meant to scale channels of some rig elements
    such as guides, plugs, sockets, controllers, etc.
    """
    # -------- Abstract methods to implement
    
    @property
    def editSetClass(self):
        """
        Needs to return edit set that should be evaluated live.

        Returns
        -------
        base_ToolEditSet
        """
        return None

    @property
    def dropEditSetClass(self):
        """
        Returns edit set (or multiple edit sets) that should be evaluated once
        when the tool is dropped. The changes to these edit sets will not be live.

        Returns
        -------
        base_ToolEditSet, [base_ToolEditSet]
        """
        return None

    def start(self):
        """ Called when the tool is initially started.
        
        This usually has to set channels data.
        """
        self.setChannelsData()
        
    # -------- Public interface
    
    def setChannelsData(self, attributes=None):
        self._toolChannels = []
        editSet = self.editSetClass()
        editSet.attributes = attributes

        channelsData = []
        selected = modo.Scene().selected
        if selected:
            channelsData = editSet.getChannelsFromModoItems(selected)
            
        if not channelsData:
            rig = rs.Scene().editRig
            channelsData = editSet.getChannelsFromRig(rig)

        for chanData in channelsData:
            # We skip channels with value 0, it makes no sense to scale them.
            if chanData.chanRefValue == 0.0:
                continue
            self._toolChannels.append(chanData)

    # -------- Tool Interface

    def tmod_Initialize(self,vts,adjust,flags):
        adj_tool = lx.object.AdjustTool(adjust)
        adj_tool.SetFlt(0, 1.0)

        scene = lx.object.Scene(lxu.select.SceneSelection().current())
        self.chan_read = lx.object.ChannelRead(scene.Channels(lx.symbol.s_ACTIONLAYER_EDIT, 0.0))
        self.chan_write = lx.object.ChannelWrite(scene.Channels(lx.symbol.s_ACTIONLAYER_EDIT, 0.0))

        self.start()
        
    def tool_Reset(self):
        self.attr_SetFlt(0, 1.0)
        self.cur_scale = 1.0
        
        try:
            self.reset()
        except AttributeError:
            pass

    def tool_Evaluate(self,vts):
        size_attr = self.attr_GetFlt(0)
        self.cur_scale = size_attr

        self._evaluateChannelsDataList(self._toolChannels)

    def tmod_Drop(self):
        """
        This is called once when the tool is dropped.
        It should apply any chances that are related to the tool but do not need to be
        performed in real time.
        """
        dropEditSets = self.dropEditSetClass
        if dropEditSets is None:
            return
        if type(dropEditSets) not in (list, tuple):
            dropEditSets = [dropEditSets]

        editChanDataList = []
        for editSet in dropEditSets:
            chansData = self._getChannelsDataListFromEditSet(editSet)
            editChanDataList.extend(chansData)

        # eval channels
        self._evaluateChannelsDataList(editChanDataList)

    def tool_VectorType(self):
        return self.vector_type
 
    def tool_Order(self):
        return lx.symbol.s_ORD_ACTR
 
    def tool_Task(self):
        return lx.symbol.i_TASK_ACTR
 
    def tmod_Flags(self):
        return lx.symbol.fTMOD_I0_ATTRHAUL | lx.symbol.fTMOD_I0_INPUT #| lx.symbol.fTMOD_DRAW_3D
                
    def tmod_Haul(self,index):
        if index == 0:
            return "size"
        else:
            return 0

    # -------- Private methods

    def _getChannelsDataListFromEditSet(self, editSetClass):
        """
        This is only really used when getting the list of channels to edit when the tool is dropped.
        """
        rig = rs.Scene().editRig

        channelsToEdit = []
        for chanData in editSetClass().getChannelsFromRig(rig):
            # We skip channels with value 0, it makes no sense to scale them.
            if chanData.chanRefValue == 0.0:
                continue
            channelsToEdit.append(chanData)

        return channelsToEdit

    def _evaluateChannelsDataList(self, chansDataList):
        if not chansDataList:
            return

        # start = clock()

        for data in chansDataList:
            newVal = data.chanRefValue * self.cur_scale
            self.chan_write.Double(data.item, data.chanIndex, newVal)

        # end = clock()
        # lx.out(end-start)

    def __init__(self):
        lxu.attributes.DynamicAttributes.__init__(self)
 
        # Single size attribute
        self.dyna_Add('size', lx.symbol.sTYPE_PERCENT)
        self.attr_SetFlt(0,1.0)
 
        packet_service = lx.service.Packet()
        self.vector_type = lx.object.VectorType(packet_service.CreateVectorType(lx.symbol.sCATEGORY_TOOL))
        packet_service.AddPacket(self.vector_type, lx.symbol.sP_TOOL_INPUT_EVENT, lx.symbol.fVT_GET)
        packet_service.AddPacket(self.vector_type, lx.symbol.sP_TOOL_EVENTTRANS, lx.symbol.fVT_GET)
        
        self.chan_read = lx.object.ChannelRead()
        self.chan_write = lx.object.ChannelWrite()
        
        try:
            self.init()
        except AttributeError:
            pass
        
        self.tool_Reset()


# ------------ TOOL IMPLEMENTATIONS

class GuideScaleTool(base_ElementScaleTool):

    @property
    def editSetClass(self):
        return GuideResizeEditSet

    def tmod_Drop(self):
        """
        Guide scale tool only needs to perform drop operation if guides transforms were affected.
        """
        # Edits have to be applied since freezing is I think working off setup
        # and edits are made to edit action.
        # TODO: Clean up all the setup/edit stuff one day and make it consistent.
        modox.TransformUtils.applyEdit()

        # When the tool is dropped we need to scale all item drawing accordingly so it doesn't
        # get out of sync with guide scale.
        factor = self.cur_scale
        editRig = rs.Scene().editRig
        rs.Guide(editRig).freezeScale()
        rs.RigSizeOperator(editRig).referenceSize *= factor

        base_ElementScaleTool.tmod_Drop(self)

lx.bless(GuideScaleTool, "rs.guideScale")


class GuideScaleShapesTool(base_ElementScaleTool):

    @property
    def editSetClass(self):
        return GuideResizeShapesEditSet

lx.bless(GuideScaleShapesTool, "rs.guideScaleShapes")


class ControllersResizeTool(base_ElementScaleTool):

    @property
    def editSetClass(self):
        return ControllersResizeEditSet

lx.bless(ControllersResizeTool, "rs.ctrlsResize")


class SkeletonResizeTool(base_ElementScaleTool):

    @property
    def editSetClass(self):
        return SkeletonResizeEditSet

lx.bless(SkeletonResizeTool, "rs.skeletonResize")


class PlugsSocketsResizeTool(base_ElementScaleTool):

    @property
    def editSetClass(self):
        return PlugsSocketsResizeEditSet

lx.bless(PlugsSocketsResizeTool, "rs.plugsocResize")