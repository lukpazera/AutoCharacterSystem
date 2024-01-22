

""" Naming Scheme interface definition.
"""


from . import sys_component
from . import const as c


class NamingScheme(sys_component.SystemComponent):
    """ Naming scheme interface.
    
    Attributes
    ----------
    formatGeneric : list
        List of name components in an order in which they appear in rendered name.
        Components are defined as constants in rs.c.NameToken.
        Literal strings can be used as well.
        When literal string starts with '<' it means the literal string is dependent
        on previous token being resolved and rendered in name. The '<' character
        itself is skipped from literal string.
    
    formatByItemType : dict
        Each item type can have different name format.
        You define it by using item type (rig item type or MODO item type) as key
        and the format list (built in the same way as in formatGeneric) as value.
        MODO item type is picked up only on rig items that are not bound to
        a specific modo item type.
        
    itemTypeTokens : dict
        Dictionary of strings that will be put into names of items of given type.
    
    itemFeatureTokens : dict
        Same as above but for item features.
    
    leftToken : str
        String for left side.
    
    rightToken : str
        String for right side.

    centerToken : str
        String for items with no side.
    """
    
    descIdentifier = ''
    descUsername = ''

    # -------- Public attributes

    formatGeneric = []
    formatByItemType = {}
    itemTypeTokens = {}
    itemFeatureTokens = {}
    modoItemTypeTokens = {}
    leftToken = ''
    rightToken = ''
    centerToken = ''
    formatGenericMeta = []
    formatByGroupTypeMeta = {}

    # -------- System Component Interface
    
    @classmethod
    def sysType(cls):
        return c.SystemComponentType.NAMING_SCHEME
    
    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier
    
    @classmethod
    def sysUsername(cls):
        return cls.descUsername

    @classmethod
    def sysSingleton(cls):
        return True

