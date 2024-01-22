

import lx
import lxu
import modo
import modox

import rs


class CmdGenericItemFilter (lxu.command.BasicCommand):
    """ This command is used as a filter command for a form.
    When this command's enable state returns true the form 
    will be visible. It'll be hidden otherwise.
    
    More information here:
    http://modo.sdk.thefoundry.co.uk/wiki/Form_Filtering
    
    This is the atom that the form needs to have to use this
    command as filter:
    <atom type="FilterCommand">rs.filter.genericItem</atom>
    
    Generic item filter checks if an item has generic rig item package added.
    If there's no generic package present
    form using this filter should not be visible.
    """

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

    def basic_Enable (self, msg):
        for item in modox.ItemSelection().getRaw():
            if item.PackageTest('rs.pkg.generic'):
                return True
        return False

lx.bless(CmdGenericItemFilter, 'rs.filter.genericItem')