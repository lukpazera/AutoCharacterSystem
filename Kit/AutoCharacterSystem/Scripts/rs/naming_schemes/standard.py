

from ..naming_scheme import NamingScheme
from ..const import NameToken as n
from ..const import RigItemType as t
from ..const import ItemFeatureType as i
from ..const import MetaGroupType as m


class NamingSchemeStandard(NamingScheme):
    
    descIdentifier = 'standard'
    descUsername = 'Standard'
    
    formatGeneric = [n.RIG_NAME, '<__', n.SIDE, n.MODULE_NAME, '<_', n.BASE_NAME, n.ITEM_TYPE, n.ITEM_FEATURE, n.MODO_ITEM_TYPE]
    formatByItemType = {t.ROOT_ITEM: [n.RIG_NAME, '__Rig (Folder)'],
                        t.ROOT_ASSM: [n.RIG_NAME, '__RootAssembly'],
                        t.MODULE_ROOT: [n.RIG_NAME, '<__', n.SIDE, n.BASE_NAME, ' (Module)'],
                        t.MODULE_ASSM: [n.RIG_NAME, '<__', n.SIDE, n.BASE_NAME]}

    formatGenericMeta = [n.RIG_NAME, '<__', n.BASE_NAME]
    formatByGroupTypeMeta = {m.ACTOR: [n.RIG_NAME]}

    itemTypeTokens = {t.PLUG: ' (Plug)',
                      t.SOCKET: ' (Socket)',
                      t.GUIDE: ' (Guide)',
                      t.REFERENCE_GUIDE: ' (RefGuide)',
                      t.BIND_LOCATOR: ' (Bind)',
                      t.PIECE_ASSM: ' (Piece)',
                      t.GUIDE_ASSM: ' (Guide)',
                      t.MIRROR_CHAN_GROUP: ' (MirrorChannels)',
                      t.RIG_CLAY_ASSEMBLY: ' (RigClayAssm)'}

    modoItemTypeTokens = {'groupLocator': ' (Folder)',
                          'genInfluence': ' (Influence)',
                          'deformGroup': ' (NormalizingFolder)',
                          'deformFolder': ' (DeformFolder)',
                          'morphDeform': ' (MorphInfluence)',
                          'itemInfluence': ' (ItemInfluence)',
                          'widget': ' (Handle)',
                          'weightContainer': ' (WeightContainer)',
                          'cmdRegionPolygon': ' (PolyCmdRegion)'}
    
    itemFeatureTokens = {i.CONTROLLER: ' (Ctrl)',
                         i.CONTROLLER_GUIDE: ' (Ctrl)'}
    
    leftToken = 'Left.'
    rightToken = 'Right.'
