

import lx
import modo

from ..item import Item
from ..items.bind_loc import BindLocatorItem
from .. import const as c
from ..log import log


class BindLocatorShadow(Item):
    """ Bind locator shadow is a single item in the shadow bind skeleton.
    
    Bind locator shadow has identifier set to ident of its source bind locator modo item.
    """
    
    GRAPH_NAME = 'rs.bindLocShadow'

    descType = c.RigItemType.BIND_LOCATOR_SHADOW
    descUsername = 'Bind Locator Shadow'
    descDefaultName = 'BindLocatorShadow'
    descModoItemType = 'locator'
    descPackages = ['rs.pkg.generic']
    descSynthName = False

    def onAdd(self, subtype):
        modoItem = self.modoItem
        ident = modoItem.id

        if not modoItem.internalItem.PackageTest("glItemShape"):
            modoItem.PackageAdd("glItemShape")

        if not modoItem.internalItem.PackageTest("glLinkShape"):
            modoItem.PackageAdd("glLinkShape")

        # Set shape
        lx.eval('!channel.value custom channel:{%s:drawShape}' % ident)
        lx.eval('!channel.value circle channel:{%s:isShape}' % ident)
        lx.eval('!channel.value true channel:{%s:isAlign}' % ident)
        lx.eval('!channel.value 0.005 channel:{%s:isRadius}' % ident)

        # Set link shape
        lx.eval('!channel.value custom channel:{%s:link}' % ident)
        lx.eval('!channel.value box channel:{%s:lsShape}' % ident)
        lx.eval('!channel.value true channel:{%s:lsSolid}' % ident)
        lx.eval('!channel.value true channel:{%s:lsAuto}' % ident)
        
        # Set item color.
        lx.eval('select.item {%s} set' % ident)
        lx.eval('item.editorColor orange')

    @property
    def sourceBindLocator(self):
        """ Gets source bind locator for this shadow.
        
        Returns
        -------
        BindLocatorItem or None
        """
        graph = self.modoItem.itemGraph(self.GRAPH_NAME)
        try:
            return BindLocatorItem(graph.forward(0))
        except LookupError:
            return None
        except TypeError:
            return None
    
    @sourceBindLocator.setter
    def sourceBindLocator(self, bindLocatorItem):
        """ Sets bind locator source for this shadow.
        
        Parameters
        ----------
        bindLocatorItem : BindLocatorItem
        """
        shadowGraph = self.modoItem.itemGraph(self.GRAPH_NAME)
        sourceGraph = bindLocatorItem.modoItem.itemGraph(self.GRAPH_NAME)
        shadowGraph >> sourceGraph
    
    def matchToSource(self):
        lx.eval('!item.match item pos average:false item:{%s} itemTo:{%s}' % (self.modoItem.id, self.sourceBindLocator.modoItem.id))
        lx.eval('!item.match item rot average:false item:{%s} itemTo:{%s}' % (self.modoItem.id, self.sourceBindLocator.modoItem.id))
        lx.eval('!item.match item scl average:false item:{%s} itemTo:{%s}' % (self.modoItem.id, self.sourceBindLocator.modoItem.id))
    
    @classmethod
    def newFromBindLocator(cls, bindloc, name):
        """ Creates new bind locator shadow from source bind locator.
        
        Parameters
        ----------
        bindloc : BindLocatorItem
        """
        shadow = cls.new(name)
        shadow.identifier = bindloc.modoItem.id
        shadow.sourceBindLocator = bindloc
        return shadow