# python

import lx

args = lx.args()
if len(args) == 2:
    lx.eval('rs.item.dropOnItem {%s} {%s} mode:src' % (args[0], args[1]))