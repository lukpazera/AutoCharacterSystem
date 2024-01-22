
""" Startup sequence for Rigging System.

Python codebase will be imported only when C++ servers are registered.
This is to avoid import errors that will inevitably happen if C++ servers
are not present.
"""


import sys
import os
import traceback

import lx


MAIN_PATH_ALIAS = 'kit_AutoCharacterSystem:'
MAIN_PATH = lx.eval('query platformservice alias ? "%s"' % MAIN_PATH_ALIAS)
SERVERS_PATH = os.path.join(MAIN_PATH, 'Scripts', 'servers')


class ImportPath():
    """ Context manager for altering the system path.
    
    We want to temporarily append
    and remove the temp path in every case, normal or exceptional.
    This is taken from MODO's lxserv import code.
    """
    def __init__(self, dirpath):
        self._dir = dirpath

    def __enter__(self):
        sys.path.append(self._dir)

    def __exit__(self, xt, xv, tb):
        sys.path.pop()
        return False


def test():
    """ Checks whether C++ servers are present.
    
    For simplicity it only tests against the main rig root item.
    If this item is missing we assume C++ servers are not there.
    """
    try:
        typeid = lx.service.Scene().ItemTypeLookup('rs.root')
    except LookupError:
        return False
    return True


def scanServers(path):
    """ Scans servers folder and creates the list of all servers to import.
    
    Returns
    -------
    list of str
    """
    
    if not os.path.exists(path):
        return []

    ls = []
    for filename in os.listdir(path):
        module,extension = os.path.splitext(filename)
        if extension == '.py' or extension == '.pyc' and module not in ls:
            ls.append(module)

    return ls

# -------- IMPORT
if test():
    import rs

    with ImportPath(SERVERS_PATH):
        for module in scanServers(SERVERS_PATH):
            try:
                exec("import " + module)
            except Exception:
                lx.out("Error importing Rigging System Module: " + str(module))
                lx.out(traceback.format_exc())

    from modules.base import BaseModule
    rs.service.systemComponent.register(BaseModule)

    from modules.base import BaseModuleEventHandler
    rs.service.events.registerHandler(BaseModuleEventHandler)

    from modules.fk_chain import FKChainModule
    rs.service.systemComponent.register(FKChainModule)

    from modules.quad_leg import QuadLegModule
    rs.service.systemComponent.register(QuadLegModule)

    from modules.arm import Arm
    rs.service.systemComponent.register(Arm)

    from modules.arm import ArmVer2
    rs.service.systemComponent.register(ArmVer2)

    from modules.biped_leg import BipedLegVer2
    rs.service.systemComponent.register(BipedLegVer2)

    from modules.torso import TorsoModule
    rs.service.systemComponent.register(TorsoModule)

    from modules.spine import SpineModule
    rs.service.systemComponent.register(SpineModule)

    from modules.std_joint import StandardJointModule
    rs.service.systemComponent.register(StandardJointModule)

    from modules.car_path import CarOnPathModule
    rs.service.systemComponent.register(CarOnPathModule)

    from modules.retarget import BipedRetargetingModule
    rs.service.systemComponent.register(BipedRetargetingModule)

    from modules.retarget import RetargetingModuleEventHandler
    rs.service.events.registerHandler(RetargetingModuleEventHandler)

    from modules.aim_at_joint import AimAtJointModule
    rs.service.systemComponent.register(AimAtJointModule)

    from modules.adv_joint import AdvancedJointModule
    rs.service.systemComponent.register(AdvancedJointModule)

    from modules.eyes import EyesModule
    rs.service.systemComponent.register(EyesModule)

    from modules.eyelids import EyelidsModule
    rs.service.systemComponent.register(EyelidsModule)

    from modules.muscle_joint import MuscleJointModule
    rs.service.systemComponent.register(MuscleJointModule)

    from rigs.biped_retarget import BipedRetargetRig
    rs.service.systemComponent.register(BipedRetargetRig)
