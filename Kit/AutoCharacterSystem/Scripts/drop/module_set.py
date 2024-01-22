#python

import lx

args = lx.args()
lx.eval('rs.module.add {%s} true type:moduleset' % (args[0]))