

from .event_handler import EventHandler
from .const import EventTypes as e
from .log import log

from .item import Item
from .rig import Rig


class MeshItem(Item):
    """ Base class for mesh type items.
    
    Meshes can be added or removed from resolutions
    so this base class provides interface for that.
    """
    
    SETTING_RESOLUTION = 'mres'

    def addToResolution(self, resolutionName):
        """ Adds this mesh to a given resolution.
        """
        resolutions = self.settings.get(self.SETTING_RESOLUTION, [])
        if resolutionName not in resolutions:
            resolutions.append(resolutionName)
        self.settings.set(self.SETTING_RESOLUTION, resolutions)
    
    def removeFromResolution(self, resolutionName):
        """ Removes this mesh from a given resolution.
        """
        resolutions = self.settings.get(self.SETTING_RESOLUTION, [])
        try:
            resolutions.remove(resolutionName)
        except ValueError:
            return
        if len(resolutions) > 0:
            self.settings.set(self.SETTING_RESOLUTION, resolutions)
        else:
            self.settings.delete(self.SETTING_RESOLUTION)
    
    def clearResolutions(self):
        """ Clears all resolutions from this mesh.
        """
        self.settings.delete(self.SETTING_RESOLUTION)
    
    def replaceResolution(self, previousName, newName):
        """ Replaces one item resolution for another. Same as renaming item's resolution really.
        """
        resolutions = self.settings.get(self.SETTING_RESOLUTION, [])
        try:
            prevIndex = resolutions.index(previousName)
        except ValueError:
            return
        resolutions[prevIndex] = newName
        self.settings.set(self.SETTING_RESOLUTION, resolutions)        
        
    def isInResolution(self, resolutionName):
        """ Tests whether a mesh is a part of a given resolution.
        """
        resolutions = self.settings.get(self.SETTING_RESOLUTION, [])
        return resolutionName in resolutions
    

class MeshItemResolutionsEventHandler(EventHandler):
    """ Handles events that relate to mesh resolutions.
    
    Attributes
    ----------
    descElementSet : str
        Name of element set that is related to this mesh item.
        It's required to handle 
    """
  
    descElementSet = None
    
    @property
    def eventCallbacks(self):
        return {e.MESH_RES_RENAMED: self.event_meshResolutionRenamed,
                e.MESH_RES_REMOVED: self.event_meshResolutionRemoved}

    def event_meshResolutionRenamed(self, **kwargs):
        """ Mesh resolution was renamed, we need to update all the items.
        """ 
        try:
            rig = Rig(kwargs['rigRoot'])
            resolutionName = kwargs['name']
            resolutionNewName = kwargs['newName']
        except KeyError:
            return
  
        modoItems = rig[self.descElementSet].elements
        for modoItem in modoItems:
            rigItem = Item.getFromModoItem(modoItem)
            try:
                rigItem.replaceResolution(resolutionName, resolutionNewName)
            except AttributeError:
                pass
        
    def event_meshResolutionRemoved(self, **kwargs):
        """ Mesh resolution was removed, we need to clear all references to it.
        """
        try:
            rig = Rig(kwargs['rigRoot'])
            resolutionName = kwargs['name']
        except KeyError:
            return
        
        modoItems = rig[self.descElementSet].elements
        for modoItem in modoItems:
            rigItem = Item.getFromModoItem(modoItem)
            try:
                rigItem.removeFromResolution(resolutionName)
            except AttributeError:
                pass