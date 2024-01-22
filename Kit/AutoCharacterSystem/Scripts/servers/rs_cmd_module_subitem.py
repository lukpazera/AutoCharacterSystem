

import lx
import lxu
import modo
import modox

import rs


class CmdNewModuleSubitem(rs.Command):
    """ Adds new sub item to module.
    
    This is really for adding special assemblies and groups.
    It doesn't really check if we're inside module in schematic either.
    So just know what you do...
    """

    ARG_IDENT = 'ident'
    ARG_FROM_ASSEMBLY = 'fromAssm'
    ARG_ASSEMBLY = 'assm'
    
    def arguments(self):
        ident = rs.cmd.Argument(self.ARG_IDENT, 'string')
        ident.flags = "optional"
        ident.defaultValue = ""
        
        fromAssm = rs.cmd.Argument(self.ARG_FROM_ASSEMBLY, 'boolean')
        fromAssm.flags = ['optional', 'hidden']
        fromAssm.defaultValue = False
        
        assm = rs.cmd.Argument(self.ARG_ASSEMBLY, '&item')
        assm.flags = ['optional', 'hidden']
        assm.defaultValue = None
        
        return [ident, fromAssm, assm]
    
    def execute(self, msg, flags):
        ident = self.getArgumentValue(self.ARG_IDENT)
        assm = self.getArgumentValue(self.ARG_ASSEMBLY)
            
        try:
            itemClass = rs.service.systemComponent.get(rs.c.SystemComponentType.ITEM, ident)
        except LookupError:
            return
        
        newItem = itemClass.new()
        parentGroup = None
        if assm is None:
            rs.run('schematic.addItem item:{%s} mods:false' % newItem.modoItem.id)
    
            # Schematic link is established but now we need to see to which group
            # and parent to this group as well.
            try:
                parentGroup = newItem.modoItem.connectedGroups[0]
            except IndexError:
                pass
        else:
            try:
                assm = modo.Item(modox.SceneUtils.findItemFast(assm))
            except LookupError:
                return # Should return failed code really.
            rs.run('schematic.addItem item:{%s} group:{%s} mods:false' % (newItem.modoItem.id, assm.id))
            parentGroup = assm
            
        newItem.modoItem.setParent(parentGroup)
        
        # Now that the added item has rig context we can render its name.
        newItem.renderAndSetName()
        
    # -------- Private methods
    
    # THIS CODE IS UNUSED FOR THE TIME BEING
    @property
    def _assembly(self):
        if not self.getArgumentValue(self.ARG_FROM_ASSEMBLY):
            return None

        scene = modo.Scene()

        if self.isArgumentSet(self.ARG_ASSEMBLY):
            assmid = self.getArgumentValue(self.ARG_ASSEMBLY)
            try:
                return scene.item(assmid)
            except LookupError:
                return None
        else:
            for item in scene.selected:
                if item.type == 'assembly':
                    return item
        return None

rs.cmd.bless(CmdNewModuleSubitem, 'rs.module.newSubitem')

