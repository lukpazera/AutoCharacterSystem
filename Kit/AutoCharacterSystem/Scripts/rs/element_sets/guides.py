

from ..element_set import ItemsElementSet
from ..element_set import ElementSetFromMetaGroupItems
from ..meta_rig import MetaRig
from ..const import MetaGroupType
from ..const import ElementSetType
from ..item_features.controller_guide import ControllerGuideItemFeature as ControllerGuide
from ..log import log


class GuidesElementSet(ElementSetFromMetaGroupItems):
    
    descIdentifier = ElementSetType.GUIDES
    descUsername = 'Guides'
    descMetaGroupIdentifier = MetaGroupType.GUIDES
    

class ControllerGuidesElementSet(ElementSetFromMetaGroupItems):
    """ Elements set that includes only non-symmetric controller guides.
    
    Elements are filtered items from guides meta group.
    The class doesn't inherit from meta group element set though
    because item properties like visible and selectable need to changed
    on individual items rather then on group level.
    """
    descIdentifier = ElementSetType.CONTROLLER_GUIDES
    descUsername = 'Driver Guides'
    descMetaGroupIdentifier = MetaGroupType.GUIDES
    
    @property
    def elements(self):
        elements = super(ControllerGuidesElementSet, self).elements
        guideCtrlModoItems = []
        for modoItem in elements:
            try:
                guideController = ControllerGuide(modoItem)
            except TypeError:
                continue
            guideCtrlModoItems.append(modoItem)

        return guideCtrlModoItems


class EditableControllerGuidesElementSet(ElementSetFromMetaGroupItems):
    """
    Element set with controller guides that can be edited in guide context.
    """

    descIdentifier = ElementSetType.EDITABLE_CONTROLLER_GUIDES
    descUsername = 'Editable Controller Guides'
    descMetaGroupIdentifier = MetaGroupType.GUIDES

    @property
    def elements(self):
        elements = super(EditableControllerGuidesElementSet, self).elements
        guideCtrlModoItems = []
        for modoItem in elements:
            try:
                guideController = ControllerGuide(modoItem)
            except TypeError:
                continue
            if guideController.item.symmetricGuide is not None:
                continue
            guideCtrlModoItems.append(modoItem)

        return guideCtrlModoItems