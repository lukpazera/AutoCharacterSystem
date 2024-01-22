

import lx
import lxu
import modo

import rs


class CmdGuideZeroTransforms(rs.base_OnItemFeatureCommand):
    """ Sets zero transforms property of the guide item feature.
    """

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.GuideItemFeature
    
    ARG_STATE = 'state'

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
        
        state = rs.cmd.Argument(self.ARG_STATE, 'boolean')
        state.flags = 'query'
        state.defaultValue = False

        return [state] + superArgs

    def uiHints(self, argument, hints):
        if argument == self.ARG_STATE:
            hints.BooleanStyle(lx.symbol.iBOOLEANSTYLE_BUTTON)

    def restoreItemSelection(self):
        return True

    def setupMode(self):
        return True

    def enable(self, msg):
        return self.itemFeatureToQuery is not None

    def execute(self, msg, flags):
        state = self.getArgumentValue(self.ARG_STATE)

        for feature in self.itemFeaturesToEdit:
            feature.zeroTransforms = state

    def query(self, argument):
        if argument == self.ARG_STATE:
            guideFeature = self.itemFeatureToQuery
            if guideFeature is not None:
                return guideFeature.zeroTransforms
            return False

rs.cmd.bless(CmdGuideZeroTransforms, 'rs.item.guideZeroTransforms')