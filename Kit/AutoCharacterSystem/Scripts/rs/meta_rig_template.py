
""" Meta Rig template interface.
"""


from .const import MetaGroupType as m


class MetaRigTemplate(object):

    @property
    def layout(self):
        """ Returns a list of group names forming the template.
        
        A leading space characters can be used to indicate hierarchy setup.
        
        Returns
        -------
        list : str
        """
        return ['root',
                ' actor',
                '  ' + m.BIND_MESHES,
                '  ' + m.BIND_PROXIES,
                '  ' + m.RIGID_MESHES,
                ' ctrls',
                ' bindloc',
                ' ' + m.PLUGS,
                ' ' + m.SOCKETS,
                ' ' + m.DECORATORS,
                ' lchans',
                ' ' + m.GUIDES,
                ' ' + m.CHANNEL_SETS]

