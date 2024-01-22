

import lx
import lxu
import modo

import rs


class RSCmdItemFeatureFilter(rs.Command):
    """ Command used as a filter for item feature property form.
    
    Enable method needs to return True when the form should not be filtered.
    NOTE: Consider writing filter in C++ for performance reasons.
    
    Arguments
    ---------
    ident : string
        Ident(s) of features that the filter will test against.
        Multiple idents can be passed by separating them with ';'.
    """

    ARG_IDENT = 'ident'

    def arguments(self):
        ident = rs.cmd.Argument(self.ARG_IDENT, 'string')
        ident.defaultValue = ''
        return [ident]

    def enable(self, msg):
        """ If at least one selected item has a feature then it's ok.
        
        Note that we also do a check that is for rig properties in general.
        This is because of bug in forms, this filter will be tested
        even if rig properties should not be visible at all.
        Item feature properties are part of rig properties so whenever rig
        properties should not be visible item feature properties won't be
        visible either.
        """
        selectionRaw = lxu.select.ItemSelection().current()
        
        # This is needed because of a bug in forms.
        if not self._testRigPropertiesEnable(selectionRaw):
            return False

        ident = self.getArgumentValue(self.ARG_IDENT)
        if not ident:
            return False

        idents = ident.split(';')
        for ident in idents:
            try:
                featureClass = rs.service.systemComponent.get(rs.c.SystemComponentType.ITEM_FEATURE, ident)
            except LookupError:
                return False
    
            for rawItem in selectionRaw:
                if featureClass.isAddedToItemFast(rawItem):
                    return True

        return False

    def notifiers(self):
        notifiers = []
        notifiers.append(('select.event', 'item +dt'))
        notifiers.append((rs.c.Notifier.ITEM_FEATURES_ADDREM, '+d'))
        return notifiers

    # -------- Private methods

    def _testRigPropertiesEnable(self, selection):
        rigPropertiesVisible = False
        for item in selection:
            if item.PackageTest('rs.pkg.generic'):
                rigPropertiesVisible = True
                break
        
        return rigPropertiesVisible

rs.cmd.bless(RSCmdItemFeatureFilter, 'rs.filter.itemFeature')
