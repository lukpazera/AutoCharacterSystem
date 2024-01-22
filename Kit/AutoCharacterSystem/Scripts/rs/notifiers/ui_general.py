

import lx
import rs.notifier
import rs.const as c


class NotifierUIGeneral(rs.notifier.Notifier):
    
    descServerName = c.Notifier.UI_GENERAL
    descUsername = 'General UI Notifier'


class NotifierItemFeatureAddRemove(rs.notifier.Notifier):
    """ Notify when an item feature is either added or removed from an item.
    """

    descServerName = c.Notifier.ITEM_FEATURES_ADDREM
    descUsername = 'Item Features Add | Remove Notifier'


class NotifierModuleProperties(rs.notifier.Notifier):
    """ Notify when module properties need to be refreshed.
    """

    descServerName = c.Notifier.MODULE_PROPERTIES
    descUsername = 'Module Properties Notifier'


class NotifierAccessLevel(rs.notifier.Notifier):
    """ Notify when access level to a rig has changed.
    """

    descServerName = c.Notifier.ACCESS_LEVEL
    descUsername = 'Access Level Change'


class NotifierDevelopmentMode(rs.notifier.Notifier):
    """ Notify when development mode was toggled.
    """

    descServerName = c.Notifier.DEV_MODE
    descUsername = 'Development Mode Change'


class NotifierRigSelected(rs.notifier.Notifier):
    """ Notify when rig selection has changed.
    """

    descServerName = c.Notifier.RIG_SELECTION
    descUsername = 'Rig Selection Changed'


class NotifierCommandRegionsStateChanged(rs.notifier.Notifier):
    """
    When users pushes command regions disable button.
    """
    descServerName = c.Notifier.CMD_REGION_DISABLE
    descUserName = 'Command Regions Disable'
