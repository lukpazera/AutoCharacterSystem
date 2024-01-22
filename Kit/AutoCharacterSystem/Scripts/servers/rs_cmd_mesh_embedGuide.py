

import lx
import lxu
import modo
import modox

import rs


class CmdGuideEmbedInMesh(rs.Command):

    def setupMode(self):
        return True

    def enable(self, msg):
        return True

    def execute(self, msg, flags):
        scene = modo.Scene()
        try:
            mesh = scene.selectedByType('mesh')[0]
        except IndexError:
            return

        rscene = rs.Scene()
        editRig = rscene.editRig
        if editRig is None:
            return
        guide = rs.Guide(editRig)
        guide.embedInMesh(mesh)

rs.cmd.bless(CmdGuideEmbedInMesh, 'rs.guide.embedInMesh')


class CmdSetGuideFromMesh(rs.Command):

    def setupMode(self):
        return True

    def restoreItemSelection(self):
        return True

    def enable(self, msg):
        return True

    def execute(self, msg, flags):
        scene = modo.Scene()
        try:
            mesh = scene.selectedByType('mesh')[0]
        except IndexError:
            return

        rscene = rs.Scene()
        editRig = rscene.editRig
        if editRig is None:
            return
        guide = rs.Guide(editRig)
        guide.setFromMesh(mesh)

rs.cmd.bless(CmdSetGuideFromMesh, 'rs.guide.setFromMesh')