

from .scene import Scene
from .module_op import ModuleOperator
from .items.module_root import ModuleRoot
from .items.root_item import RootItem
from .guide import Guide
from .module_feature import *
from .core import service
from .log import log


class FeaturedModuleOperator(object):
    """
    Featured module operator allows for performing operations on featured modules.

    It can be considered higher level then Modules Operator but lower then Rig.

    Parameters
    ----------
    rigRootItem : RootItem

    Raises
    ------
    TypeError
        When trying to initialize this instance with object that is not rig root item.
    """

    # -------- Public interface

    @classmethod
    def getFeaturedModuleClass(cls, moduleIdent):
        """
        Gets proper module object it's module with features.

        moduleIdent : FeaturedModule, str, Module, ModuleRoot

        Raises
        ------
        LookupError
            If module with this identifier has no features.

        TypeError
            If bad ident object type was passed.
        """
        if issubclass(moduleIdent.__class__, FeaturedModule):
            return moduleIdent.__class__
        elif isinstance(moduleIdent, str):
            pass
        elif isinstance(moduleIdent, Module):
            moduleIdent = moduleIdent.identifier
        elif isinstance(moduleIdent, ModuleRoot):
            moduleIdent = Module(ModuleRoot).identifier
        else:
            raise TypeError

        try:
            return service.systemComponent.get(c.SystemComponentType.FEATURED_MODULE, moduleIdent)
        except LookupError:
            pass
        raise LookupError

    @classmethod
    def getAsFeaturedModule(cls, module):
        """ Gets module as featured one - provided one was registered.

        Parameters
        ----------
        module : Module
            Module to return as FeaturedModule.

        Returns
        -------
        FeaturedModule

        Raises
        ------
        TypeError
            When given module does not have any features registered.
        """
        if issubclass(module.__class__, FeaturedModule):
            return module
        ident = module.identifier
        try:
            featuredModuleClass = cls.getFeaturedModuleClass(ident)
        except LookupError:
            raise TypeError
        return featuredModuleClass(module)

    def saveVariants(self, module):
        """
        Saves all variants for a given module (provided this is featured modules with variants).

        Parameters
        ----------
        module : FeaturedModule, str, Module, ModuleRoot

        Returns
        -------
        bool
            True if saving was successfull, False otherwise.
        """
        try:
            featuredModuleClass = self.getFeaturedModuleClass(module)
        except LookupError:
            featuredModuleClass = None

        if featuredModuleClass is None:
            return False

        moduleOp = ModuleOperator(self._rigRoot)
        variants = featuredModuleClass.descVariants
        for variantClass in variants:
            duplicatedModule = moduleOp.duplicateModule(module)
            if duplicatedModule is None:
                continue
            featuredModule = featuredModuleClass(duplicatedModule)
            self.applyVariant(featuredModule, variantClass)
            featuredModule.module.save(filename=None, captureThumb=True)

        return True

    def applyVariant(self, featuredModule, variant):
        """
        Parameters
        ----------
        module : FeaturedModule

        variant : ModuleVariant, str
        """
        module = featuredModule.module
        if isinstance(variant, ModuleVariant):
            pass
        elif isinstance(variant, str):
            try:
                variantClass = featuredModule.getVariantClass(variant)
            except LookupError:
                log.out("Module (%s) variant (%s) cannot be found!" % (module.name, variant), log.MSG_ERROR)
                return False
            variant = variantClass(module)
        else:
            try:
                variant = variant(module)
            except TypeError:
                raise

        result = variant.apply()
        if result:
            self._applyEdits(module, variant)
        return result

    # -------- Private methods

    def _applyEdits(self, modules, editedClassOrObject):
        """
        This applies edits made to the rig via property or command.
        """
        if type(modules) not in (tuple, list):
            modules = [modules]

        if editedClassOrObject.descApplyGuide:
            guide = Guide(self._rigRoot)
            guide.apply(modules)

        refreshContext = editedClassOrObject.descRefreshContext
        if isinstance(refreshContext, bool):
            if refreshContext:
                Scene().contexts.refreshCurrent()
        elif isinstance(refreshContext, str):
            Scene().contexts.current = refreshContext

    def __init__ (self, rigRootItem):
        if isinstance(rigRootItem, modo.Item):
            try:
                rigRootItem = RootItem(rigRootItem)
            except TypeError:
                raise
        if not isinstance(rigRootItem, RootItem):
            raise TypeError
        self._rigRoot = rigRootItem
