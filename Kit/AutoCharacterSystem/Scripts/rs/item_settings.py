
""" Item settings.
"""


import json

import lx
import lxu
import modo


class ItemSettings(object):
    """ Item settings.
    
    Settings can be stored on and read from a modo item.
    Python objects/values are stored directly.
    This interface doesn't know anything about settings to be stored
    so all responsibility for getting/setting right type of value
    is on the client.
    
    There are two types of settings:
    - single setting is a value referenced by unique string key.
    - setting group is a dictionary of setting key/value pairs referenced
    by an unique string key.

    Settings are saved to item each time any setting or group is set.
    Use batchEdit property to change multiple settings and save only once
    at the end.
    """

    TAG_SINGLE = 'RSIS'
    TAG_GROUPS = 'RSIG'

    @property
    def batchEdit(self):
        return self._batchMode

    @batchEdit.setter
    def batchEdit(self, value):
        self._batchMode = value
        if not value:
            self.save()

    def getGroup(self, groupKey):
        """ Gets a group of settings by its key.
        
        Parameters
        ----------
        groupKey : str
            Unique key of settings group.
            
        Returns
        -------
        dict
            Group of settings as dictionary of setting key/value pairs.
            Empty dictionary is returned when settings group does not exist.
        """
        try:
            return self._settingGroups[groupKey]
        except KeyError:
            return {}

    def get(self, settingKey, defaultValue=None):
        """ Gets a single setting by its key.
        
        Parameters
        ----------
        settingKey : str
            Unique key of the setting.
        
        defaultValue : optional
            When setting is not present on an item the default value
            will be returned (None by default).
        """
        try:
            return self._singleSettings[settingKey]
        except KeyError:
            return defaultValue

    def getFromGroup(self, groupKey, settingKey, defaultValue=None):
        """ Gets a single setting from a group.

        defaultValue : optional
            When setting is not present on an item the default value
            will be returned (None by default).
        
        Returns
        -------
            Setting value or default value when setting cannot be found.
        """
        try:
            return self._settingGroups[groupKey][settingKey]
        except KeyError:
            return defaultValue

    def set(self, settingKey, value):
        """ Sets a single setting by its key.
        
        Parameters
        ----------
        settingKey : str
            Unique key for the setting.
        
        value :
            Setting value to be stored on an item.
        """
        self._singleSettings[settingKey] = value
        if not self._batchMode:
            self.save()

    def setInGroup(self, groupKey, settingKey, value):
        try:
            settings = self._settingGroups[groupKey]
        except KeyError:
            settings = {}
        settings[settingKey] = value
        self._settingGroups[groupKey] = settings

        if not self._batchMode:
            self.save()

    def setGroup(self, groupKey, settingsDict):
        """ Sets settings group by a key.
        
        Parameters
        ----------
        groupKey : str
            Key for the settings group.
        
        settingsDict : dict
            Settings group has to be a dictionary of setting key/value pairs.
        """
        self._settingGroups[groupKey] = settingsDict
        if not self._batchMode:
            self.save()

    def delete(self, settingKey):
        """ Deletes single setting by its key.
        """
        if settingKey in self._singleSettings:
            del self._singleSettings[settingKey]
            if not self._batchMode:
                self.save()
            return True
        return False

    def deleteGroup(self, groupKey):
        if groupKey in self._settingGroups:
            del self._settingGroups[groupKey]
            if not self._batchMode:
                self.save()
            return True
        return False
    
    def deleteInGroup(self, groupKey, settingKey):
        try:
            del self._settingGroups[groupKey][settingKey]
        except KeyError:
            return False
        if not self._batchMode:
            self.save()
        return True
    
    def clear(self):
        """ Clears all settings and setting groups.
        """
        self._reset()
        if not self._batchMode:
            self.save()

    def save(self):
        """ Saves all settings and setting groups to the item.
        """
        if (self._singleSettings):
            tagVal = json.dumps(self._singleSettings)
        else:
            tagVal = None
        self._modoItem.setTag(self.TAG_SINGLE, tagVal)

        if (self._settingGroups):
            tagVal = json.dumps(self._settingGroups)
        else:
            tagVal = None
        self._modoItem.setTag(self.TAG_GROUPS, tagVal)

    # -------- Private methods

    def _reset(self):
        self._singleSettings = {}
        self._settingGroups = {}

    def _load(self):
        self._reset()
        try:
            self._singleSettings = json.loads(self._modoItem.readTag(self.TAG_SINGLE))
        except LookupError:
            pass
            
        try:
            self._settingGroups = json.loads(self._modoItem.readTag(self.TAG_GROUPS))
        except LookupError:
            pass

    def __init__(self, modoItem):
        self._modoItem = modoItem
        self._singleSettings = {}
        self._settingGroups = {}
        self._batchMode = False
        self._load()


class SettingsTag(object):
    """ Allows for storing a set of settings on a tag.
    
    Lists and dictionaries are supported.
    
    Parameters
    ----------
    modoItem : modo.Item
        Modo item on which settings are/will be stored.
        
    tagNameOrId : str, int
        Either tag string identifier (4 letters) or its identifier code.
    """
    
    _ASSING_VALUE = '='
    _SETTING_SEPARATOR = ';'
    
    def set(self, settings):
        """ Sets given settings in a tag on an item.
        
        Parameters
        ----------
        settings : dict, list
        """
        if isinstance(settings,dict): 
            self._storeDictionary(settings)
    
    def get(self, keyType, valueType=None):
        """ Gets given settings from a tag on an item.
        
        Parameters
        ----------
        keyType : object class
            Key will be converted to this type upon returning.
            When dealing with dictionary key is the type of keys in dictionary.
            When deailing with lists it's type of elements on the list.
        
        valueType : object class, None
            Only relevant to dictionaries, should be None when getting lists.
            In dictionary it's a object type for values in the dict.
            
        Returns
        -------
        dict, list
            If valueType is None you're get list, you'll get dictionary otherwise.
        """
        if valueType is None:
            settings = []
        else:
            settings = {}
            
        try:
            val = self._tag.Get(self._tagId)
        except LookupError:
            return settings
        
        settingsSrc = val.split(self._SETTING_SEPARATOR)

        for s in settingsSrc:
            if type(settings) == list:
                settings.append(keyType(s))
            elif type(settings) == dict:
                entry = s.split(self._ASSING_VALUE)
                settings[keyType(entry[0])] = valueType(entry[1])
        return settings
        
    def clear(self):
        """ Clears settings tag from an item.
        """
        self._tag.Set(self._tagId, None)

    # -------- Private methods
    
    def _storeDictionary(self, dictionary):
        string = ''
        for key in list(dictionary.keys()):
            string += (str(key) + self._ASSING_VALUE + str(dictionary[key]) + self._SETTING_SEPARATOR)
        if len(string) > 0:
            string = string[:-1]
        self._storeTag(string)

    def _storeTag(self, tagString):
        self._tag.Set(self._tagId, tagString)
        
    def __init__(self, modoItem, tagNameOrId):
        if isinstance(tagNameOrId, str):
            self._tagId = lxu.lxID4(tagNameOrId)
        else:
            self._tagId = tagNameOrId
        self._item = modoItem
        self._tag = lx.object.StringTag(self._item.internalItem)
