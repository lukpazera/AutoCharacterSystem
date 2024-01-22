#python

import lx
import rs

args = lx.args()
rs.service.buffer.put(args[0], 'pieceId')