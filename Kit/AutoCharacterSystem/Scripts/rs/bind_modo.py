

import lx
import modo
import modox

from . import const as c


class ModoBind(object):
    """ Deals with default modo binding setup.
    
    This class works off bind skeleton shadow as default bind setup
    should only be ran over the bind skeleton shadow.
    """

    @property
    def shadowSkeleton(self):
        return self._bindSkelShadow
        
    def delete(self):
        """ Modo bind setup deletes itself.
        
        We go through all the general influences and delete them
        as well as any parent deform groups that might be in.
        """
        skeleton = self._bindSkelShadow.skeleton
        for locShadow in skeleton:
            eff = modox.Effector(locShadow.modoItem)
            genInfItems = eff.generalInfluences
            for infItem in genInfItems:
                influence = modox.GeneralInfluence(infItem)
                parentFolder = influence.parentFolder
                if parentFolder:
                    lx.eval('!item.delete child:0 item:{%s}' % parentFolder.id)
                lx.eval('item.delete child:0 item:{%s}' % infItem.id)

    # -------- Private methods
        
    def __init__(self, bindSkelShadow):
        self._bindSkelShadow = bindSkelShadow