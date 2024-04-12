
import lx
from .log import log as log
from .debug import debug
from .core import service as service
from . import const as c
from . import acs2
from . import io

import time
initTime = time.time()
log.out('Auto Character System initialization:', log.MSG_INFO)
log.startChildEntries()

from .scene import Scene

# Notifiers
from .notifiers.ui_general import NotifierUIGeneral
service.systemComponent.register(NotifierUIGeneral)
from .notifiers.ui_general import NotifierItemFeatureAddRemove
service.systemComponent.register(NotifierItemFeatureAddRemove)
from .notifiers.controller import NotifierController
service.systemComponent.register(NotifierController)
from .notifiers.ui_general import NotifierModuleProperties
service.systemComponent.register(NotifierModuleProperties)
from .notifiers.ui_general import NotifierAccessLevel
service.systemComponent.register(NotifierAccessLevel)
from .notifiers.ui_general import NotifierDevelopmentMode
service.systemComponent.register(NotifierDevelopmentMode)
from .notifiers.ui_general import NotifierRigSelected
service.systemComponent.register(NotifierRigSelected)
from .notifiers.ui_general import NotifierCommandRegionsStateChanged
service.systemComponent.register(NotifierCommandRegionsStateChanged)
from .bind_map import NotifierBindMapUI
service.systemComponent.register(NotifierBindMapUI)

# Commands
from .command import Command
from .command import RigCommand
from .command import base_OnModuleCommand
from .command import base_OnItemCommand
from .command import base_OnItemFeatureCommand
from . import command as cmd
from .command_anim import AnimCommand
from .command_notify import NotifierSet

# Base classes to inherit from
from .event import Event as base_Event
from .item import Item as base_Item
from .context import Context as base_Context
from .color_scheme import ColorScheme as base_ColorScheme
from .item_feature import ItemFeature as base_ItemFeature
from .item_feature import LocatorSuperTypeItemFeature as base_LocatorItemFeature
from .controller_if import Controller as base_Controller
from .controller_cmds import CmdControllerChannels as base_CmdControllerChannels
from .controller_cmds import CmdControllerChannelState as base_CmdControllerChannelState
from .controller_cmds import CmdControllerChannelsFCL as base_CmdControllerChannelsFCL
from .controller_cmds import CmdControllerChannelsPreset as base_CmdControllerChannelsPreset
from .controller_cmds import CmdControllerChanPresetChoice as base_CmdControllerChanPresetChoice
from .module_feature import FeaturedModule as base_FeaturedModule
from .module_feature import ModuleProperty as base_ModuleProperty
from .module_feature import ModuleVariant as base_ModuleVariant
from .module_feature import ModuleCommand as base_ModuleCommand
from .rig_feature import RigCommand as base_RigCommand
from .rig_feature import FeaturedRig as base_FeaturedRig
from .piece_serial import SerialPiece as base_SerialPiece
from .piece_serial import SerialPiecesSetup as base_SerialPiecesSetup
from .game_export import GameExportSet as base_GameExportSet
from .game_export import GameExportCommand as base_GameExportCommand

# To get access to class methods
from .item import Item
from .sys_component import SystemComponent
from .context_op import ContextOperator
from .naming_scheme import NamingScheme
from .name_op import NameOperator as NamingSchemeOperator
from .item_feature_op import ItemFeatureOperator as ItemFeatures
from .item_utils import ItemUtils
from .event_handler import EventHandler
from .guide import Guide
from .attach_op import AttachOperator as Attachments
from .guide_symmetry import GuideSymmetry as GuideTransforms
from .module_guide import ModuleGuide
from .module_map import ModuleMap
from .module_op import ModuleOperator
from .module_feature_op import FeaturedModuleOperator
from .piece_op import PieceOperator
from .module_set import ModuleSet
from .bind_skel import BindSkeleton
from .bind_skel_shadow import BindSkeletonShadow
from .bind_skel_shadow import BindSkeletonShadowDescription
from .bind_skel_shadow import BakeShadowDescription
from .bind_skel_shadow import BindShadowDescription
from .bind import Bind
from .bind_modo import ModoBind
from .bind_meshes_op import BindMeshesOperator as BindMeshes
from .resolutions import Resolutions
from .bake_op import BakeDescription
from .bake_op import BakeOperator
from .xfrm_in_mesh import TransformsInMesh
from .util import run
from .util_select import SelectionUtils
from .xfrm_link import TransformLink
from .piece import Piece
from .shape_op import ShapesOperator
from .deform_stack import DeformStack
from .symmetry import SymmetryUtils
from .pose import Pose
from .action import Action
from .retarget import Retargeting
from .rig_clay_op import RigClayOperator
from .rig_clay_op import RigClayModuleOperator
from .rig_clay_op import RigClayUtils
from .attach_item import AttachItem
from .controller_ui import ChannelSet

# Events
from .events.item_added import EventItemAdded
service.events.registerEvent(EventItemAdded)
from .events.item_changed import EventItemChanged
service.events.registerEvent(EventItemChanged)
from .events.chanset_added import EventChannelSetAdded
service.events.registerEvent(EventChannelSetAdded)
from .events.side_changed import EventModuleSideChanged
service.events.registerEvent(EventModuleSideChanged)
from .events.side_changed import EventItemSideChanged
service.events.registerEvent(EventItemSideChanged)
from .events.item import EventItemRemoved
service.events.registerEvent(EventItemRemoved)
from .events.item import EventItemChannelEditBatchPre
service.events.registerEvent(EventItemChannelEditBatchPre)
from .events.item import EventItemChannelEditBatchPost
service.events.registerEvent(EventItemChannelEditBatchPost)
from .events.item import EventRigItemSelected
service.events.registerEvent(EventRigItemSelected)
from .events.color_scheme_changed import EventModuleSideChanged
service.events.registerEvent(EventModuleSideChanged)
from .events.guide import EventGuideApplyInit
service.events.registerEvent(EventGuideApplyInit)
from .events.guide import EventGuideApplyItemScan
service.events.registerEvent(EventGuideApplyItemScan)
from .events.guide import EventGuideApplyPre
service.events.registerEvent(EventGuideApplyPre)
from .events.guide import EventGuideApplyPost
service.events.registerEvent(EventGuideApplyPost)
from .events.guide import EventGuideApplyPost2
service.events.registerEvent(EventGuideApplyPost2)
from .events.guide import EventModuleGuideScaled
service.events.registerEvent(EventModuleGuideScaled)
from .events.guide import EventGuideLinkChanged
service.events.registerEvent(EventGuideLinkChanged)
from .events.module import EventModuleNew
service.events.registerEvent(EventModuleNew)
from .events.module import EventModuleLoadPost
service.events.registerEvent(EventModuleLoadPost)
from .events.module import EventModuleDropActionPre
service.events.registerEvent(EventModuleDropActionPre)
from .events.module import EventModuleDropActionPost
service.events.registerEvent(EventModuleDropActionPost)
from .events.module import EventModuleSavePre
service.events.registerEvent(EventModuleSavePre)
from .events.module import EventModuleSavePost
service.events.registerEvent(EventModuleSavePost)
from .events.module import EventModuleDeletePre
service.events.registerEvent(EventModuleDeletePre)
from .events.module import EventModuleNameChanged
service.events.registerEvent(EventModuleNameChanged)
from .events.module import EventPlugConnected
service.events.registerEvent(EventPlugConnected)
from .events.module import EventPlugDisconnected
service.events.registerEvent(EventPlugDisconnected)
from .events.module import EventPieceNew
service.events.registerEvent(EventPieceNew)
from .events.module import EventPiecePreSave
service.events.registerEvent(EventPiecePreSave)
from .events.module import EventPieceLoadPost
service.events.registerEvent(EventPieceLoadPost)
from .events.scene import EventContextRigResetVisible
service.events.registerEvent(EventContextRigResetVisible)
from .events.scene import EventContextRigSetVisible
service.events.registerEvent(EventContextRigSetVisible)
from .events.scene import EventEditRigChanged
service.events.registerEvent(EventEditRigChanged)
from .events.mesh_resolution import EventMeshResolutionRenamed
service.events.registerEvent(EventMeshResolutionRenamed)
from .events.mesh_resolution import EventMeshResolutionRemoved
service.events.registerEvent(EventMeshResolutionRemoved)
from .events.rig import EventRigReferenceSizeChanged
service.events.registerEvent(EventRigReferenceSizeChanged)
from .events.rig import EventRigDropped
service.events.registerEvent(EventRigDropped)
from .events.rig import EventRigNameChanged
service.events.registerEvent(EventRigNameChanged)
from .events.rig import EventRigStandardizePre
service.events.registerEvent(EventRigStandardizePre)

# Scene Events
from .scene_event import event_RootSelected
service.systemComponent.register(event_RootSelected)
from .scene_event import event_ModuleRootSelected
service.systemComponent.register(event_ModuleRootSelected)
from .scene_event import event_ItemParented
service.systemComponent.register(event_ItemParented)
from .ikfk import event_MatchChainItemChanged
service.systemComponent.register(event_MatchChainItemChanged)
from .rig_clay_op import event_CommandRegionsDisableToggled
service.systemComponent.register(event_CommandRegionsDisableToggled)

# Event Handlers
from .event_handlers.meta_rig import MetaRigEventHandler
service.events.registerHandler(MetaRigEventHandler)
from .event_handlers.color_scheme import ColorSchemeEventHandler
service.events.registerHandler(ColorSchemeEventHandler)
from .event_handlers.guide_match import MatchToGuideEventHandler
service.events.registerHandler(MatchToGuideEventHandler)
from .event_handlers.attach import AttachmentsEventHandler
service.events.registerHandler(AttachmentsEventHandler)
from .event_handlers.deform_stack import DeformStackEventHandler
service.events.registerHandler(DeformStackEventHandler)
from .event_handlers.plugs import PlugsEventHandler
service.events.registerHandler(PlugsEventHandler)
from .event_handlers.module_map import ModulesMapEventHandler
service.events.registerHandler(ModulesMapEventHandler)
from .decorator import DecoratorEventHandler
service.events.registerHandler(DecoratorEventHandler)
from .event_handlers.context_op import ContextOperatorEventHandler
service.events.registerHandler(ContextOperatorEventHandler)
from .vis_op import VisibilityEventHandler
service.events.registerHandler(VisibilityEventHandler)
from .items.bind_mesh import BindMeshEventHandler
service.events.registerHandler(BindMeshEventHandler)
from .items.bind_proxy import BindProxyEventHandler
service.events.registerHandler(BindProxyEventHandler)
from .items.rigid_mesh import RigidMeshEventHandler
service.events.registerHandler(RigidMeshEventHandler)
from .rig_size_op import RigSizeEventHandler
service.events.registerHandler(RigSizeEventHandler)
from .shape_op import ShapesOperatorEventHandler
service.events.registerHandler(ShapesOperatorEventHandler)
from .guide_symmetry import GuideSymmetryEventHandler
service.events.registerHandler(GuideSymmetryEventHandler)
from .event_handlers.channel_set import ChannelSetEventHandler
service.events.registerHandler(ChannelSetEventHandler)
from .controller_dyna_space import DynamicSpaceEventHandler
service.events.registerHandler(DynamicSpaceEventHandler)
from .rig_clay_op import RigClayEventHandler
service.events.registerHandler(RigClayEventHandler)

# Contexts
from .contexts.assembly import ContextAssembly
service.systemComponent.register(ContextAssembly)
from .contexts.guide import ContextGuide
service.systemComponent.register(ContextGuide)
from .contexts.meshes import ContextMeshes
service.systemComponent.register(ContextMeshes)
from .contexts.weight import ContextWeight
service.systemComponent.register(ContextWeight)
from .contexts.animate import ContextAnimate
service.systemComponent.register(ContextAnimate)

# Naming Schemes
from .naming_schemes.standard import NamingSchemeStandard
service.systemComponent.register(NamingSchemeStandard)
from .naming_schemes.alternate import NameSchemeAlternate
service.systemComponent.register(NameSchemeAlternate)

# Components
from .module import Module
service.systemComponent.register(Module)
from .bind_meshes import BindMeshes as BindMeshesComponent
service.systemComponent.register(BindMeshesComponent)
# Attachment set components
from .attach_sets import RigidMeshesAttachmentSet
service.systemComponent.register(RigidMeshesAttachmentSet)
from .attach_sets import BindProxiesAttachmentSet
service.systemComponent.register(BindProxiesAttachmentSet)

# Component Setups
from .component_setups.rig import RigComponentSetup
service.systemComponent.register(RigComponentSetup)
from .component_setups.module import ModuleComponentSetup
service.systemComponent.register(ModuleComponentSetup)
from .module_set import ModuleSetComponentSetup
service.systemComponent.register(ModuleSetComponentSetup)
from .component_setups.meshes import BindMeshesComponentSetup
service.systemComponent.register(BindMeshesComponentSetup)
from .component_setups.meshes import RigidMeshesComponentSetup
service.systemComponent.register(RigidMeshesComponentSetup)
from .component_setups.meshes import BindProxiesComponentSetup
service.systemComponent.register(BindProxiesComponentSetup)

# Items
from .items.root_item import RootItem
service.systemComponent.register(RootItem)
from .items.root_assm import RootAssembly
service.systemComponent.register(RootAssembly)
from .items.generic import GenericItem
service.systemComponent.register(GenericItem)
from .items.module_root import ModuleRoot
service.systemComponent.register(ModuleRoot)
from .items.module_assm import ModuleAssembly
service.systemComponent.register(ModuleAssembly)
from .module_set import ModuleSetRoot
service.systemComponent.register(ModuleSetRoot)
from .module_set import ModuleSetAssembly
service.systemComponent.register(ModuleSetAssembly)
from .items.bind_loc import BindLocatorItem
service.systemComponent.register(BindLocatorItem)
from .items.plug import PlugItem
service.systemComponent.register(PlugItem)
from .items.socket import SocketItem
service.systemComponent.register(SocketItem)
from .items.guide import GuideItem
service.systemComponent.register(GuideItem)
from .items.guide import ReferenceGuideItem
service.systemComponent.register(ReferenceGuideItem)
from .items.rigid_mesh import RigidMeshItem
service.systemComponent.register(RigidMeshItem)
from .items.bind_proxy import BindProxyItem
service.systemComponent.register(BindProxyItem)
from .items.bind_mesh import BindMeshItem
service.systemComponent.register(BindMeshItem)
from .items.bind_loc_shadow import BindLocatorShadow
service.systemComponent.register(BindLocatorShadow)
from .items.deform_stack import DeformStackRootItem
service.systemComponent.register(DeformStackRootItem)
from .items.deform_stack import NormalizingFolderItem
service.systemComponent.register(NormalizingFolderItem)
from .items.deform_stack import PostCorrectiveMorphsFolderItem
service.systemComponent.register(PostCorrectiveMorphsFolderItem)
from .items.layout import ModulesFolder
service.systemComponent.register(ModulesFolder)
from .items.layout import GeometryFolder
service.systemComponent.register(GeometryFolder)
from .piece import PieceAssembly
service.systemComponent.register(PieceAssembly)
from .items.module_sub import GuideAssembly
service.systemComponent.register(GuideAssembly)
from .items.module_sub import ModuleRigAssembly
service.systemComponent.register(ModuleRigAssembly)
from .items.module_sub import MirrorChannelsGroup
service.systemComponent.register(MirrorChannelsGroup)
from .transmit import TransmitterItem
service.systemComponent.register(TransmitterItem)
from .ikfk import IKFKChainGroup
service.systemComponent.register(IKFKChainGroup)
from .items.space_switcher import SpaceSwitcherItem
service.systemComponent.register(SpaceSwitcherItem)
from .rig_clay_op import RigClayAssemblyItem
service.systemComponent.register(RigClayAssemblyItem)

# Item features
from .item_features.identifier import IdentifierFeature
service.systemComponent.register(IdentifierFeature)
from .item_features.color import ColorItemFeature as ItemColor
service.systemComponent.register(ItemColor)
from .item_features.guide import GuideItemFeature
service.systemComponent.register(GuideItemFeature)
from .item_features.controller import ControllerItemFeature as Controller
service.systemComponent.register(Controller)
from .item_features.controller_guide import ControllerGuideItemFeature as ControllerGuide
service.systemComponent.register(ControllerGuide)
from .item_features.embed_guide import EmbedGuideFeature
service.systemComponent.register(EmbedGuideFeature)
from .item_features.item_shape import ItemShapeFeature
service.systemComponent.register(ItemShapeFeature)
from .item_features.item_shape import ItemAxisFeature
service.systemComponent.register(ItemAxisFeature)
from .item_features.item_link import ItemLinkFeature
service.systemComponent.register(ItemLinkFeature)
from .item_features.controller_fit import ControllerFitFeature
service.systemComponent.register(ControllerFitFeature)
from .decorator import DecoratorIF
service.systemComponent.register(DecoratorIF)
from .ikfk import MatchTransformItemFeature
service.systemComponent.register(MatchTransformItemFeature)
from .ikfk import IKFKSwitcherItemFeature
service.systemComponent.register(IKFKSwitcherItemFeature)
from .ikfk import IKSolverMatchExtras
service.systemComponent.register(IKSolverMatchExtras)
from .xfrm_link import DrawTransformLink
service.systemComponent.register(DrawTransformLink)

# Meta groups
from .meta_groups.root import RootMetaGroup
service.systemComponent.register(RootMetaGroup)
from .meta_groups.bindloc import BindLocatorsMetaGroup
service.systemComponent.register(BindLocatorsMetaGroup)
from .meta_groups.actor import ActorMetaGroup
service.systemComponent.register(ActorMetaGroup)
from .meta_groups.controllers import ControllersMetaGroup
service.systemComponent.register(ControllersMetaGroup)
from .meta_groups.locked_chans import LockedChannelsMetaGroup
service.systemComponent.register(LockedChannelsMetaGroup)
from .meta_groups.channel_sets import ChannelSetsMetaGroup
service.systemComponent.register(ChannelSetsMetaGroup)
from .meta_groups.guides import GuidesMetaGroup
service.systemComponent.register(GuidesMetaGroup)
from .meta_groups.plugs import PlugsMetaGroup
service.systemComponent.register(PlugsMetaGroup)
from .meta_groups.sockets import SocketsMetaGroup
service.systemComponent.register(SocketsMetaGroup)
from .meta_groups.bind_meshes import BindMeshesMetaGroup
service.systemComponent.register(BindMeshesMetaGroup)
from .meta_groups.rigid_meshes import RigidMeshesMetaGroup
service.systemComponent.register(RigidMeshesMetaGroup)
from .meta_groups.bind_proxies import BindProxiesMetaGroup
service.systemComponent.register(BindProxiesMetaGroup)
from .decorator import DecoratorMG
service.systemComponent.register(DecoratorMG)

# Element sets
from .element_sets.controllers import ControllersElementSet
service.systemComponent.register(ControllersElementSet)
from .element_sets.controllers import ControllersFromSetElementSet
service.systemComponent.register(ControllersFromSetElementSet)
from .element_sets.bindskel import BindSkeletonElementSet
service.systemComponent.register(BindSkeletonElementSet)
from .element_sets.guides import GuidesElementSet
service.systemComponent.register(GuidesElementSet)
from .element_sets.guides import ControllerGuidesElementSet
service.systemComponent.register(ControllerGuidesElementSet)
from .element_sets.guides import EditableControllerGuidesElementSet
service.systemComponent.register(EditableControllerGuidesElementSet)
from .element_sets.assembly import PlugsElementSet
service.systemComponent.register(PlugsElementSet)
from .element_sets.assembly import SocketsElementSet
service.systemComponent.register(SocketsElementSet)
from .element_sets.attach import RigidMeshesElementSet
service.systemComponent.register(RigidMeshesElementSet)
from .element_sets.attach import ResolutionRigidMeshesElementSet
service.systemComponent.register(ResolutionRigidMeshesElementSet)
from .element_sets.attach import BindProxiesElementSet
service.systemComponent.register(BindProxiesElementSet)
from .element_sets.attach import ResolutionBindProxiesElementSet
service.systemComponent.register(ResolutionBindProxiesElementSet)
from .element_sets.meshes import BindMeshesElementSet
service.systemComponent.register(BindMeshesElementSet)
from .element_sets.meshes import ResolutionBindMeshesElementSet
service.systemComponent.register(ResolutionBindMeshesElementSet)
from .decorator import DecoratorsElementSet
service.systemComponent.register(DecoratorsElementSet)

# Color schemes
from .color_schemes.red_blue import RedBlueColorScheme
service.systemComponent.register(RedBlueColorScheme)
from .color_schemes.red_blue import RedBlueDarkerColorScheme
service.systemComponent.register(RedBlueDarkerColorScheme)
from .color_schemes.red_blue import RedBlueVividColorScheme
service.systemComponent.register(RedBlueVividColorScheme)
from .color_schemes.red_green import RedGreenColorScheme
service.systemComponent.register(RedGreenColorScheme)
from .color_schemes.red_green import RedGreenDarkerColorScheme
service.systemComponent.register(RedGreenDarkerColorScheme)
from .color_schemes.mono_yellow import MonoYellowColorScheme
service.systemComponent.register(MonoYellowColorScheme)

# Transform link setups
from .xfrm_link_setups.dyna_parent import DynaParentTransformLinkSetup
service.systemComponent.register(DynaParentTransformLinkSetup)
from .xfrm_link_setups.dyna_parent import DynaParentNoScaleTransformLinkSetup
service.systemComponent.register(DynaParentNoScaleTransformLinkSetup)
from .xfrm_link_setups.static import StaticTransformLinkSetup
service.systemComponent.register(StaticTransformLinkSetup)
from .xfrm_link_setups.world_xfrm_permanent import WorldTransformPermanentLinkSetup
service.systemComponent.register(WorldTransformPermanentLinkSetup)

# Presets
from .preset_anim import ActionPreset
service.systemComponent.register(ActionPreset)
from .preset_anim import PosePreset
service.systemComponent.register(PosePreset)
from .preset_guide import GuidePreset
service.systemComponent.register(GuidePreset)
from .preset_shapes import ShapesPreset
service.systemComponent.register(ShapesPreset)
from .preset_skeleton_bake import SkeletonBakePreset
service.systemComponent.register(SkeletonBakePreset)

# Game Export
from .game_export import NotifierGameExport
service.systemComponent.register(NotifierGameExport)
from .game_export_unreal import UnrealExportSet
service.systemComponent.register(UnrealExportSet)
from .game_export_unity import UnityExportSet
service.systemComponent.register(UnityExportSet)

# Temporary folder
from .temp_folder import TemporaryFolderSetup
service.systemComponent.register(TemporaryFolderSetup)
from .temp_folder import TemporaryFolder
service.systemComponent.register(TemporaryFolder)

# Rig
from .rig import Rig
from .rig_size_op import RigSizeOperator

# Preset Thumbnails
from .preset_thumbs.rig import RigPresetThumbnail
service.systemComponent.register(RigPresetThumbnail)
from .preset_thumbs.module import ModulePresetThumbnail
service.systemComponent.register(ModulePresetThumbnail)
from .preset_anim import PosePresetThumbnail
service.systemComponent.register(PosePresetThumbnail)
from .preset_anim import ActionPresetThumbnail
service.systemComponent.register(ActionPresetThumbnail)
from .preset_guide import GuidePresetThumbnail
service.systemComponent.register(GuidePresetThumbnail)
from .preset_shapes import ShapesPresetThumbnail
service.systemComponent.register(ShapesPresetThumbnail)

log.out('%d system components registered.' % service.systemComponent.componentCount)
log.out('%d events registered.' % service.events.eventsCount)
log.out('%d event handlers registered.' % service.events.handlersCount)
log.out('Initialization completed in %f s.' % (time.time() - initTime))
log.stopChildEntries()