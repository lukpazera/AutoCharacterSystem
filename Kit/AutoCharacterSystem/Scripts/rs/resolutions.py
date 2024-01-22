

from . import const as c
from .log import log
from .items.root_item import RootItem
from .core import service


class Resolutions(object):
    """ Resolutions allow for defining various sets of meshes to be visible at a time.
    
    Resolutions can be used to toggle between high res, low res or proxy meshes for example.
    
    Parameters
    ----------
    rigRootItem : RootItem
    
    Raises
    ------
    TypeError
        When trying to initialise object with bad item.
    """

    SETTING_GROUP_RES = 'meshres'
    SETTING_LIST = 'list'
    SETTING_CURRENT = 'current'

    def addResolution(self, name, setAsCurrent=True):
        """ Adds new resolution to the rig.
        
        Resolutions are stored on the rig root item as an item setting.
        
        Paramters
        ---------
        name : str
            Name of the resolution to add.
            
        setAsCurrent : bool
            When true added resolution will be automatically set as current.
        
        Returns
        -------
        bool
            True if resolution was added, False if resolution already exists.
        """
        if not name:
            name = 'Default'
        resolutions = self._rigRootItem.settings.getFromGroup(self.SETTING_GROUP_RES, self.SETTING_LIST, [])
        if name in resolutions:
            return False  # possibly raise an exception so you can't add another layer with the same name.

        resolutions.append(name)
        self._saveResolutions(resolutions)
        if setAsCurrent:
            self.currentResolution = name
        return True

    def removeResolution(self, name):
        """ Removes resolution with a given name.
        
        Current resolution is automatically set to the next one on the list.
        
        Returns
        -------
        bool
        """
        if not name:
            return False
        resolutions = self._rigRootItem.settings.getFromGroup(self.SETTING_GROUP_RES, self.SETTING_LIST, [])
        try:
            resIndex = resolutions.index(name)
        except ValueError:
            return False
        
        resolutions.pop(resIndex)
        self._rigRootItem.settings.setInGroup(self.SETTING_GROUP_RES, self.SETTING_LIST, resolutions)
        
        nextRes = None
        if len(resolutions) > 0:
            if resIndex > 0:
                resIndex -= 1

            nextRes = resolutions[resIndex]

        self.currentResolution = nextRes

        service.events.send(c.EventTypes.MESH_RES_REMOVED, rigRoot=self._rigRootItem, name=name)
        return True

    def renameResolution(self, name, newName):
        """ Renames given resolution.
        
        Parameters
        ----------
        name : str
            Name of resolution to rename.
            
        newName : str
            New name for resolution.
        
        Raises
        ------
        LookupError
            When non-existent resolution name was passed.

        ValueError
            When resolution with new name already exists.
        """
        resolutions = self.allResolutions
        if name not in resolutions:
            raise LookupError
        if newName in resolutions:
            raise ValueError
        
        renamedResolutions = [newName if x==name else x for x in resolutions]
        self._saveResolutions(renamedResolutions)
        
        if self.currentResolution == name:
            self.currentResolution = newName

        service.events.send(c.EventTypes.MESH_RES_RENAMED, rigRoot=self._rigRootItem, name=name, newName=newName)
        return True

    @property
    def currentResolution(self):
        """ Gets current resolution.
        """
        currentRes = self._rigRootItem.settings.getFromGroup(self.SETTING_GROUP_RES, self.SETTING_CURRENT, None)
        return currentRes

    @currentResolution.setter
    def currentResolution(self, name):
        """ Gets or sets new current resolution.
        
        Parameters
        ----------
        name : str, None
            None should be passed only when there are no resolutions at all.

        Returns
        -------
        str, None
            Resolution name or None if there is no resolution set.
        """
        if name is None:
            self._rigRootItem.settings.deleteInGroup(self.SETTING_GROUP_RES, self.SETTING_CURRENT)
            return
        
        if name not in self.allResolutions:
            log.out('Invalid resolution name! Cannot set %s resolution as current.' % name, log.MSG_ERROR)
            return
        
        self._rigRootItem.settings.setInGroup(self.SETTING_GROUP_RES, self.SETTING_CURRENT, name)

    @property
    def resolutionsCount(self):
        return len(self.allResolutions)

    @property
    def allResolutions(self):
        """ Gets a list of resolutions.
        
        Returns
        -------
        list of str
        """
        return self._rigRootItem.settings.getFromGroup(self.SETTING_GROUP_RES, self.SETTING_LIST, [])

    def moveOrderUp(self, resolutionName):
        """ Moves resolution one position up on the list.
        """
        resolutions = self.allResolutions
        try:
            index = resolutions.index(resolutionName)
        except ValueError:
            return False
        
        if index == 0:
            return False
        
        resToMove = resolutions.pop(index)
        index -= 1
        resolutions.insert(index, resToMove)
        self._saveResolutions(resolutions)
        return True
    
    def moveOrderDown(self, resolutionName):
        """ Moves resolution one position down on the list.
        """
        resolutions = self.allResolutions
        try:
            index = resolutions.index(resolutionName)
        except ValueError:
            return False
        
        if index == (len(resolutions) - 1):
            return False
        
        resToMove = resolutions.pop(index)
        
        # If we want to shift the resolution to last place on the list
        # we simply use append. Insert inserts to element before, not after.
        if index == (len(resolutions) - 1):
            resolutions.append(resToMove)
        else:
            index += 1 
            resolutions.insert(index, resToMove)

        self._saveResolutions(resolutions)
        return True
    
    def setNext(self):
        """ Sets next resolution on list.
        """
        currentRes = self.currentResolution
        if currentRes is None:
            return
        resolutions = self.allResolutions
        try:
            currentIndex = resolutions.index(currentRes)
        except IndexError:
            currentIndex = -1

        nextIndex = 0
        if currentIndex >= 0:
            nextIndex = currentIndex + 1
            if nextIndex >= len(resolutions):
                nextIndex = 0
        
        self.currentResolution = resolutions[nextIndex]
    
    def setPrevious(self):
        """ Sets previous resolution on list.
        """
        currentRes = self.currentResolution
        if currentRes is None:
            return
        resolutions = self.allResolutions
        try:
            currentIndex = resolutions.index(currentRes)
        except IndexError:
            currentIndex = -1

        prevIndex = len(resolutions) - 1
        if currentIndex >= 0:
            prevIndex = currentIndex - 1
            if prevIndex < 0:
                prevIndex = len(resolutions) - 1
        
        self.currentResolution = resolutions[prevIndex]

    # -------- Private methods
    
    def _saveResolutions(self, resolutions):
        self._rigRootItem.settings.setInGroup(self.SETTING_GROUP_RES, self.SETTING_LIST, resolutions)
    
    def _getNewResolutionIndex(self, indexes):
        """ Generates new resolution index based on the passed list of taken indexes.
        """
        newIndex = 0
        while True:
            try:
                list.index(newIndex)
            except ValueError:
                break
            newIndex += 1
        return newIndex
        
    def __init__(self, rigRootItem):
        if not isinstance(rigRootItem, RootItem):
            try:
                rigRootItem = RootItem(rigRootItem)
            except TypeError:
                raise

        self._rigRootItem = rigRootItem

    def __iter__(self):
        return iter(self.allResolutions)
