

import lx
import lxu
import modo

import rs


class CmdEmbedGuideAlignSourcePopup(rs.Command):
    """ Sets or queries guide which orientation will be source of alignment for embedding another guide in mesh.
    
    The guide is set via a popup so this command is suitable
    for putting it into UI but not for using it from scripts.
    """

    ARG_INDEX = 'popupIndex'
    
    def arguments(self):
        index = rs.cmd.Argument(self.ARG_INDEX, 'integer')
        index.flags = 'query'
        index.valuesList = self._buildPopup
        index.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        return [index]

    def enable(self, msg):
        return self._embedGuideFeatureToQuery is not None

    def execute(self, msg, flags):
        index = self.getArgumentValue(self.ARG_INDEX)

        featuresToEdit = self._guideFeaturesToEdit
        if not featuresToEdit:
            return

        if index == 0:
            guideToConnectTo = None
        else:
            guides = self._embedGuideFeatureToQuery.axesReferenceGuidesPopup
            guideToConnectTo = guides[index - 1]

        for guideFeature in featuresToEdit:
            guideFeature.axesReferenceGuide = guideToConnectTo

    def query(self, argument):
        if argument == self.ARG_INDEX:
            guideFeature = self._embedGuideFeatureToQuery
            if guideFeature is None:
                return 0
            guide = guideFeature.axesReferenceGuide
            if guide is None:
                return 0
            
            index = -1
            for n, guideItem in enumerate(guideFeature.axesReferenceGuidesPopup):
                if guideItem == guide:
                    index = n
                    break
            
            if index >= 0:
                return index + 1 # account for the (self) option
            
            return 0

    # -------- Private methods

    @property
    def _embedGuideFeatureToQuery(self):
        """ Gets feature object that will be used for querying a list of guides.

        Returns
        -------
        EmbedGuideFeature, None
        """
        for item in modo.Scene().selected:
            try:
                return rs.EmbedGuideFeature(item)
            except TypeError:
                continue
        return None

    @property
    def _guideFeaturesToEdit(self):
        """ Gets a list of feature objects for which the guide choice will be set.
        """
        guideFeatures = []
        for item in modo.Scene().selected:
            try:
                guideFeatures.append(rs.EmbedGuideFeature(item))
            except TypeError:
                continue
        return guideFeatures

    def _buildPopup(self):
        """ Builds a popup that the command will present in UI.
        """
        entries = [('self', '(self)')]
        feature = self._embedGuideFeatureToQuery
        if feature is not None:
            guides = feature.axesReferenceGuidesPopup
            for guide in guides:
                entries.append((guide.modoItem.id, guide.nameAndSide + ' (Reference)'))
        return entries

rs.cmd.bless(CmdEmbedGuideAlignSourcePopup, 'rs.guide.embedAlignSourcePopup')