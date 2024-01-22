

import lx
import lxu
import modo

import rs


class CmdGuideSymmetricGuidePopup(rs.base_OnItemCommand):
    """ Sets or queries guide that acts as symmetryc reference for another guide.
    """

    descItemClassOrIdentifier = rs.GuideItem
    
    ARG_SYMMETRY_GUIDE_INDEX = 'index'

    def arguments(self):
        superArgs = rs.base_OnItemCommand.arguments(self)
            
        argSymGuide = rs.cmd.Argument(self.ARG_SYMMETRY_GUIDE_INDEX, 'integer')
        argSymGuide.flags = 'query'
        argSymGuide.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP
        argSymGuide.valuesList = self._buildPopup
        
        return [argSymGuide] + superArgs

    def execute(self, msg, flags):
        index = self.getArgumentValue(self.ARG_SYMMETRY_GUIDE_INDEX)

        if index == 0:
            symGuide = None
        else:
            index -= 1
            symGuidesList = self._availableSymmetryGuides
            if index >= len(symGuidesList):
                return
            symGuide = symGuidesList[index]
        
        guideToEdit = self.itemToQuery
        if guideToEdit is None:
            return

        guideToEdit.symmetricGuide = symGuide

    def query(self, argument):
        if argument == self.ARG_SYMMETRY_GUIDE_INDEX:
            guide = self.itemToQuery
            if guide is None:
                return

            currentSymGuide = guide.symmetricGuide
            if currentSymGuide is None:
                return 0

            index = -1
            for n, guideItem in enumerate(self._availableSymmetryGuides):
                if guideItem == currentSymGuide:
                    index = n
                    break
            
            if index >= 0:
                return index + 1 # account for the (none) option
            
            return 0

    # -------- Private methods

    @property
    def _availableSymmetryGuides(self):
        """ Gets a list of guide items that can be used as
        symmetry reference for a given guide.
        
        When module has center side we look for guides within the module.
        If the module has side set we look for guides in symmetric module.

        Returns
        -------
        list of GuideItem
        """
        guide = self.itemToQuery
        if guide is None:
            return []
        
        if guide.side == rs.c.Side.CENTER:
            return []

        modRoot = guide.moduleRootItem
        if modRoot is None:
            return []
               
        sideToQuery = rs.c.Side.RIGHT
        if guide.side == rs.c.Side.RIGHT:
            sideToQuery = rs.c.Side.LEFT

        symList = []
        mod = rs.Module(modRoot)
        
        if mod.side == rs.c.Side.CENTER:
            symList = self._getGuidesFromModule(mod, sideToQuery)
        else:
            # Look for guides in the symmetric module
            symModule = mod.symmetricModule
            if symModule is not None:
                symList = self._getGuidesFromModule(symModule, sideToQuery)

        return symList

    def _getGuidesFromModule(self, module, sideToQuery):
        symList = []
        modGuides = module[rs.c.ElementSetType.GUIDES]
        for g in modGuides:
            try:
                g = rs.GuideItem(g)
            except TypeError:
                continue

            if g.side == sideToQuery:
                symList.append(g)
        return symList

    def _buildPopup(self):
        """ Builds a popup that the command will present in UI.
        """
        entries = [('none', '(none)')]
        guides = self._availableSymmetryGuides
        for guide in guides:
            m = guide.moduleRootItem
            entries.append((guide.modoItem.id, guide.nameAndSide))
        return entries

rs.cmd.bless(CmdGuideSymmetricGuidePopup, 'rs.guide.symmetricGuidePopup')