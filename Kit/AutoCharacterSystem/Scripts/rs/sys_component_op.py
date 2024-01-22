
""" System component operator.

    This module is used to register and maintain system components during
    runtime. Components need to present SystemComponent interface.
"""


from collections import OrderedDict

import lx
import modo

from .log import log as log
from .debug import debug
from . import sys_component


class SystemComponentsOperator(object):
    """ Maintains all Rigging System components.
    """

    def register(self, componentClass):
        """ Registers new system component.

        If SystemComponent is singleton (sysSingleton() returns True)
        it's registered as object rather then as a class.
        It becomes persistent object then.

        Parameters
        ----------
        componentClass : SystemComponent
            Class presenting SystemComponent interface.
        """
        componentType = componentClass.sysType()
        componentIdentifier = componentClass.sysIdentifier()
        
        if componentType not in self._components:
            self._components[componentType] = OrderedDict()

        try:
            singleton = componentClass.sysSingleton()
        except AttributeError:
            singleton = False
            
        if singleton:
            self._components[componentType][componentIdentifier] = componentClass()
        else:
            self._components[componentType][componentIdentifier] = componentClass
        
        self._componentCount += 1
        
        try:
            server = componentClass.sysServer()
        except AttributeError:
            server = False
            
        if server:
            try:
                lx.bless(componentClass, componentClass.sysIdentifier())
            except RuntimeError:
                log.out('System component %s cannot be blessed as a plugin!' % componentClass.sysUsername(), log.MSG_ERROR)
                return
        
        if debug.output:
            log.out("%s system component registered." % componentClass.sysUsername(), log.MSG_INFO)

    @property
    def componentCount(self):
        """ Gets number of registered system components.
        
        Returns
        -------
        int
        """
        return self._componentCount

    def get(self, componentType, componentIdentifier):
        """ Retrieves registered system component class or object.

        Parameters
        ----------
        componentType : str
            String component type.
        
        componentIdentifier : str
            Unique string identifier of the component.
            
        Returns
        -------
        SystemComponent, SystemComponent()
            SystemComponent class with given type and identifier or SystemComponent object
            if the component is a singleton.

        Raises
        ------
        LookupError
            If requested component cannot be found.
        """
        try:
            return self._components[componentType][componentIdentifier]
        except KeyError:
            if debug.output:
                log.out('Getting component failed. Component not found: %s : %s' % (componentType, componentIdentifier), log.MSG_ERROR)
            raise LookupError

    def getOfType(self, componentType):
        """ Returns all components of a given type.
        
        Parameters
        ----------
        componentType : str
            String component type.
        
        Returns
        -------
        list of SystemComponent
            These will be classes for non-singletons and instantiated
            class objects for singletons.
        
        Raises
        ------
        LookupError
            If componentType is not correct.
        """
        try:
            return list(self._components[componentType].values())
        except KeyError:
            raise LookupError

    def getOfTypeSortedByIdentifier(self, componentType):
        """ Returns all components of a given type sorted alphabetically using their idents.

        Parameters
        ----------
        componentType : str
            String component type.

        Returns
        -------
        list of SystemComponent
            These will be classes for non-singletons and instantiated
            class objects for singletons.

        Raises
        ------
        LookupError
            If componentType is not correct.
        """
        try:
            components = self.getOfType(componentType)
        except LookupError:
            raise

        components.sort()
        return components

    def getOfTypeSortedByUsername(self, componentType):
        """ Returns all components of a given type sorted alphabetically using their username.

        Parameters
        ----------
        componentType : str
            String component type.

        Returns
        -------
        list of SystemComponent
            These will be classes for non-singletons and instantiated
            class objects for singletons.

        Raises
        ------
        LookupError
            If componentType is not correct.
        """
        try:
            components = self.getOfType(componentType)
        except LookupError:
            raise

        componentsByUsernames = {}
        names = []
        for component in components:
            componentsByUsernames[component.sysUsername()] = component
            names.append(component.sysUsername())

        names.sort()
        sortedComponents = []
        for name in names:
            sortedComponents.append(componentsByUsernames[name])

        return sortedComponents

    # -------- Private methods

    def __init__(self):
        self._components = {}
        self._componentCount = 0