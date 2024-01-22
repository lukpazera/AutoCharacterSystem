

import lx
import lxu
import modo

import rs


class CmdSetGuidePopup(rs.base_OnItemFeatureCommand):
    """ Sets or queries guide for an item.
    
    The guide is set via a popup so this command is suitable
    for putting it into UI but not for using it from scripts.
    """

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.GuideItemFeature
    
    ARG_INDEX = 'popupIndex'
    
    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
                
        index = rs.cmd.Argument(self.ARG_INDEX, 'integer')
        index.flags = 'query'
        index.valuesList = self._buildPopup
        index.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        return [index] + superArgs

    def enable(self, msg):
        return self.itemFeatureToQuery is not None

    def execute(self, msg, flags):
        index = self.getArgumentValue(self.ARG_INDEX)

        featuresToEdit = self.itemFeaturesToEdit
        if not featuresToEdit:
            return

        if index == 0:
            guideToConnectTo = None
        else:
            guides = self.itemFeatureToQuery.availableGuides
            guideToConnectTo = guides[index - 1] # -1 to compensate for None option.

        for guideFeature in featuresToEdit:
            guideFeature.guide = guideToConnectTo

    def query(self, argument):
        if argument == self.ARG_INDEX:
            guideFeature = self.itemFeatureToQuery
            if guideFeature is None:
                return 0
            guide = guideFeature.guide
            if guide is None:
                return 0
            
            index = -1
            for n, guideItem in enumerate(guideFeature.availableGuides):
                if guideItem == guide:
                    index = n
                    break
            
            if index >= 0:
                return index + 1 # account for the (none) option
            
            return 0

    # -------- Private methods

    def _buildPopup(self):
        """ Builds a popup that the command will present in UI.
        """
        entries = [('none', '(none)')]
        feature = self.itemFeatureToQuery
        if feature is not None:
            guides = feature.availableGuides
            for guide in guides:
                entries.append((guide.modoItem.id, guide.nameAndSide))
        return entries

rs.cmd.bless(CmdSetGuidePopup, 'rs.item.setGuideFromPopup')