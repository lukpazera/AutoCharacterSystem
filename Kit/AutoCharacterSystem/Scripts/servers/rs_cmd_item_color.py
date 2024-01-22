

import lx
import lxu
import modo

import rs


class CmdItemColorPopup(rs.base_OnItemFeatureCommand):
    """ Sets/queries color for an item using a popup.
    
    This command is suitable for using in UI.
    """

    # This is for base_OnItemFeatureCommand interface
    descIFClassOrIdentifier = rs.ItemColor
    
    ARG_LIST = 'list'

    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
        
        listArg = rs.cmd.Argument(self.ARG_LIST, 'integer')
        listArg.flags = 'query'
        listArg.valuesList = self._buildPopup
        listArg.valuesListUIType = rs.cmd.ArgumentValuesListType.POPUP

        return [listArg] + superArgs

    def query(self, argument):
        if argument == self.ARG_LIST:
            colorFeature = self.itemFeatureToQuery
            if colorFeature is None:
                return 0
            chosenColorIdent = colorFeature.colorIdentifier
            
            if not chosenColorIdent:
                return 0 # This is None

            # We need to reach out to rig to get the color scheme.
            rigRoot = colorFeature.item.rigRootItem
            colorScheme = rigRoot.colorScheme

            # We then iterate through rig color scheme colors
            # and look for one that is set in color feature properties
            # on a chosen item
            for n, colorObject in enumerate(colorScheme.colors):
                if colorObject == chosenColorIdent:
                    return n + 1 # This is because of the first none entry

            return 0

    def execute(self, msg, flags):
        identIndex = self.getArgumentValue(self.ARG_LIST)
        
        colorFeatures = self.itemFeaturesToEdit

        if identIndex < 0:
            return

        if identIndex == 0: # none option
            for colorFeature in colorFeatures:
                colorFeature.color = None
            return

        identIndex -= 1 # account for the none option
        
        # Convert index to identifier.
        # Using index is not safe if items from multiple rigs and color schemes
        # are going to be processed.        
        queryFeature = self.itemFeatureToQuery
        rigRoot = queryFeature.item.rigRootItem
        colorScheme = rigRoot.colorScheme
        
        try:
            color = colorScheme.getColorByIndex(identIndex)
        except IndexError:
            return
        colorId = color.identifier
        
        for colorFeature in colorFeatures:
            colorFeature.color = colorId

    # -------- Private methods

    def _buildPopup(self):
        content = rs.cmd.ArgumentPopupContent()
        content.iconWidth = rs.base_ColorScheme.Icon.COLOR_WIDTH
        content.iconHeight = rs.base_ColorScheme.Icon.COLOR_HEIGHT

        noneEntry = rs.cmd.ArgumentPopupEntry("$none$", "(none)")
        content.addEntry(noneEntry)

        colorFeature = self.itemFeatureToQuery
        if colorFeature is None:
            return []

        rigRoot = colorFeature.item.rigRootItem
        colorScheme = rigRoot.colorScheme

        for color in colorScheme.colors:
            username = color.username
            iconImage = color.iconImage

            entry = rs.cmd.ArgumentPopupEntry(color.identifier, username)
            entry.iconImage = iconImage
            content.addEntry(entry)
        return content

rs.cmd.bless(CmdItemColorPopup, 'rs.item.colorPopup')


class CmdItemColor(rs.base_OnItemFeatureCommand):
    """ Sets/queries color for a given item.
    
    This command is suitable for use from a script.
    """

    descIFClassOrIdentifier = rs.ItemColor
    
    ARG_COLOR = 'color'
    ARG_AUTO_ADD = 'autoAdd'
    
    def arguments(self):
        superArgs = rs.base_OnItemFeatureCommand.arguments(self)
        
        colorArg = rs.cmd.Argument(self.ARG_COLOR, 'string')
        colorArg.flags = 'query'
        
        autoAddArg = rs.cmd.Argument(self.ARG_AUTO_ADD, 'boolean')
        autoAddArg.flags = 'optional'
        autoAddArg.defaultValue = False
        
        return [colorArg, autoAddArg] + superArgs

    def query(self, argument):
        if argument == self.ARG_COLOR:
            colorFeature = self.itemFeatureToQuery
            if colorFeature:
                return colorFeature.colorIdentifier

    def execute(self, msg, flags):
        colorIdentifier = self.getArgumentValue(self.ARG_COLOR)

        if self.getArgumentValue(self.ARG_AUTO_ADD):
            for item in self.itemsToEdit:
                op = rs.ItemFeatures(item)
                op.addFeature(rs.c.ItemFeatureType.COLOR)

        for colorFeature in self.itemFeaturesToEdit:
            colorFeature.color = colorIdentifier

rs.cmd.bless(CmdItemColor, 'rs.item.color')
