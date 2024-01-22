

import lx
import lxu
import modo
import modox

import rs


class CmdBindFromMap(rs.RigCommand):
    """ Binds mesh to rig using map stored on the mesh itself.
    """
    
    def enable(self, msg):
        return True

    def setup(self):
        return True

    def restoreItemSelection(self):
        return True

    def execute(self, msg, flags):
        mesh = self._mesh
        if mesh is None:
            return
        
        rig = self.firstRigToEdit
        bind = rs.Bind(rig)
        bind.fromMap(mesh)

        rs.Scene().contexts.refreshCurrent()

        # This is causing crashes in Mutog scene for some reason.
        # Can't close the layout automatically for now.
        # self._closeLayout()

    # -------- Private methods

    def _closeLayout(self):
        layoutName = "rs_BindMap"
        cmd = 'layout.createOrClose {rsBindMap} {%s} open:false {Bind Map}'
        lx.eval(cmd % (layoutName))

    @property
    def _mesh(self):
        """
        
        Returns
        -------
        BindMeshItem
        """
        for mesh in modo.Scene().selectedByType('mesh'):
            try:
                bmesh = rs.BindMeshItem(mesh)
            except TypeError:
                continue
            if not bmesh.isBound:
                return bmesh
        return None

rs.cmd.bless(CmdBindFromMap, 'rs.bind.fromMap')