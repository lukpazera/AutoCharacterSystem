
import lx
import modo
import modox
from modox import ItemUtils
from ..item import Item
from .. import const as c
from ..log import log
from ..util import run
from ..xfrm_link import TransformLink
from ..core import service


class GuideItem(Item):

    GRAPH_SYMMETRY = 'rs.symmetricGuide'

    descType = c.RigItemType.GUIDE
    descUsername = 'Guide'
    descModoItemType = 'locator'
    descFixedModoItemType = False
    descDefaultName = 'Guide'
    descPackages = ['rs.pkg.guide', 'rs.pkg.generic']
    descItemCommand = c.ItemCommand.GENERIC
    descDropScriptSource = c.DropScript.ITEM_ON_ITEM_SOURCE
    descDropScriptDestination = c.DropScript.ITEM_ON_ITEM_DESTINATION

    CHAN_DRAW_SHAPE = 'rsgdDraw'

    @property
    def symmetricGuide(self):
        """ Gets a symmetry reference guide for this guide.
        
        Returns
        -------
        GuideItem or None
        """
        graph = self.modoItem.itemGraph(self.GRAPH_SYMMETRY)
        fwd = graph.forward()
        if fwd:
            try:
                return GuideItem(fwd[0])
            except TypeError:
                pass
        return None

    @symmetricGuide.setter
    def symmetricGuide(self, guideItem):
        """ Sets new symmetry reference guide.
        
        This guide will keep its transforms symmetric to the given guide
        each time the guide is updated.
        
        Parameters
        ----------
        guideModoItem : GuideItem, modo.Item, None
            Either rig guide item or modo item that acts as symmetry reference
            for this guide. Pass None to clear current symmetric guide link.
        
        Raises
        ------
        TypeError
            When bad item was passed.
        """
        if guideItem is None:
            ItemUtils.clearForwardGraphConnections(self.modoItem, self.GRAPH_SYMMETRY)
            return

        if isinstance(guideItem, GuideItem):
            guideModoItem = guideItem.modoItem
        elif isinstance(guideItem, modo.Item):
            guideModoItem = guideItem
        else:
            raise TypeError

        ItemUtils.clearForwardGraphConnections(self.modoItem, self.GRAPH_SYMMETRY)

        guideGraph = self.modoItem.itemGraph(self.GRAPH_SYMMETRY)
        driverGraph = guideModoItem.itemGraph(self.GRAPH_SYMMETRY)
        guideGraph >> driverGraph

    @property
    def symmetryTargetGuide(self):
        """ Gets a guide for which this guide is the symmetry reference.

        Returns
        -------
        GuideItem or None
        """
        graph = self.modoItem.itemGraph(self.GRAPH_SYMMETRY)
        rev = graph.reverse()
        if rev:
            try:
                return GuideItem(rev[0])
            except TypeError:
                pass
        return None

    def setLockFromEdit(self, state):
        if state:
            self.drawShape = False
            self.setChannelProperty('select', 2)
        else:
            self.drawShape = True
            self.setChannelProperty('select', 0)

    @property
    def drawShape(self):
        return self.getChannelProperty(self.CHAN_DRAW_SHAPE)

    @drawShape.setter
    def drawShape(self, state):
        self.setChannelProperty(self.CHAN_DRAW_SHAPE, state)

    @property
    def isRootGuide(self):
        """
        Tests whether this guide is root guide.

        That means the guide is parented directly to the edit guides folder.

        Returns
        -------
        bool
        """
        parentItem = self.modoItem.parent
        if parentItem is None:
            return False

        try:
            parentRigItem = Item.getFromModoItem(parentItem)
        except TypeError:
            return False

        return parentRigItem.identifier == c.KeyItem.EDIT_GUIDE_FOLDER

    @property
    def isAttachedToOther(self):
        """
        Tests whether this guide is attached to some other guide.

        Returns
        -------
        bool
        """
        try:
            link = TransformLink(self.modoItem)
        except TypeError:
            return False
        return link.type == c.TransformLinkType.WORLD_POS_PERMANENT

    @property
    def attachTarget(self):
        """
        Gets the guide this guide is attached to.

        Returns
        -------
        GuideItem, None
        """
        try:
            xfrmLink = TransformLink(self.modoItem)
        except TypeError:
            return None
        return GuideItem(xfrmLink.driverItem)

    @attachTarget.setter
    def attachTarget(self, otherGuide):
        """
        Attaches this guide to another guide.

        Parameters
        ----------
        otherGuide : GuideItem, None
            The guide to attach to.
            When None is passed this clears the attachment link.
        """
        # Remove any existing links keeping item's world transforms first.
        try:
            xfrmLink = TransformLink(self.modoItem)
        except TypeError:
            pass
        else:
            xfrmLink.remove()

        # When guide is None
        # it means all we wanted to do is remove existing link
        # so we can return early.
        if otherGuide is None:
            return

        TransformLink.new(self.modoItem, otherGuide.modoItem, c.TransformLinkType.WORLD_POS_PERMANENT, compensation=False)

    def detachAllAttachedGuides(self):
        """
        Detaches all guides that are attached to this gude in one go.
        """
        links = TransformLink.getLinkedTransformLinksFromTarget(self.modoItem, c.TransformLinkType.WORLD_POS_PERMANENT)
        for link in links:
            try:
                GuideItem(link.drivenItem).setLockFromEdit(False)
            except TypeError:
                pass
            link.remove()

    @property
    def hasOtherGuidesAttached(self):
        return len(TransformLink.getLinkedTransformLinksFromTarget(self.modoItem, c.TransformLinkType.WORLD_POS_PERMANENT)) > 0

    @property
    def isTransformLinked(self):
        """
        Tests whether this guide has its transforms linked to another guide.

        Returns
        -------
        bool
        """
        try:
            link = TransformLink(self.modoItem)
        except TypeError:
            return False
        return link.type == c.TransformLinkType.DYNA_PARENT

    @property
    def transformLinkedGuide(self):
        """
        Gets the guide this guide is linked to.

        Returns
        -------
        Guide, None
        """
        try:
            xfrmLink = TransformLink(self.modoItem)
        except TypeError:
            return None
        return GuideItem(xfrmLink.driverItem)

    @transformLinkedGuide.setter
    def transformLinkedGuide(self, guide):
        """
        Links this guide to another guide.

        This guide has to be root guide.
        Another guide has to belong to different module within same rig.

        Parameters
        ----------
        guide : GuiteItem, None
            Pass none to remove the link (if any exists).
            When removing link world transform of the guide will be preserved.
        """
        # Don't do anything if target guide is not None and is not compatible
        # with this property.
        # TODO: Consider these checks, when doing connections through code on purpose
        # TODO: it may undesirable that this doesn't allow for full control.
        if guide is not None:
            if not self.isRootGuide:
                return
            if self.rigRootItem != guide.rigRootItem:
                return
            if self.side == c.Side.CENTER and guide.side != self.side:
                return
            if self.side == c.Side.LEFT and guide.side == c.Side.RIGHT:
                return
            if self.side == c.Side.RIGHT and guide.side == c.Side.LEFT:
                return
        else:
            if not self.isTransformLinked:
                return

        # We want to apply transform to guide so it doesn't jump - if possible.
        # So backup world transform first.
        wposVec = modox.LocatorUtils.getItemWorldPositionVector(self.modoItem)
        wrotMtx = modox.LocatorUtils.getItemWorldRotation(self.modoItem)
        wsclVec = modox.LocatorUtils.getItemWorldScaleVector(self.modoItem)

        wxfrm = modox.LocatorUtils.getItemWorldTransform(self.modoItem)

        # Remove any existing links keeping item's world transforms first.
        try:
            xfrmLink = TransformLink(self.modoItem)
        except TypeError:
            pass
        else:
            xfrmLink.remove()
            # Reapply world transforms
            modox.TransformUtils.applyTransform(self.modoItem,
                                                wposVec,
                                                wrotMtx,
                                                wsclVec,
                                                mode=lx.symbol.iLOCATOR_WORLD,
                                                action=lx.symbol.s_ACTIONLAYER_SETUP)

        # When guide is None  or root guide was dragged onto guide from the same module
        # it means all we wanted to do is remove existing link
        # so we can return early.
        if guide is None or self.moduleRootItem == guide.moduleRootItem:
            # Send an event so the rest of the guide can react if needed.
            service.events.send(c.EventTypes.GUIDE_LINK_CHANGED, guide=self)
            return

        parentInvWxfrm = modox.LocatorUtils.getItemWorldTransform(guide.modoItem)
        parentInvWxfrm.invert()
        lxfrm = wxfrm * parentInvWxfrm
        lrot = modo.Matrix3(lxfrm.asRotateMatrix())
        lpos = modo.Vector3(lxfrm.position)
        lscl = lxfrm.scale() # vector3

        # Transform link is added with no compensation.
        # This is because we're going to set linked guide local transforms manually anyway.
        # We do not want any offset in dynamic parent setup.
        # We want all child transforms to be on the linked guide item local transform itself.
        TransformLink.new(self.modoItem, guide.modoItem, c.TransformLinkType.DYNA_PARENT, compensation=False)

        # Reapply world transforms
        # we have to do this in local mode because world doesn't work with dyna parent here.
        modox.TransformUtils.applyTransform(self.modoItem,
                                            lpos,
                                            lrot,
                                            lscl,
                                            mode=lx.symbol.iLOCATOR_LOCAL,
                                            action=lx.symbol.s_ACTIONLAYER_SETUP)

        # Send an event so the rest of the guide can react if needed.
        service.events.send(c.EventTypes.GUIDE_LINK_CHANGED, guide=self)

    def onAdd(self, subtype):
        # Set guide in hierarchy automatically
        #ItemUtils.autoPlaceInChain(self.modoItem, modo.Vector3(0.0, 0.0, 0.2))

        modoItem = self.modoItem
        ident = modoItem.id

        if not modoItem.internalItem.PackageTest("glItemShape"):
            modoItem.PackageAdd("glItemShape")

        if not modoItem.internalItem.PackageTest("glLinkShape"):
            modoItem.PackageAdd("glLinkShape")

        # Set shape
        run('!channel.value custom channel:{%s:drawShape}' % ident)
        run('!channel.value circle channel:{%s:isShape}' % ident)
        run('!channel.value true channel:{%s:isAlign}' % ident)
        run('!channel.value 0.005 channel:{%s:isRadius}' % ident)

        # Set link shape
        run('!channel.value custom channel:{%s:link}' % ident)
        run('!channel.value rhombus channel:{%s:lsShape}' % ident)
        run('!channel.value true channel:{%s:lsSolid}' % ident)
        run('!channel.value true channel:{%s:lsAuto}' % ident)

        run('!rs.item.color guide1 autoAdd:true item:{%s}' % ident)

        run('select.item {%s} set' % ident)
        run('item.editorColor ultramarine')

    def onDroppedOnItem(self, destinationItem, context):
        """
        Adds support for drop actions, this guide is dropped onto another item.

        When guide is dropped onto another guide we're trying to set up or
        break guides transform link. Dropping guide on another guide from
        the same module will break the link.
        """
        # We support dropping on other guides for now only.
        try:
            targetGuide = GuideItem(destinationItem)
        except TypeError:
            return

        run('rs.guide.link {%s} {%s}' % (self.modoItem.id, targetGuide.modoItem.id))


class ReferenceGuideItem(Item):

    descType = c.RigItemType.REFERENCE_GUIDE
    descUsername = 'Reference Guide'
    descModoItemType = 'locator'
    descFixedModoItemType = True
    descDefaultName = 'RefGuide'
    descPackages = ['rs.pkg.generic']
