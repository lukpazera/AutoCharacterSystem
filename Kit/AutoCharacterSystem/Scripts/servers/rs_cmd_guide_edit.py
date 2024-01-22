
import lx
import lxu
import modo
import modox

import rs


class CmdGuideSelectRoots(rs.RigCommand):
    """ Selects root of selected guide modules.
    """

    def execute(self, msg, flags):
        itemSelection = modox.ItemSelection().getRaw()
        modules = rs.SelectionUtils.getModulesFromItems(itemSelection)

        if not modules:
            modules = self.firstRigToEdit.modules.allModules

        roots = []
        for mod in modules:
            modGuide = rs.ModuleGuide(mod)

            rootCtrlGuideFeatures = modGuide.rootControllerGuides

            guideModoItems = [feature.modoItem for feature in rootCtrlGuideFeatures]
            roots.extend(guideModoItems)

        modo.Scene().select(roots, add=False)
        
rs.cmd.bless(CmdGuideSelectRoots, 'rs.guide.selectRoots')


class CmdGuideSnapToGround(rs.RigCommand):
    """ Snaps module to ground.
    """

    def applyEditActionPre(self):
        """ This command has to apply edit action because it does
        operations on the setup action directly. If there's stuff
        on edit action when this command is executed it'll 'cover'
        the setup action edits.
        """
        return True
    
    def execute(self, msg, flags):
        editRig = self.firstRigToEdit

        itemSelection = modox.ItemSelection().getRaw()
        modules = rs.SelectionUtils.getModulesFromItems(itemSelection)

        if not modules:
            modules = None # This will force snapping entire rig to ground

        rs.Guide(editRig).snapToGround(modules)

rs.cmd.bless(CmdGuideSnapToGround, 'rs.guide.snapToGround')


class CmdGuideFitToGround(rs.RigCommand):
    """ Resizes module such that it fits to the ground.
    """

    def applyEditActionPre(self):
        """ This command has to apply edit action because it does
        operations on the setup action directly. If there's stuff
        on edit action when this command is executed it'll 'cover'
        the setup action edits.
        """
        return True

    def execute(self, msg, flags):
        editRig = self.firstRigToEdit
        editModule = editRig.modules.editModule
        modGuide = rs.ModuleGuide(editModule)
        modGuide.setToPositionAndFitToGround()

rs.cmd.bless(CmdGuideFitToGround, 'rs.guide.fitToGround')