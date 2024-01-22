
"""
Command notifier definitions.
"""


from . import const as c


class NotifierSet(object):

    EDIT_MODULE_CHANGED = [
    ('item.event', "add[%s] +t" % c.RigItemType.MODULE_ROOT),
    ('item.event', "remove[%s] +t" % c.RigItemType.MODULE_ROOT),

    ('item.event', "name[%s] +t" % c.RigItemType.MODULE_ROOT),

    ('graphs.event', '%s +t' % c.Graph.EDIT_MODULE),
    ('graphs.event', '%s +t' % c.Graph.EDIT_RIG),

    ('select.event', 'cinema +dt')]
