

import lx

from . import const as c
from .log import log


class UserValuesOperator(object):
    
    def registerTemporary(self, name, valueType, defaultValue=None):
        """ Registers new temporary user value.
        
        Temporary user values register only throughout current MODO session.
        They need to be recreated on each MODO startup.
        
        Parameters
        ----------
        name : str
            Name of the user value that needs to be registered (created).

        valueType : str
            Value type as string: float, boolean, etc.
            It's probably the same as the string that command argument type takes.
        
        defaultValue : dynamic, optional
        """
        try:
            lx.eval('!user.defNew name:%s type:%s life:temporary' % (name, valueType))
        except RuntimeError:
            log.out("Registering %s user value failed!" % name, log.MSG_ERROR)
        else:
            self.set(name, defaultValue)

    def get(self, name):
        """ Gets value with a given name.
        
        Parameters
        ----------
        name : str
        
        Returns
        -------
        value, None
            None is returned when reaching user value was not successfull.
        """
        try:
            return lx.eval('!user.value %s ?' % name)
        except RuntimeError:
            return None

    def set(self, name, value):
        """ Sets value with a given name.
        
        Parameters
        ----------
        name : str
        
        value : dynamic
            Pass value that fits the type of the user value you want to set.
        """
        if value is None:
            return
        try:
            lx.eval('!user.value {%s} {%s}' % (name, str(value)))
        except RuntimeError:
            log.out('Cannot set %s user value.' % name, log.MSG_ERROR)
    
    # -------- Private methods
        
    def __getitem__(self, ident):
        return self.get(ident)

userValues = UserValuesOperator()