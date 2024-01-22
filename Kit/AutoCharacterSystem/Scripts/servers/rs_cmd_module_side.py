

import lx
import lxu
import modo
import modox

import rs


class CmdModuleSide(rs.base_OnModuleCommand):
    """ Query or set module side.
    
    This command presents a popup with side choices.
    Therefore the argument is an integer (in range from 0 to n)
    and then it has popup as a hint that is using internal and user strings.
    
    Query needs to read side setting from module and
    map it to integer that is an index in the popup.
    
    Execute needs to take integer value and map it to the proper
    side value.
    
    TODO: The popup is not dynamic so not sure if current mechanism
    is the right one. If there's a way to define static popup
    that should be used instead.
    """

    ARG_SIDE = 'side'
    ARG_APPLY_GUIDE = 'applyGuide'

    POPUP_INDEX_TO_SIDE = {0: rs.c.Side.CENTER,
                           1: rs.c.Side.LEFT,
                           2: rs.c.Side.RIGHT}
    SIDE_TO_POPUP_INDEX = {rs.c.Side.CENTER: 0,
                           rs.c.Side.LEFT: 1,
                           rs.c.Side.RIGHT: 2}
    POPUP_ITEMS = [('center', 'Center'),
                   ('left', 'Left'),
                   ('right', 'Right')]

    def arguments(self):
        superArgs = rs.base_OnModuleCommand.arguments(self)
                
        argSide = rs.cmd.Argument(self.ARG_SIDE, 'integer')
        argSide.flags = 'query'
        argSide.valuesList = self.POPUP_ITEMS
        argSide.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        argApplyGuide = rs.cmd.Argument(self.ARG_APPLY_GUIDE, 'boolean')
        argApplyGuide.flags = 'optional'
        argApplyGuide.defaultValue = True

        return [argSide, argApplyGuide] + superArgs
    
    def applyEditActionPre(self):
        return True
    
    def applyEditActionPost(self):
        return True

    def execute(self, msg, flags):
        moduleSide = self.getArgumentValue(self.ARG_SIDE)

        try:
            moduleSide = self.POPUP_INDEX_TO_SIDE[moduleSide]
        except KeyError:
            return

        updateGuide = False
        allModules = self.modulesToEdit

        for mod in self.modulesToEdit:
            allModules.extend(mod.submodules)

        for mod in allModules:
            # Don't do anything if the side hasn't changed.
            previousSide = mod.side
            if previousSide == moduleSide:
                continue
            
            mod.side = moduleSide
            modFirstSide = mod.firstSide

            # Mirroring doesn't need to be done if we module's first side is center.
            # With first side to be center we never mirror module as it doesn't have a concept of side.
            if modFirstSide == rs.c.Side.CENTER:
                continue

            # If first side is not center we only skip mirroring if we switch
            # - from first side to center
            # - from center to first side.
            # We have to do mirroring in other cases.
            if previousSide == modFirstSide and moduleSide == rs.c.Side.CENTER:
                continue
            if previousSide == rs.c.Side.CENTER and moduleSide == modFirstSide:
                continue

            # Flip guide and reapply it only if we go from one side to another.
            # Going from lef/right to center or vice versa should not do mirror.
            sides = [rs.c.Side.LEFT, rs.c.Side.RIGHT]
            if previousSide in sides and moduleSide in sides:
                guideXfrms = rs.GuideTransforms()
                guideXfrms.setGuides(mod[rs.c.ElementSetType.GUIDES])
                guideXfrms.mirrorTransforms()

            # Mirror values on channels that developer marked within the module assemblies.
            mod.mirrorKeyChannels()

            updateGuide = True

        # TODO: This assumes that only edit rig modules changed side.
        # This is potential hole.
        if updateGuide and self.getArgumentValue(self.ARG_APPLY_GUIDE):
            lx.eval('!rs.guide.apply')

    def query(self, argument):
        if argument == self.ARG_SIDE:
            module = self.moduleToQuery
            if module:
                sideName = module.side
                if sideName:
                    return self.SIDE_TO_POPUP_INDEX[sideName]
        return None

    def notifiers(self):
        notifiers = rs.Command.notifiers(self)
        notifiers.append(('select.event', 'item element+v'))
        return notifiers

rs.cmd.bless(CmdModuleSide, 'rs.module.side')