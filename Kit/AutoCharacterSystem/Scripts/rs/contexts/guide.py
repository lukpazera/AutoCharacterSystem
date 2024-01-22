

import lx
import modox

import rs.context
from ..util import run
from ..const import ElementSetType as e
from ..const import ItemVisible as v
from ..const import TriState as t
from ..const import Context as cxt
from ..const import GuideSubcontexts as sub
from ..scene import Scene
from ..guide import Guide

class ContextGuide(rs.context.Context):
    
    descIdentifier = cxt.GUIDE
    descUsername = 'Guide'
    descSubcontexts = [sub.EDIT, sub.GENERAL]
    descDefaultSubcontext = sub.EDIT
    descDisableMessageKey = 'cxtGuide'

    setup = True
    edit = True
    isHierarchyVisible = False

    elementsVisible = {e.EDITABLE_CONTROLLER_GUIDES: True,
                       e.RESOLUTION_BIND_MESHES: True,
                       e.RESOLUTION_RIGID_MESHES: True,
                       e.RESOLUTION_BIND_PROXIES: True}

    elementsSelectable = {e.RESOLUTION_BIND_MESHES: t.OFF,
                          e.RESOLUTION_RIGID_MESHES: t.OFF,
                          e.RESOLUTION_BIND_PROXIES: t.OFF}

    @property
    def enable(self):
        rootItem = Scene.getEditRigRootItemFast()
        if rootItem is None:
            return False
        return Guide.isEditableFast(rootItem)

    def onSet(self):
        run('!view3d.overlay true')
    
    def onLeave(self):
        """ Make sure to disable child compensation on all tools.
        """
        # Make sure to switch to item mode first.
        # Changing transform tools attributes will fail otherwise.
        run('select.type item')

        xfrm = modox.TransformToolsUtils()
        
        xfrm.moveItem = True
        xfrm.childCompensation = False
        
        xfrm.rotateItem = True
        xfrm.childCompensation = False
        
        xfrm.scaleItem = True
        xfrm.childCompensation = False
        
        xfrm.transformItem = True
        xfrm.childCompensation = False
        
        xfrm.drop()