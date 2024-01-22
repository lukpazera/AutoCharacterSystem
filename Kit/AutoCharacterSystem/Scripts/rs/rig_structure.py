

import modo

from . import const as c
from .rig_template import RigTemplate
from .rig_template import HierarchyNode
from .component_setups.rig import RigComponentSetup
from .component import Component
from .core import service


class RigStructure(object):
    """ Rig structure governs components and how they are arranged within the rig.
    """
    
    TAG_COMPONENT = 'RSCM'

    def newComponent(self, componentClass):
        """ Adds new component to the rig.
        
        Parameters
        ----------
        componentClass : Component, str
            Eigher class of a component to add or its string identifier.
            
        Returns
        -------
        Component
        
        Raises
        ------
        TypeError
            If bad component class or ident was passed.
        """
        if isinstance(componentClass, str):
            try:
                componentClass = service.systemComponent.get(c.SystemComponentType.COMPONENT, componentClass)
            except LookupError:
                raise TypeError
        
        if not issubclass(componentClass, Component):
            raise TypeError
        
        component = componentClass.new()
        self.addComponent(component)
        return component
        
    def addComponent(self, component):
        """ Adds existing component to the rig.
        
        Component will be added according to the template.
        """
        self._setup.addSetup(component.setup)
        self._placeWithinTemplate(component)
        self._linkComponent(component)
        component.updateItemNames()
    
    @property
    def components(self):
        """ Gets all rig components.
        
        Returns
        -------
        list of Component
        """
        componentSetups = self._setup.subsetups
        componentRoots = [setup.rootModoItem for setup in componentSetups]

        components = []
        for root in componentRoots:
            try:
                compid = root.readTag(self.TAG_COMPONENT)
            except LookupError:
                continue
            try:
                componentClass = service.systemComponent.get(c.SystemComponentType.COMPONENT, compid)
            except LookupError:
                continue
            
            try:
                components.append(componentClass(root))
            except TypeError:
                continue
        return components

    def getComponents(self, identifier):
        """ Gets all rig components with a given identifier.
        
        Parameters
        ----------
        identifier : Component class, str
            Either component class or its string identifier.
            
        Returns
        -------
        list of Component
            List will be empty if components cannot be found.
        """
        if isinstance(identifier, str):
            try:
                componentClass = service.systemComponent.get(c.SystemComponentType.COMPONENT, identifier)
            except LookupError:
                return []
        else:
            componentClass = identifier
        
        # If components have lookup graph - use it to find components.
        # If not, scan first level children of the root assembly.
        if componentClass.descLookupGraph is not None:
            componentRoots = self._root.getLinkedItems(componentClass.descLookupGraph)
        else:
            componentSetups = self._setup.getSubsetupsOfType(componentClass.descComponentSetupClass)
            componentRoots = [setup.rootModoItem for setup in componentSetups]
        
        # Filter out any components that do not have right identifier.
        # This is especially important when getting components by graph.
        # Mutlitple types of components may be linked with the same graph (attachments)
        components = []
        for root in componentRoots:
            try:
                compid = root.readTag(self.TAG_COMPONENT)
            except LookupError:
                continue
            if compid == componentClass.descIdentifier:
                components.append(componentClass(root))
        return components

    def getComponentsByGraph(self, graphName):
        """ Gets all components that are linked with rig on a given graph.
        
        Note that this may return components of different types!
        
        Parameters
        ----------
        graphName : str
        
        Returns
        -------
        list of Component, empty list
        """
        if not graphName:
            return []
        componentRoots = self._root.getLinkedItems(graphName)
        
        components = []
        for root in componentRoots:
            try:
                compid = root.readTag(self.TAG_COMPONENT)
            except LookupError:
                continue
            try:
                componentClass = service.systemComponent.get(c.SystemComponentType.COMPONENT, compid)
            except LookupError:
                continue
            try:
                component = componentClass(root)
            except TypeError:
                continue
            components.append(component)
        return components
        
    def removeComponent(self, component):
        """ Removes component from rig structure.
        
        This does not delete the component itself. It only removes it from
        the structure together with any other items that serve no purpose
        if the component is not in there.
        """
        # Find component in the structure by its ident.
        # Get its parent.
        
        # If parent is optional check if it has any children.
        # If it doesn't remove the parent.
        # Now check parent of the parent, etc.
        pass
         
    # -------- Private methods
    
    def _getNodeParentChain(self, node):
        parents = []
        while node.parent is not None:
            parentNode = self._template.getNode(node.parent)
            parents.append(parentNode)
            node = parentNode
        return parents

    def _placeWithinTemplate(self, component):
        """ Places component within rig hierarchy template.
        """
        # Find component in the template using its identifier.
        # If it's not found then no need to do anything else.
        # We assume component identifiers and item identifiers won't clash.
        try:
            node = self._template.getNode(component.descIdentifier)
        except LookupError:
            return

        # Get all parent nodes of the component in the template.
        # We assume these will be items, not other components.
        parentsChain = self._getNodeParentChain(node)
        parentsChain.reverse()
        
        # We support template that is only 1 hierarchy level deep.
        # Components can be under root or right under next level folder item.
        # This needs to improved if needed at some point.
        childrenInScene = self._root.modoItem.children()
        existingParentRigItems = []
        for x in range(len(parentsChain)):
            parentNode = parentsChain[x]
            try:
                rigItemClass = service.systemComponent.get(c.SystemComponentType.ITEM, parentNode.identifier)
            except LookupError():
                break
            
            rigItem = None
            for modoItem in childrenInScene:
                try:
                    rigItem = rigItemClass(modoItem)
                    existingParentRigItems.append(rigItem)
                    break
                except TypeError:
                    continue
            
            # This creates new template item and integrates it
            # with the rig.
            if rigItem is None:
                newRigItem = rigItemClass.new()
                if x > 0:
                    newRigItem.modoItem.setParent(existingParentRigItems[x].modoItem)
                self._setup.addItem(newRigItem.modoItem)
                newRigItem.renderAndSetName()
                existingParentRigItems.append(newRigItem)

        # Add component to the proper place in hierarchy.
        # New component is added as last child (this is the -1 argument to setParent)
        if existingParentRigItems:
            component.rootModoItem.setParent(existingParentRigItems[-1].modoItem, -1)

    def _linkComponent(self, component):
        """ Links component with rig root if component has lookup graph set.
        """
        graphName = component.descLookupGraph
        if graphName is None:
            return
        self._root.linkItems(component.rootModoItem, graphName)

    def __init__(self, rigRootItem):
        self._root = rigRootItem
        self._setup = RigComponentSetup(self._root.modoItem)
        self._template = RigTemplate()
    
    