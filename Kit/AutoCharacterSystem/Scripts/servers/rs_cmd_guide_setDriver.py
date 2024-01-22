

import lx
import lxu
import modo

import rs


class CmdSetGuide(rs.base_OnItemFeatureCommand):
    """ Sets or queries guide for an item.
    
    This command allows for passing guide item directly as its
    argument and therefore is suitable for use from scripts
    (not so much in UI though).
    """

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.GuideItemFeature
    
    ARG_GUIDE = 'guide'
    
    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
                
        guide = rs.cmd.Argument(self.ARG_GUIDE, '&item')
        guide.defaultValue = None

        return [guide] + superArgs

    def notifiers(self):
        """ This command doesn't need to update its disable/enable state.
        By returning empty list we clear any default notifiers.
        """
        return []

    def enable(self, msg):
        return self.itemFeatureToQuery is not None

    def execute(self, msg, flags):
        guideItemId = self.getArgumentValue(self.ARG_GUIDE)
        if not guideItemId:
            return

        try:
            guideToConnectTo = rs.GuideItem(modo.Scene().item(guideItemId))
        except (TypeError, LookupError):
            return

        for feature in self.itemFeaturesToEdit:
            feature.guide = guideToConnectTo

    def query(self, argument):
        if argument == self.ARG_GUIDE:
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

rs.cmd.bless(CmdSetGuide, 'rs.item.setGuide')