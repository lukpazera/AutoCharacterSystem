
import lx
import modo

from . import sys_component
from . import const as c
from .module import Module
from .log import log


class PropertyScope(object):
    LOCAL = 0
    GLOBAL = 1


class ModuleVariant(object):
    """
    Module variant allows for applying changes to a module to create its variant.

    Changes are applied one time, after variant is applied to module the module becomes this variant
    and it cannot be changed to anything else or go back to "vanilla" module state.

    Variants still need to be compatible with "vanilla" module as far as all the feature code is concerned.

    Attributes
    ----------
    descIdentifier : str
        Unique identifier for the variant. It has to be unique within other variants
        for this module.

    descUsername : str
        Username to show on an apply button.

    descName : str
        New name for module.

    descFilename : str
        Variant will be saved under this filename.

    descDefaultThumbnailName :  str
        Name of the thumbnail from default thumbnails path without extension (.png is assumed).

    descApplyGuide : bool
        If variant changes the guide the guide should be applied.

    descRefreshContext : bool
        If variant adds or removes items the context should be refreshed after applying it.

    descFeatures : [], None
        When not None the list of module features provided will be used instead of the host module features.
        It's None by default assuming that the variant will have the same features as the host module.
    """

    descIdentifier = ''
    descUsername = ''
    descName = ''
    descFilename = ''
    descDefaultThumbnailName = ''
    descApplyGuide = False  # apply guide when done
    descRefreshContext = False  # refresh context when done
    descFeatures = None

    @classmethod
    def isVariant(cls, module):
        """
        Tests if given module is a variant (or just module).

        Returns
        -------
        bool
        """
        return (module.rootItem.settings.get(cls._SETTING_VARIANT, None) is not None)

    def onApply(self):
        """
        Implement this to perform any actions required to create the variant.

        Returns
        -------
        bool
            Return True is everything was applied correctly, False if it didn't.
        """
        return False

    def apply(self):
        """
        Implement this method to perform actions that create the variant.

        Returns
        -------
        bool
            True when application was successfull, False otherwise.
        """
        # Do not apply variant if module is variant already
        if self.isVariant(self.module):
            return False

        result = self.onApply()
        if result:
            self._applyVariantSettings()

        return result

    @property
    def identifier(self):
        """
        Gets variant identifier.

        Returns
        -------
        str, None
            Returns None if this module isn't a variant.
        """
        return self.module.rootItem.settings.get(self._SETTING_VARIANT, None)

    @property
    def module(self):
        return self._module

    # -------- Private methods

    _SETTING_VARIANT = 'variant'

    def _applyVariantSettings(self):
        """
        """
        if self.descName:
            self.module.name = self.descName
        self.module.filename = self.descFilename
        self.module.defaultThumbnailName = self.descDefaultThumbnailName
        self.module.rootItem.settings.set(self._SETTING_VARIANT, self.descIdentifier)

    def __init__(self, module):
        if isinstance(module, Module):
            self._module = module
        else:
            try:
                self._module = Module(module)
            except TypeError:
                raise


class ModuleProperty(object):
    """ Module properties allow for customising modules.
    
    Properties are part of module feature.
    Properties are shown as custom module attribute in
    module properties and can be manipulated by user.

    Parameters
    ----------
    module : Module
        Module to which the property applies.

    Attributes
    ----------
    descIdentifier : str
        Identifier for the property, unique within module feature.
    
    descUsername : str
        User friendly name for property that will be shown in UI.

    descValueType : str
        Type of the value representing the property.
        It needs to be one of lx.symbol.sTYPE_ constants.

    descTooltipMsgTableKey : str
        Key to entry in tooltips message table for the property tooltip.

    descApplyGuide : bool
        Tells whether this property when set (and onSet returns True)
        should reapply the guide to the rig.
        If the property changes module in such a way that the guide is changed
        this should return True.
        The guide is applied only to the module that has a property and to all its submodules.
    
    descRefreshContext : bool
        When set to True

    descDeveloperAccess : bool
        When set to True the property is visible in development context only.

    descSetupMode : bool, None
        Set to None for property to not affect setup mode or True/False to set setup mode to a given state.
        True by default.

    descSupportSymmetry : bool
        If property supports symmetry changing property on one side will automatically apply the same
        change to the property on the symmetrical module.
        True by default.
    """

    Scope = PropertyScope

    descIdentifier = ''
    descUsername = ''
    descValueType = lx.symbol.sTYPE_INTEGER
    descScope = Scope.LOCAL
    descApplyGuide = False
    descRefreshContext = False
    descTooltipMsgTableKey = None
    descDeveloperAccess = False
    descSetupMode = True
    descSupportSymmetry = True

    def onQuery(self):
        """ Implements code that queries property for a value.
        
        Returned value needs to be of type defined in descValueType.
        """
        pass
    
    def onSet(self, value):
        """ Implements code that sets property with a given value.
        
        Passed value will be of type defined in descValueType.
        
        Returns
        -------
        bool
            Return True when setting property changed the module.
            False otherwise.
        """
        pass

    @property
    def module(self):
        return self._module

    # -------- Private methods
    
    def __init__(self, module):
        self._module = module


class ModuleCommand(object):
    """ Module commands allow for customising modules by firing a piece of code with arguments.
    
    Commands are show as buttons to press in module properties.

    Attributes
    ----------
    descIdentifier : str
        Identifier for the command, unique within module feature commands.
    
    descUsername : str
        User friendly name for command that will be shown in UI.

    descTooltipMsgTableKey : str
        Key to entry in tooltips message table for the property tooltip.

    descApplyGuide : bool
        Tells whether this property when set (and onSet returns True)
        should reapply the guide to the rig.
        If the property changes module in such a way that the guide is changed
        this should return True.
    
    descRefreshContext : bool
        When set to True

    descDeveloperAccess : bool
        When set to True the command is visible in development context only.

    descSetupMode : bool, None
        Set to None for property to not affect setup mode or True/False to set setup mode to a given state.
        True by default.

    descSupportSymmetry : bool
        If command supports symmetry firing command on one side will automatically fire it
        on the symmetrical module as well.
        True by default.
    """

    Scope = PropertyScope

    descIdentifier = ''
    descUsername = ''
    descTooltipMsgTableKey = None
    descScope = Scope.LOCAL
    descApplyGuide = False
    descRefreshContext = False
    descDeveloperAccess = False
    descSetupMode = True
    descSupportSymmetry = True

    def run(self, arguments=[]):
        """ Implements a code that should be run with given set of arguments.

        Parameters
        ----------
        arguments : [str]
        """
        pass

    @property
    def module(self):
        return self._module

    # -------- Private methods
    
    def __init__(self, module):
        self._module = module


class FeaturedModule(sys_component.SystemComponent):
    """
    Featured module is a module that is supported with code and exposes extra features.

    Featured modules have to be registered with the system using their identifier.
    They won't be seen and their properties will not show up in UI otherwise.

    Parameters
    ----------
    module : Module
        Module class initialized with setup that matches this featured module.

    Attributes
    ----------
    descIdentifier : str
        Unique string identifier for the module that is being implemented.

    descUsername : str
        User friendly name for module that will be shown in log outputs, etc.

    descVariants : [ModuleVariant]
        List of variants that can be applied to the module.

    descFeatures : [ModuleCommand, ModuleProperty]
        List of properties and commands that the module is exposing.

    descVariants : [ModuleVariant]
        List of possible variants of the module.

    DIVIDER : str
        Use this contant to insert divider into module properties form.

    Raises
    ------
    TypeError
        When trying to initialize this instance with object that is not Module.
    """

    DIVIDER = "- "

    descIdentifier = ''
    descUsername = ''
    descFeatures = []
    descVariants = []

    # -------- System component attributes, do not touch.

    @classmethod
    def sysType(cls):
        return c.SystemComponentType.FEATURED_MODULE

    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier

    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Featured Module'

    # -------- Virtual methods

    def onSwitchToFK(self, switcherFeature):
        """ Custom operation on the switch from IK to FK for a module.

        Implement this method to perform these custom operations.

        Parameters
        ----------
        switcherFeature : IKFKSwitcherItemFeature

        """
        pass

    # -------- Public interface

    @classmethod
    def getPropertyClass(cls, ident):
        """ Gets module property class by its ident.

        Parameters
        ----------
        ident : str

        Returns
        -------
        ModuleProperty
        """
        for prop in cls.descFeatures:
            if isinstance(prop, str):
                continue
            elif not issubclass(prop, ModuleProperty):
                continue
            if prop.descIdentifier == ident:
                return prop
        return None

    @classmethod
    def getCommandClass(cls, ident):
        """ Gets module command class by its ident.

        Parameters
        ----------
        ident : str

        Returns
        -------
        ModuleCommand
        """
        for prop in cls.descFeatures:
            if isinstance(prop, str):
                continue
            elif not issubclass(prop, ModuleCommand):
                continue
            if prop.descIdentifier == ident:
                return prop
        return None

    @classmethod
    def getVariantClass(cls, ident):
        """
        Gets variant class by its identifier.

        Parameters
        ----------
        ident : str

        Returns
        -------
        ModuleVariant

        Raises
        ------
        LookupError
            When given variant cannot be found.
        """
        for variantClass in cls.descVariants:
            if variantClass.descIdentifier == ident:
                return variantClass
        raise LookupError

    def getVariant(self):
        """
        If this module is a variant an initialized variant object will be returned.

        Returns
        -------
        ModuleVariant

        Raises
        ------
        TypeError
            When module is not variant.
        """
        # This code is werid.
        # First we use generic ModuleVariant class to get variant identifier.
        # Once we have identifier we find the actual variant class and return variant
        # object instantiated from that class.
        variant = ModuleVariant(self.module)
        identifier = variant.identifier
        if identifier is None:
            raise TypeError

        return self.getVariantClass(identifier)(self.module)

    @property
    def featuresList(self):
        try:
            features = self.getVariant().descFeatures
        except TypeError:
            features = None

        if features is None:
            features = self.descFeatures

        return features

    def onQuery(self, propertyIdent):
        """ Called when module property is queried.
        """
        propClass = self.getPropertyClass(propertyIdent)
        if propClass is not None:
            return propClass(self._module).onQuery()

    def onSet(self, propertyIdent, value):
        """ Called when module property is set.

        Parameters
        ----------
        propertyIdent : str
        """
        propClass = self.getPropertyClass(propertyIdent)
        if propClass is not None:
            propObj = propClass(self._module)
            return propObj.onSet(value)

    def onRun(self, commandIdent, arguments):
        """ Called when module command is ran.

        Parameters
        ----------
        arguments : [str]
        """
        cmdClass = self.getCommandClass(commandIdent)
        if cmdClass is not None:
            return cmdClass(self._module).run(arguments)

    @property
    def module(self):
        return self._module

    # -------- Private methods

    def __init__(self, module):
        if not isinstance(module, Module):
            raise TypeError

        self._module = module
