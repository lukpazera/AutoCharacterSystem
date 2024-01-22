import lx
import modo

from . import sys_component
from . import const as c
from .rig import Rig


class RigCommand(object):
    """ Rig commands allow for customising rigs by firing a piece of code with arguments.

    Commands are shown as buttons main rig properties.

    Attributes
    ----------
    descIdentifier : str
        Identifier for the command, unique within particular rig commands.

    descUsername : str
        User friendly name for command that will be shown in UI.
    """

    descIdentifier = ''
    descUsername = ''
    descApplyGuide = False
    descRefreshContext = False

    def run(self, arguments):
        """ Implements a code that should be run with given set of arguments.
        """
        pass

    @property
    def rig(self):
        return self._rig

    # -------- Private methods

    def __init__(self, rig):
        self._rig = rig


class FeaturedRig(sys_component.SystemComponent):
    """
    Featured rig is a rig that is supported with code and exposes extra features.

    Featured rigs have to be registered with the system using their identifier.
    They won't be seen and their properties will not show up in UI otherwise.

    Parameters
    ----------
    rig : Rig
        Rig object that relates to this featured rig.

    Attributes
    ----------
    descIdentifier : str
        Unique string identifier for the rig that is being implemented.

    descUsername : str
        User friendly name for rig that will be shown in log outputs, etc.

    descFeatures : [RigCommand, RigProperty]
        List of properties and commands that the rog is exposing.

    DIVIDER : str
        Use this contant to insert divider into rig properties form.

    Raises
    ------
    TypeError
        When trying to initialize this instance with object that is not Rig.
    """

    DIVIDER = "- "

    descIdentifier = ''
    descUsername = ''
    descFeatures = []

    # -------- System component attributes, do not touch.

    @classmethod
    def sysType(cls):
        return c.SystemComponentType.FEATURED_RIG

    @classmethod
    def sysIdentifier(cls):
        return cls.descIdentifier

    @classmethod
    def sysUsername(cls):
        return cls.descUsername + ' Featured Rig'

    # -------- Public interface

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
            elif not issubclass(prop, RigCommand):
                continue
            if prop.descIdentifier == ident:
                return prop
        return None

    def onRun(self, commandIdent, arguments):
        """ Called when module command is ran.
        """
        cmdClass = self.getCommandClass(commandIdent)
        if cmdClass is not None:
            return cmdClass(self._rig).run(arguments)

    @property
    def rig(self):
        return self._rig

    # -------- Private methods

    def __init__(self, rig):
        if not isinstance(rig, Rig):
            raise TypeError

        self._rig = rig
