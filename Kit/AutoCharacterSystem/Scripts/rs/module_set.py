"""
    Module set module.
"""

import lx
import modo
import modox

from . import const as c
from .component import Component
from .component_setup import ComponentSetup
from .item import Item
from .module import Module
from .preset_thumbs.module import ModulePresetThumbnail


class ModuleSetRoot(Item):

    descType = c.RigItemType.MODULE_SET_ROOT
    descUsername = 'Module Set Root Item'
    descModoItemType = 'groupLocator'
    descDefaultName = 'ModuleSet'
    descPackages = []
    descSelectable = False


class ModuleSetAssembly(Item):

    descType = c.RigItemType.MODULE_SET_ASSM
    descUsername = 'Module Set Assembly Item'
    descModoItemType = 'group'
    descModoItemSubtype = 'assembly'
    descDefaultName = 'ModuleSet'
    descPackages = []


class ModuleSetComponentSetup(ComponentSetup):
    descIdentifier = c.ComponentType.MODULE_SET
    descUsername = 'Module Set'
    descPresetDescription = 'ACS Module Set'
    descOnCreateDropScript = 'rs_drop_module_set'


class ModuleSet(Component):
    """ Module is a collection of modules.

    It is temporary construct for now, it's only set up for saving
    multiple modules as a single preset.
    It may become a scene entity later.

    Parameters
    ----------
    rootModoItem : modo.Item
        The item that is root of module set.
        It doesn't really serve a puprose right now except being the item
        with the drop script attached.
    """

    descIdentifier = c.ComponentType.MODULE_SET
    descUsername = 'Module Set'
    descRootItemClass = ModuleSetRoot
    descAssemblyItemClass = ModuleSetAssembly
    descComponentSetupClass = ModuleSetComponentSetup

    # -------- Public interface

    @property
    def modules(self):
        """
        Gets a list of modules in the module set.

        The order is according to hierarchy of module root items under the module set root.

        Returns
        -------
        [Module]
        """
        subsetups = self.setup.subsetups
        modules = []
        for subsetup in subsetups:
            try:
                modules.append(Module(subsetup.rootModoItem))
            except TypeError:
                continue
        return modules

    def save(self, filename, captureThumb=False):
        """
        Saves module set as an assembly preset.

        Parameters
        ----------
        filename : str
        """
        if captureThumb:
            thumb = ModulePresetThumbnail()
            # Get thumbnail filename from first module if one is set.
            thumbName = self.modules[0].rootItem.defaultThumbnailName
            if thumbName:
                thumb.setThumbnailDirectly(thumbName)
        else:
            thumb = None

        # Need to set system version on the main module.
        # This is really sketchy here but let it be for now.
        self.modules[0].rootItem.setSystemVersion()

        self.setup.save(filename, thumb)

    def selfDelete(self):
        """
        Module set deletes itself. Don't use the object once you call this method.
        """
        self.setup.selfDelete()

    # -------- Private methods
