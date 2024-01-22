
""" Notifier base system component.
"""


import lx
import lxifc


class Notifier(lxifc.Notifier, lxifc.CommandEvent):
    """ Notifier used to update rigging system UI.

    See SDK Wiki for tutorial on python notifiers:
    http://sdk.luxology.com/wiki/Python_Notifier_Example
    
    Note that Notifier is SystemComponent. It doesn't inherit
    from SystemComponent class because MODO won't bless such class
    but it does implement SystemComponent interface.
    """
    masterList = {}
 
    descServerName = ''
    descUsername = ''
    
    # -------- System Component Interface

    @classmethod
    def sysType(cls):
        return 'notifier'
    
    @classmethod
    def sysIdentifier(cls):
        return cls.descServerName

    @classmethod
    def sysUsername(cls):
        return cls.descUsername

    @classmethod
    def sysSingleton(cls):
        return True

    @classmethod
    def sysServer(cls):
        return True

    # -------- Notifier interface

    def noti_Name (self):
        return self.descServerName
 
    def noti_AddClient (self, event):
        """ Method is called when new client wants to register to notifier.
        """
        self.masterList[event.__peekobj__()] = event
 
    def noti_RemoveClient (self, event):
        if event.__peekobj__() in self.masterList:
            del self.masterList[event.__peekobj__()]
 
    def notify (self, flags):
        """ Calls every client's event method with flags that were set for notifier.
        """
        for event in self.masterList:
            evt = lx.object.CommandEvent(self.masterList[event])
            evt.Event(flags)
