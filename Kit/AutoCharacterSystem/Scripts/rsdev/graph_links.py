

import lx
import modo


def printGraphLinks():
    scene = modo.Scene()
    for item in scene.selected:
    
        graphNames = item.itemGraphNames
        
        lx.out('--------------------')
            
        if not graphNames:
            lx.out('%s item has no graph links' % item.name)
            return
        
        lx.out('%s item graph links:' % item.name)
        for graphName in graphNames:
            graph = item.itemGraph(graphName)
            forward = graph.forward()
            if forward:
                lx.out('GRAPH %s FORWARD:' % graphName)
                for connection in forward:
                    lx.out('*   ' + connection.name + ' : ' + connection.id)
            reverse = graph.reverse()
            if reverse:
                lx.out('GRAPH %s REVERSE:' % graphName)
                for connection in reverse:
                    lx.out('*   ' + connection.name + ' : ' + connection.id)
            lx.out('---')

def printRSGraphLinksForSelectedItems():
    scene = modo.Scene()

    for item in scene.selected:
        graphNames = item.itemGraphNames
        
        itemOutput = []
        
        itemOutput.append('--------------------')
        itemOutput.append('%s item RS graph links:' % item.name)
        
        for graphName in graphNames:
            if not graphName.startswith('rs.'):
                continue
            graph = item.itemGraph(graphName)
            forward = graph.forward()
            if forward:
                itemOutput.append('%s FORWARD:' % graphName)
                for connection in forward:
                    itemOutput.append('*   ' + connection.name)
            reverse = graph.reverse()
            if reverse:
                itemOutput.append('%s REVERSE:' % graphName)
                for connection in reverse:
                    itemOutput.append('*   ' + connection.name)

        if len(itemOutput) > 2:
            for o in itemOutput:
                lx.out(o)