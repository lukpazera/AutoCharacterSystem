#python

import lx

args = lx.args()
lx.eval('rs.rig.fromDroppedPreset rootItem:{%s}' % args[0])
