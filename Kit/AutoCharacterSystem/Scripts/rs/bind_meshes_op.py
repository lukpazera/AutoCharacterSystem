
import lx
import modo
import modox

from .component_op import ComponentOperator
from .items.bind_mesh import BindMeshItem
from .attach_item import AttachItem
from .item import Item
from .bind_meshes import BindMeshes
from .resolutions import Resolutions
from .deform_stack import DeformStack
from .item_utils import ItemUtils
from . import const as c
from .util import run


class BindMeshesOperator(ComponentOperator):
    """ Represents bind meshes in the scene.
    """

    descComponentClass = BindMeshes

    # -------- Public interface
    
    def assign(self, modoItems, addToCurrentResolution=True):
        """ Assigns new bind mesh(es).
        
        This doesn't bind the mesh yet, just puts it on the list of meshes that
        will be bound at some point.
        """
        # TODO:This method should check if the item is valid bind mesh.
        # Freeze transforms, etc.
        
        if type(modoItems) not in (list, tuple):
            modoItems = [modoItems]
        
        # Convert mesh items to rig items of bind mesh type.
        meshes = []
        meshModoItems = []
        for modoItem in modoItems:
            try:
                mesh = BindMeshItem.newFromExistingItem(modoItem)
            except TypeError:
                continue
            meshes.append(mesh)
            meshModoItems.append(modoItem)

        self.component.setup.addItem(meshModoItems)

        if addToCurrentResolution:
            resolutions = Resolutions(self.component.rigRootItem)
            currentResolution = resolutions.currentResolution

            for mesh in meshes:
                if currentResolution:
                    mesh.addToResolution(currentResolution)
                
    def unassign(self, items):
        """ Unassigns mesh from the rig.
        
        Parameters
        ----------
        modoItems : list of modo.Item, list of BindMeshItem
        """
        if self.component is None:
            return
        
        if type(items) not in (list, tuple):
            items = [items]
        
        for modoItem in items:
            try:
                bmesh = Item.getFromOther(modoItem)
            except TypeError:
                continue
            if bmesh.type != c.RigItemType.BIND_MESH:
                continue
            # TODO: Needs to make sure features are gone as well.
            bmesh.standardise()
        
        modoItems = [item.modoItem for item in items]
        self.component.setup.removeItem(modoItems)

    def unassignAll(self):
        pass

    def addEmptyBindMesh(self, name):
        """
        Adds empty bind mesh to the rig.

        Returns
        -------
        BindMeshItem
        """
        meshItem = modo.Scene().addItem(modo.c.MESH_TYPE, name=name)
        self.assign(meshItem, addToCurrentResolution=True)
        return BindMeshItem(meshItem)

    def mergeRigidOrProxyMesh(self, rigidMeshOrProxy, bindMesh):
        """
        Merges given rigid mesh with the bind mesh.

        Rigid mesh contents are copied over to the bind mesh,
        a weight map is set up so rigid mesh can be deformed to move in the exact
        same way as when it was attached to bind skeleton.

        If rigid mesh is attached to a bind locator that doesn't have
        general influence set up - a general influence is set up manually
        and the bind mesh is connected to it.

        Parameters
        ----------
        rigidMeshOrProxy : RigidMeshItem, BindProxyItem

        bindMesh : BindMeshItem
        """
        # Get bind locator rigid mesh is attached to
        attachItem = AttachItem(rigidMeshOrProxy)
        bindLocator = attachItem.attachedToBindLocator

        if bindLocator is None:
            return False

        # We need to make sure the bind locator does affect the bind mesh.
        # If it doesn't the merged rigid mesh won't work.
        # To make it work we have to connect bind locator (and its deformer)
        # to the bind mesh manually.

        # If bind locator doesn't drive any deformers
        # we need to add general influence that will be driven by the bind locator.
        if not bindLocator.isEffector:
            genInf = self._addGeneralInfluence(bindLocator)
        else:
            genInf = bindLocator.normalizedGeneralInfluence
            # We need to reset settings if general influence is there but is not
            # influencing any meshes.
            # If we don't do it and general influence has weight map name set
            # to bad value (pointing to wrong map) this weight map name will be
            # picked up and it's possible that the mesh will be merged using
            # wrong weight map.
            genInf.resetSettingsIfNotDeforming()

        # We set the deform connection between general influence and bind mesh.
        # This is only really needed for a situation when bind mesh does not have
        # binding between itself and general influence already but we just do this
        # connecting always. If connection is already there nothing will simply happen.
        genInf.meshes = bindMesh.modoItem

        # Get weightmap name or create new weight map name
        # and make sure the general influence is set to this weight map and
        # weight map influence type.
        weightMapName = bindLocator.weightMapName
        if not weightMapName:
            weightMapName = bindLocator.modoItem.name
            genInf.influenceType = modox.GeneralInfluenceType.WEIGHT_MAP
            genInf.mapName = weightMapName

        # Create new weight map on the rigid mesh
        itemSelection = modox.ItemSelection()
        itemSelection.set(rigidMeshOrProxy.modoItem, modox.SelectionMode.REPLACE)
        run('vertMap.new {%s} wght init:true value:1.0' % weightMapName)

        # Copy / Paste geo
        run('select.type polygon')
        run('select.drop polygon')
        run('copy')

        itemSelection.set(bindMesh.modoItem, modox.SelectionMode.REPLACE)
        run('select.type polygon')
        run('paste')
        run('select.drop polygon')
        run('!select.type item')

    # -------- Private methods

    def _addGeneralInfluence(self, bindLocator):
        """
        Utility function that adds new general influence for a bind locator
        that is not effector yet and sets it up in deformers stack.
        """
        scene = modo.Scene()
        genInf = scene.addItem(modo.c.GENINFLUENCE_TYPE, bindLocator.nameAndSide + " (GenInf)")

        # Set up bind locator as an effector for new deformer.
        effector = modox.Effector(bindLocator.modoItem)
        effector.setDeformers(genInf, replace=False)

        # Put general influence into ACS rig normalizing folder.
        normFolder = DeformStack(self._rigRootItem).normalizingFolder
        stdNormFolder = modox.NormalizingFolder(normFolder.modoItem)
        stdNormFolder.addDeformers(genInf)

        return modox.GeneralInfluence(genInf)