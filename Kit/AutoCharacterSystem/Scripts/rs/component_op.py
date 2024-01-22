
""" Base class for implementing functionality for a rig component.

    If you have a piece of rig functionality that is enclosed within a component
    (with component setup) you can use this class as a base for implementing operations
    that can be performed on that component (or its setup).
    
    An example is bind meshes. It's got component, the setup (which is bind meshes folder in the rig)
    and an operator that allows for assigning and unassigning bind meshes.
"""


import lx
import modo

from .rig_structure import RigStructure
from .items.root_item import RootItem
from . import const as c


class ComponentOperator(object):
    """ Component operator base class.
    
    Note that this base class works only when the component is a singleton in a rig.
    There can be only one component of a type that this operator is meant to work on.
    
    Public interface for operator can be anything that you want the operator to do.
    
    Attributes
    ----------
    descComponentClass : Component
        A class of a component that goes with this component operator.
    
    Parameters
    ----------
    rigRoot : RootItem, str, modo.Item
        Root of the rig that you want to the component operator to work with.
    """

    descComponentClass = None
    
    # -------- Public interface

    @property
    def component(self):
        """ Gets component object.
        
        If component cannot be found a new one is created.
        
        Returns
        -------
        Component
            descComponentClass type.
        """
        if self.__component is None:
            components = self._rigStructure.getComponents(self.descComponentClass)
            if len(components) > 0:
                self.__component = components[0]
                # What do we do if there are more components?
                # Need to run clean up?
            if self.__component is None:
                self._newComponent()
        return self.__component

    # -------- Private methods

    def _newComponent(self):
        """ Creates new component for bind meshes.
        """
        self.__component = self._rigStructure.newComponent(self.descComponentClass)

    def __init__(self, rigRoot):
        if not isinstance(rigRoot, RootItem):
            try:
                rigRoot = RootItem(rigRoot)
            except TypeError:
                raise

        self._rigRootItem = rigRoot
        self._rigStructure = RigStructure(self._rigRootItem)
        self.__rigSetup = None
        self.__component = None