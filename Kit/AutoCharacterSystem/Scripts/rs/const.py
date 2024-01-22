
""" Global Rigging System constants.
"""


import lx
import lxu


class TagID(object):
    META_GROUP = 'RSMG'


class TagIDInt(object):
    META_GROUP = lxu.utils.lxID4(TagID.META_GROUP)

class Path(object):
    MAIN = 'main'
    CONFIGS = 'cfg'
    TEMP_FILES = 'temp'
    SCRIPTS = 'scripts'
    PRESETS = 'presets'
    PRESETS_INTERNAL = 'intpresets'
    PIECES = 'pieces'
    MODULES = 'modules'
    MODULES_INTERNAL = 'intmodules'
    RIGS = 'rigs'
    THUMBNAILS = 'thumbs'
    TEMPLATES = 'tmplt'
    SCENE_TEMPLATES = 'stmplt'

class Graph(object):
    EDIT_RIG = 'rs.editRig'
    EDIT_MODULE = 'rs.editModule'
    MODULES = 'rs.modules'
    BIND_MESHES = 'rs.bindMeshes'
    ATTACHMENTS = 'rs.attach'

class EventTypes(object):
    EDIT_RIG_CHANGED = 'edrig'
    
    RIG_COLOR_SCHEME_CHANGED = 'rigColSchm'
    ITEM_ADDED = 'itemAdded'
    ITEM_REMOVED = 'itemRemoved'
    ITEM_CHANGED = 'itemChanged'
    ITEM_SIDE_CHANGED = 'itemSideChanged'
    ITEM_CHAN_EDIT_BATCH_PRE = 'itemChanEdBPre'
    ITEM_CHAN_EDIT_BATCH_POST = 'itemChanEdBPost'
    
    RIG_ITEM_SELECTED = 'rgitemSel'
    RIG_REFERENCE_SIZE_CHANGED = 'rgrefsize'
    RIG_DROPPED = 'rgdrop'
    RIG_NAME_CHANGED = 'rgname'
    RIG_STANDARDIZE_PRE = 'rprestd'

    MODULE_NEW = 'modNew'
    MODULE_LOAD_POST = 'modLoadPost'
    MODULE_DROP_ACTION_PRE = 'modDropAPre'
    MODULE_DROP_ACTION_POST = 'modDropAPost'
    MODULE_SAVE_PRE = 'modSavePre'
    MODULE_SAVE_POST = 'modSavePost'
    MODULE_DELETE_PRE = 'modDelPre'
    MODULE_SIDE_CHANGED = 'modSideChanged'
    MODULE_NAME_CHANGED = 'modNameChanged'
    MODULE_GUIDE_SCALED = 'modGdScaled'
    PIECE_NEW = 'pieceNew'
    PIECE_SAVE_PRE = 'pieceSavePre'
    PIECE_LOAD_POST = 'pieceLoadPost'

    PLUG_CONNECTED = 'plgConn'
    PLUG_DISCONNECTED = 'plgDisConn'
    
    CHANNEL_SET_ADDED = 'chanSetAdded'
    GUIDE_APPLY_INIT = 'gdAppInit'
    GUIDE_APPLY_ITEM_SCAN = 'gdAppItemScan'
    GUIDE_APPLY_PRE = 'gdAppPre'
    GUIDE_APPLY_DO = 'gdAppDo'
    GUIDE_APPLY_POST = 'gdAppPost'
    GUIDE_APPLY_POST2 = 'gd2AppPost'
    GUIDE_LINK_CHANGED = 'gdLnk'

    CONTEXT_RIG_VIS_RESET = 'cxtvisreset'
    CONTEXT_RIG_VIS_SET = 'cxtvisset'

    MESH_RES_RENAMED = 'mresrename'
    MESH_RES_REMOVED = 'mresrem'
    
class Notifier(object):
    UI_GENERAL = 'rs.ui.general'
    CONTROLLER = 'rs.controller'
    ITEM_FEATURES_ADDREM = 'rs.itemFeaturesAddRemove'
    MODULE_PROPERTIES = 'rs.modProps'
    ACCESS_LEVEL = 'rs.accessLevel'
    DEV_MODE = 'rs.devMode'
    RIG_SELECTION = 'rs.rigSelect'
    BIND_MAP_UI = 'rs.bindMapUI'
    GAME_EXPORT = 'rs.gameExport'
    CMD_REGION_DISABLE = 'rs.cmdRegDis'

class Notify(object):
    ALL = lx.symbol.fCMDNOTIFY_CHANGE_ALL
    DATATYPE = lx.symbol.fCMDNOTIFY_DATATYPE
    DISABLE = lx.symbol.fCMDNOTIFY_DISABLE
    LABEL = lx.symbol.fCMDNOTIFY_LABEL
    VALUE = lx.symbol.fCMDNOTIFY_VALUE

class NameToken(object):
    RIG_NAME = 'rn'
    MODULE_NAME = 'mn'
    BASE_NAME = 'bn'
    ITEM_TYPE = 'tp'
    ITEM_FEATURE = 'if'
    MODO_ITEM_TYPE = 'mi'
    SIDE = 'sd'

class SystemComponentType(object):
    COMPONENT = 'cmp'
    COMPONENT_SETUP = 'cmpsetup'
    CONTEXT = 'context'
    ITEM = 'item'
    NAMING_SCHEME = 'nameScheme'
    META_GROUP = 'metagrp'
    PRESET_THUMBNAIL = 'presetthumb'
    EVENT_HANDLER = 'eventhandler'
    ITEM_FEATURE = 'itemfeature'
    FEATURED_RIG = 'frig'
    FEATURED_MODULE = 'fmodule'
    ELEMENT_SET = 'elset'
    COLOR_SCHEME = 'colorschm'
    XFRM_LINK_SETUP = 'xfrmls'
    ATTACH_SET = 'attset'
    SCENE_EVENT = 'scnevent'
    PRESET = 'pstsav'
    GAME_EXPORT_SET = 'gameex'
    
class RigItemType(object):
    GENERIC = 'x'
    ROOT_ASSM = 'rootassm'
    ROOT_ITEM = 'rootitem'
    DEFORM_ROOT = 'dfrmroot'
    NORMALIZING_FOLDER = 'normfld'
    DEFORM_FOLDER = 'dfrmfld'
    POST_CORRECTIVE_MORPHS_FOLDER = 'postmorphfld'
    MODULE_ROOT = 'moduleroot'
    MODULE_ASSM = 'moduleassm'
    MODULE_SET_ROOT = 'modsetroot'
    MODULE_SET_ASSM = 'modsetassm'
    MODULE_RIG_ASSM = 'modrigassm'
    PLUG = 'plug'
    SOCKET = 'socket'
    GUIDE = 'guide'
    REFERENCE_GUIDE = 'bufguide'
    BIND_LOCATOR = 'bindloc'
    BIND_LOCATOR_SHADOW = 'shbindloc'
    RIGID_MESH = 'rgdmesh'
    BIND_PROXY = 'bmproxy'
    BIND_MESH = 'bmesh'
    MODULES_FOLDER = 'modfld'
    GEOMETRY_FOLDER = 'geofld'
    PIECE_ASSM = 'pieceassm'
    GUIDE_ASSM = 'gdassm'
    MIRROR_CHAN_GROUP = 'mirchangrp'
    IKFK_CHAIN_GROUP = 'ikfkcgrp'
    TRANSMITTER = 'transm'
    SPACE_SWITCHER = 'spswitch'
    RIG_CLAY_ASSEMBLY = 'rclayassm'

class ItemFeatureType(object):
    CONTROLLER = 'controller'
    COLOR = 'color'
    GUIDE = 'guide'
    CONTROLLER_GUIDE = 'ctrlgd'
    ITEM_LINK = 'itmlink'
    ITEM_SHAPE = 'itmshp'
    ITEM_AXIS = 'itmaxis'
    DRAW_XFRM_LINK = 'drawxfrmlink'
    IDENTIFIER = 'ident'
    CONTROLLER_FIT = 'fititmshp'
    DECORATOR = 'decor'
    EMBED_GUIDE = 'embgd'
    ITEM_MATCH_XFRM = 'xitmmatch'
    CHAIN_MATCH_XFRM = 'xchainmatch'
    IKFK_SWITCHER = 'ikfkswitch'
    IKFK_SOLVER_MATCH = 'ikfksolvmatch'
    
class ItemFeatureCategory(object):
    GENERAL = 'gen'
    DRAWING = 'draw'

class MetaGroupType(object):
    ROOT = 'root'
    BIND_LOCATORS = 'bindloc'
    LOCKED_CHANNELS = 'lchans'
    ACTOR = 'actor'
    CONTROLLERS = 'ctrls'
    CHANNEL_SETS = 'chansets'
    GUIDES = 'guides'
    PLUGS = 'plugs'
    SOCKETS = 'sockets'
    RIGID_MESHES = 'rgdmeshes'
    BIND_PROXIES = 'bmproxy'
    BIND_MESHES = 'bmmesh'
    DECORATORS = 'decor'

class ElementSetType(object):
    CONTROLLERS = 'ctrls'
    CONTROLLERS_SET = 'setctrls'
    BIND_SKELETON = 'bindskel'
    GUIDES = 'guides'
    CONTROLLER_GUIDES = 'dguides'
    EDITABLE_CONTROLLER_GUIDES = 'ectrlgd'
    PLUGS = 'plugs'
    SOCKETS = 'sockets'
    RIGID_MESHES = 'rgdmesh'
    BIND_PROXIES = 'bmproxy'
    BIND_MESHES = 'bmesh'
    RESOLUTION_BIND_MESHES = 'rbmesh'
    RESOLUTION_BIND_PROXIES = 'rbmproxy'
    RESOLUTION_RIGID_MESHES = 'rrgdmesh'
    DECORATORS = 'decor'

class ComponentType(object):
    MODULE_SET = 'modset'
    MODULE = 'module'
    BIND_MESHES = 'bmesh'
    RIGID_MESHES = 'rigidmesh'
    BIND_PROXIES = 'bmproxy'
    TEMPORARY = 'tmp'
    
class ComponentSetupType(object):
    RIG = 'rig'
    BIND_MESHES = 'bindmesh'
    RIGID_MESHES = 'rigidmesh'
    BIND_PROXIES = 'bmproxy'
    TEMPORARY = 'tmp'

class ModuleIdentifier(object):
    BASE = 'base'
    FK_CHAIN = 'std.fkChain'

class ModulePresetFilename(object):
    FK_CHAIN = 'Joint Chain'
    STD_JOINT = 'Joint Standard'
    ADV_JOINT = 'Joint Advanced'
    EYELIDS = 'Eyelids'

class AccessLevel(object):
    DEVELOPMENT = 2
    EDIT = 1
    ANIMATE = 0
    
class Context(object):
    GUIDE = 'guide'
    ANIMATE = 'animate'
    DEVELOP = 'dev'
    ASSEMBLY = 'assembly'
    MESHES = 'meshes'
    WEIGHT = 'weight'

class RigGraph(object):
    EDIT_RIG = 'rs.editRig'

class ItemCommand(object):
    GENERIC = 'rs.item.command'

class TriState(object):
    """ Tristate is used across MODO for options that can have 3 possible values.
    """
    DEFAULT = 0
    ON = 1
    OFF = 2

class ItemVisible(object):
    """ Item visibility has 4 possible states.
    """
    DEFAULT = 0
    YES = 1
    NO = 2
    NO_CHILDREN = 3

class ItemVisibleHint(object):
    DEFAULT = 'default'
    YES = 'on'
    NO = 'off'
    NO_CHILDREN = 'allOff'

class Side(object):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"

class SideInt(object):
    CENTER = 0
    LEFT = 1
    RIGHT = -1

class Axis(object):
    X = 0
    Y = 1
    Z = 2

class ModuleDropAction(object):
    NONE = "none"
    SNAP_TO_MOUSE = "mouse"
    REST_ON_GROUND = "ground"
    MOUSE_AND_GROUND = "both"

class DropScript(object):
    ITEM_ON_ITEM_SOURCE = 'rs_drop_item_src'
    ITEM_ON_ITEM_DESTINATION = 'rs_drop_item_dst'

class TransformLinkType(object):
    DYNA_PARENT = 'dp'
    DYNA_PARENT_NO_SCALE = 'dpns'
    STATIC = 'stt'
    WORLD_POS_PERMANENT = 'wposp'

class UIState(object):
    MESH_EDIT_MODE = 'meshEd'

class MeshesSubcontexts(object):
    BIND_MESHES = 'bindmesh'
    RIGID_MESHES = 'rigidmesh'
    BIND_PROXIES = 'bindproxy'
    RESOLUTION = 'res'
    RIG_CLAY = 'clay'

class FormSubcontexts(object):
    BIND = 'bind'
    WEIGHT = 'weight'

class AssemblySubcontexts(object):
    GENERAL = 'gen'
    ASSEMBLY = 'assm'
    DEVELOP = 'dev'

class GuideSubcontexts(object):
    EDIT = 'edit'
    GENERAL = 'gen'

class UserValue(object):
    LISTEN_TO_SCENE = 'rs.listenToScene'
    PRESET_DROP_ACTION_CODE = 'rs.presetDropActionCode'
    PRESET_DEST_IDENT = 'rs.presetDestIdent'
    PRESET_FILENAME = 'rs.presetFilename'

class MessageTable(object):
    GENERIC = 'rs.generic'
    DISABLE = 'rs.disable'
    CMDEXE = 'rs.cmdexe'
    CMDABORT = 'rs.cmdabort'
    CMDTOOLTIP = 'rs.cmdtooltip'
    BUTTON = 'rs.cmdbutton'
    DIALOG = 'rs.cmddialog'
    MODLABEL = 'rs.modlabel'
    MODTOOLTIP = 'rs.modtooltip'

class MessageKey(object):
    NO_RIGS = 'noRigs'
    NONE = 'none'
    UNKNOWN = 'unknown'

class KeyItem(object):

    # Main module folders
    GUIDE_FOLDER = "gdfld"
    EDIT_GUIDE_FOLDER = "editgdfld"
    RIG_FOLDER = "rigfld"
    BIND_SKELETON_FOLDER = "bskelfld"

    # Generic keys for deformation related items
    DEFORM_FOLDER = "dfrmfld"
    GENERAL_INFLUENCE = "geninf"

    # Other
    BIND_LOCATOR = "bindloc"
    CONTROLLER = "ctrl"
    TARGET_CONTROLLER = "ctrlTarget"
    CONTROLLER_GUIDE = "ctrlgd"
    ROOT_CONTROLLER_GUIDE = "rootctrlgd"
    TIP_CONTROLLER_GUIDE = "tipctrlgd"
    REFERENCE_GUIDE = "refgd"
    TIP_REFERENCE_GUIDE = "tiprefgd"
    SOCKET = "socket"
    PANEL_CONTROLLER = "panel"

class String(object):
    SYSTEM_PACKAGE_PREFIX = "rs."

class DefaultValue(object):
    CONTEXT = Context.ASSEMBLY
    REFERENCE_SIZE = 2.0

class DropActionCode(object):
    RIGHTPOSE = 'right'
    LEFTPOSE = 'left'
    POSE = 'pose'
    MIRRORPOSE = 'mpose'
    NEWACTION = 'naction'