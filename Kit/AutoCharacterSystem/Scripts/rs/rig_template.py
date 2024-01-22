
""" Rig template interface.
"""


from .const import RigItemType as i
from .const import ComponentType as comp


class HierarchyNode(object):
    """ Single node in the hierarchy.
    
    Attributes
    ----------
    identifier : str
        Unique identifier of the node.
        
    parent : str
        Identifier of the parent node.
    
    childIndex : int
        Child index in the template hierarchy. Used to set order of items in the template
        on a given hierarchy level.
    
    children : list of str
        List of child node identifiers.
        
    optional : bool
        Whether this node is optional (is added to rig only when other nodes need it)
        or whether it should always be in the rig.
    """
    
    identifier = ''
    parent = None
    childIndex = 0
    children = []
    optional = False

    
class RigTemplate(object):
    """ Rig hierarchy template.
    
    Template defines how various rig components are laid out in
    hierarchical form in item list. By default when component is added to the rig
    its root item will be parented to rig's root item.
    With this template a different hierarchical arrangement can be laid out.
    Components cannot be nested but their root items can be parented to other items
    for organisational purposes.
    """
    
    @property
    def layout(self):
        """ Returns a list that defines rig hierarchical layout.
        
        A leading space characters can be used to define hierarchy relationship.
        '?' can be used to mark item as optional. If item is optional it does not
        get created until there is at least one component that depends on it.
        
        NOTE: Right now component identifiers and item identifiers share the namespace!
        This may need to be improved.
        
        Returns
        -------
        list : str
        """
        return ['?' + i.GEOMETRY_FOLDER,
                ' ' + comp.BIND_MESHES,
                ' ' + comp.BIND_PROXIES,
                ' ' + comp.RIGID_MESHES,
                '?' + i.MODULES_FOLDER,
                ' ' + comp.MODULE,
                '?' + comp.TEMPORARY]

    def getNode(self, identifier):
        """ Gets a node with a given identifier.
        
        Returns
        -------
        HierarchyNode
        
        Raises
        ------
        LookupError
            If node could not be found.
        """
        try:
            return self._nodes[identifier]
        except KeyError:
            raise LookupError
        except AttributeError:
            raise LookupError

    # -------- Private methods
    
    @property
    def _nodes(self):
        if self.__nodes is None:
            self._parse()
        return self.__nodes

    def _parse(self):
        """ Parses template layout and creates internal list of hierarchy nodes.
        """
        self.__nodes = {}
        identifiersList = [] # Temporary list of just identifiers
        layout = self.layout
        
        for x in range(len(layout)):
            nodeDescription = layout[x]
            identifierWithMarks = nodeDescription.lstrip()
            hierarchyLevel = len(nodeDescription) - len(identifierWithMarks)
            
            # Parse the optional property
            optional = False
            identifier = identifierWithMarks
            if identifierWithMarks.startswith('?'):
                identifier = identifierWithMarks[1:]
                optional = True
            
            identifiersList.append(identifier)

            node = HierarchyNode()
            node.identifier = identifier
            node.optional = optional
            
            # Find parent node
            if hierarchyLevel > 0 and x > 0:
                childIndex = 0
                # Go backwards through the layout and find first node
                # that is one level up in hierarchy.
                for y in range(x-1, -1, -1):
                    hl = len(layout[y]) - len(layout[y].lstrip())
                    if hl == (hierarchyLevel - 1):
                        # This is the parent.
                        node.parent = identifiersList[y]
                        node.childIndex = childIndex
                        break
                    childIndex += 1
            
            self.__nodes[node.identifier] = node
            
            # Add this node as child to its parent node as well.
            if node.parent is not None:
                self.__nodes[node.parent].children.append(node.identifier)

    def __init__(self):
        self.__nodes = None

        