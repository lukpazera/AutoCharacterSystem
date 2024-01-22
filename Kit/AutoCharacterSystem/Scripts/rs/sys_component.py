
""" System Component interface definition.
"""


import lx
import modo


class SystemComponent(object):
    """ Interface for objects that act as system components.
    
    Note that SystemComponents do not have to inherit from this object.
    It's enough if they implement required class methods.
    """
    
    @classmethod
    def sysType(cls):
        """ Defines system component type.
        
        Returns
        -------
        str
            String type of component, there can be multiple different
            components of the same type.
        """
        return None
    
    @classmethod
    def sysIdentifier(cls):
        """ Defines unique identifier for a system component.

        Returns
        -------
        str
            String identifier of a system component that is unique within
            registered components of the same type.
        """
        return ''
    
    @classmethod
    def sysUsername(cls):
        return ''

    @classmethod
    def sysSingleton(cls):
        """ Defines whether component is a singleton or not.
        
        Singleton components are registered as object instance while
        non singleton ones (default) are registered as a class that needs to be instanced.
        """
        return False

    @classmethod
    def sysServer(cls):
        return False

    @classmethod
    def getUsernameOrIdentifier(cls):
        """ Returns either username or identifier if username is not defined.
        """
        username = cls.sysUsername()
        if not username:
            username = cls.sysIdentifier()
        return username

    def __str__(self):
        return self.getUsernameOrIdentifier() + ' Rigging System Component'

    def __eq__(self, other):
        if issubclass(other.__class__, SystemComponent):
            return self.sysIdentifier() == other.sysIdentifier()
        elif isinstance(other, str):
            return self.sysIdentifier() == other
        return False

    def __lt__(self, other):
        if issubclass(other.__class__, SystemComponent):
            return self.sysIdentifier() < other.sysIdentifier()
        elif isinstance(other, str):
            return self.sysIdentifier() < other
        return False
