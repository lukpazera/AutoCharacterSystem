

import modo
import modox

from . import command
from . import scene
from . import const as c
from .item_features.controller import ControllerItemFeature as Controller


class AnimCommandScope(object):
    AUTO = 'auto'
    RIG = 'rig'
    ITEM = 'item'
    CHANNEL = 'chan'


class AnimCommand(command.Command):
    """ Animation commmand.
    
    Commands working on controllers can inherit from this class
    to get a few utility methods.
    
    Arguments
    ---------
    scope : string
        Scope arguments defines whether the animation command should work on
        currently selected channels, items or an entire irg.
    """

    ARG_SCOPE = 'scope'
    
    Scope = AnimCommandScope

    def arguments(self):
        scope = command.Argument(self.ARG_SCOPE, 'string')
        scope.defaultValue = self.Scope.AUTO
        scope.flags = 'optional'
        return [scope]
    
    def setupMode(self):
        return False

    def notifiers(self):
        notifiers = command.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+l'))
        return notifiers

    @property
    def scope(self):
        """ Gets a scope of elements that this command should affect.
        
        Returns
        -------
        Scope
            One of predefined scope constants from the Scope class.
        """
        scope = self.getArgumentValue(self.ARG_SCOPE)
        if scope != self.Scope.AUTO:
            return scope
        if self.isAnyControllerSelected:
            return self.Scope.ITEM
        return self.Scope.RIG

    @property
    def channelsToEdit(self):
        """ Gets a list of channels that need to be edited.
        
        The list is based on the scope.
        
        Returns
        -------
        list of modo.Channel
        """
        channels = []
        scope = self.scope
        if scope == self.Scope.RIG:
            return self._rigScopeChannels
        elif scope == self.Scope.ITEM:
            return self._itemScopeChannels
        elif scope == self.Scope.CHANNEL:
            return modox.ChannelSelection().selected

    @property
    def isAnyControllerSelected(self):
        selection = modo.Scene().selected
        if selection:
            for item in selection:
                try:
                    ctrl = Controller(item)
                except TypeError:
                    continue
                return True
        return False

    # -------- Private methods

    @property
    def _rigScopeChannels(self):
        controllers = self._controllersFromRigs
        return self._channelsFromControllers(controllers)

    @property
    def _itemScopeChannels(self):
        controllers = self._selectedControllers
        return self._channelsFromControllers(controllers)

    @property
    def _controllersFromRigs(self):
        """ Gets a list of controllers that the command
        should operate on.
        
        Returns
        -------
        list of Controller
        """
        controllers = []
        rsScene = scene.Scene()
        for rig in rsScene.selectedRigs:
            elementsInRig = rig.getElements(c.ElementSetType.CONTROLLERS)
            for item in elementsInRig:
                try:
                    ctrl = Controller(item)
                except TypeError:
                    continue
                controllers.append(ctrl)
        return controllers

    @property
    def _selectedControllers(self):
        controllers = []
        selection = modo.Scene().selected
        if selection:
            for item in selection:
                try:
                    ctrl = Controller(item)
                except TypeError:
                    continue
                controllers.append(ctrl)
        return controllers
    
    def _channelsFromControllers(self, controllersList):
        channels = []
        for ctrl in controllersList:
            if ctrl.locked:
                continue
            channels.extend(ctrl.animatedChannels)
        return channels
