

import lx
import modo

from .core import service
from .log import log
from .component_setups.rig import RigComponentSetup
from .component_setup import ComponentSetup
from .attach_set import AttachmentSet
from .items.root_item import RootItem
from .rig import Rig
from .rig_structure import RigStructure
from .component import Component
from . import const as c


class AttachOperator(object):
    """ Attach operator allows for managing attachment sets of the rig.
    
    Parameters
    ----------
    rootObject : RootItem, Rig
        Root object to initialise the operator with.

    Raises
    ------
    TypeError:
        When trying to initialise with wrong item.
    """
    
    GRAPH_NAME = 'rs.attach'

    def attachItem(self, modoItem, targetModoItem, attachmentType):
        """ Attach an item to the rig as an item of a given type.
        
        Returns
        -------
        Item, None
            If attachment set converts attached item to a rig item this rig
            item is returned. None is returned otherwise.
        """
        attachSet = self._getAttachmentSet(attachmentType)
        if attachSet is None:
            lx.out('Item cannot be attached')
            return
        return attachSet.attachItem(modoItem, targetModoItem)

    def detachItem(self, modoItem):
        """ Detaches given item from the rig.
        """
        try:
            component = Component.getFromModoItem(modoItem)
        except TypeError:
            return
        
        try:
            component.detachItem(modoItem)
        except AttributeError:
            return

    @property
    def attachments(self):
        """ Gets all attachment items in a rig.
        
        This will return rig items where possible and modo items
        if attachment set members are not of any rig item type.
        So watch out for mixed list.
        
        Returns
        -------
        list of rig Item, list of modo.Item
        """
        attachments = []
        for attset in self.sets:
            attachments.extend(attset.items)
        return attachments
    
    @property
    def attachmentsModoItems(self):
        """ Gets all attachment items in a rig as modo Items.
        
        Returns
        -------
        list of modo.Item
        """
        attachments = []
        for attset in self.sets:
            attachments.extend(attset.modoItems)
        return attachments

    @property
    def sets(self):
        """ Gets all attachment sets in a rig.
        
        Returns
        -------
        list of AttachmentSet
        """
        return self._rigStructure.getComponentsByGraph(c.Graph.ATTACHMENTS)

    def getAttachmentsOfType(self, types):
        """ Gets a list of attachments of a given type(s).
        
        Paramters
        ---------
        types : str, list of str
            The type is a string identifier of the attachment set to query.
        
        Return
        ------
        list of Item, list of modo.Item
            Empty list is returned when there are no attachments of a given type found.
        """
        if type(types) not in (list, tuple):
            types = [types]

        attachments = []
        for attset in self.sets:
            if attset.descIdentifier not in types:
                continue
            attachments.extend(attset.items)
        return attachments

    # -------- Private methods

    def _getAttachmentSet(self, identifier, autoCreate=True):
        """ Gets the attachment set object using its type identifier.
        
        Parameters
        ----------
        identifier : str
            One of const.AttachSetType constants.

        autoCreate : bool
            When True required set will be created if it doesn't exist yet.
        
        Returns
        -------
        AttachmentSet, None
        """
        attachSets = self._rigStructure.getComponents(identifier)
        attachSet = None
        if len(attachSets) == 0:
            if autoCreate:
                attachSet = self._newAttachSetup(identifier)
        else:
            attachSet = attachSets[0]
        return attachSet

    def _newAttachSetup(self, attachSetIdentifier):
        return self._rigStructure.newComponent(attachSetIdentifier)
        
    def __init__ (self, rootObject):
        if isinstance(rootObject, RootItem):
            self._rigRootItem = rootObject
            self._rig = Rig(rootObject)
        elif isinstance(rootObject, Rig):
            self._rigRootItem = rootObject.rootItem
            self._rig = rootObject
        else:
            raise TypeError
        self._rigSetup = RigComponentSetup(self._rigRootItem.modoItem)
        self._rigStructure = RigStructure(self._rigRootItem)
        
