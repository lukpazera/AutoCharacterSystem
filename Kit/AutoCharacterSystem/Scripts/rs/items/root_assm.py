
""" Core rig assembly item module.

    Core assembly contains all items in the rig.
"""


import lx

import rs.item


class RootAssembly(rs.item.Item):
    
    descType = 'rootassm'
    descUsername = 'Root Assembly Item'
    descModoItemType = 'group'
    descModoItemSubtype = 'assembly'
    descDefaultName = 'Main'
    descPackages = []

    def onAdd(self, subtype):
        lx.eval('select.item {%s} set' % self.modoItem.id)
        lx.eval('item.editorColor white')
