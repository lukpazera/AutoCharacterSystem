
from ..naming_scheme import NamingScheme
from ..const import NameToken as n
from ..const import RigItemType as t
from ..const import ItemFeatureType as i
from ..const import MetaGroupType as m


class NameSchemeAlternate(NamingScheme):

    descIdentifier = 'alternate'
    descUsername = 'Alternate'

    formatGeneric = [n.RIG_NAME, '<_', n.ITEM_TYPE, n.ITEM_FEATURE, n.MODO_ITEM_TYPE, n.SIDE, n.MODULE_NAME, '<_', n.BASE_NAME]
    formatByItemType = {t.ROOT_ITEM: [n.RIG_NAME, '_FOLDER_Rig'],
                        t.ROOT_ASSM: [n.RIG_NAME, '_ASSEMBLY_Root'],
                        t.MODULE_ROOT: [n.RIG_NAME, '<_', 'MODULE_', n.SIDE, n.BASE_NAME],
                        t.MODULE_ASSM: [n.RIG_NAME, '<_', n.SIDE, n.BASE_NAME]}

    formatGenericMeta = [n.RIG_NAME, '<_', n.BASE_NAME]
    formatByGroupTypeMeta = {m.ACTOR: [n.RIG_NAME]}

    itemTypeTokens = {t.PLUG: 'PLUG_',
                      t.SOCKET: 'SOCKET_',
                      t.GUIDE: 'GUIDE_',
                      t.REFERENCE_GUIDE: 'REFGUIDE_',
                      t.BIND_LOCATOR: 'BIND_',
                      t.PIECE_ASSM: 'PIECE_',
                      t.GUIDE_ASSM: 'GUIDE_',
                      t.MIRROR_CHAN_GROUP: 'MIRRORCHANS_',
                      t.RIG_CLAY_ASSEMBLY: 'RIGCLAYASSM_'}

    modoItemTypeTokens = {'groupLocator': 'FOLDER_',
                          'genInfluence': 'GENINF_',
                          'morphDeform': 'MORPHINF_',
                          'widget': 'HANDLE_',
                          'weightContainer': 'WEIGHTCONTAINER_',
                          'cmdRegionPolygon': 'POLYCMDREGION_'}

    itemFeatureTokens = {i.CONTROLLER: 'CTRL_',
                         i.CONTROLLER_GUIDE: 'CTRL_'}

    leftToken = 'LEFT_'
    rightToken = 'RIGHT_'
    centerToken = 'CNTR_'


