

import os
import shutil
import collections

import modo
import modox

import rs


def buildPresetFromTemplate(filename, monitor, monitorTicks):

    if not os.path.isfile(filename):
        return

    rs.run('!scene.new')
    rs.run('!rs.rig.new')
    rs.run('item.channel rsDrawRefSize false')  # Turn off drawing of the size reference guide

    _processTemplateFile(filename, monitor, monitorTicks)

def buildSampleSceneFromTemplate(filename, monitor, monitorTicks):
    _processTemplateFile(filename, monitor, monitorTicks)

def _processTemplateFile(filename, monitor, monitorTicks):

    kitPath = rs.service.path.get(rs.c.Path.MAIN)
    editRigRootIdent = None
    pause = False

    with open(filename) as f:
        lines = f.read().splitlines()

        length = len(lines)
        lineTick = float(monitorTicks) / float(length)

        for line in lines:
            monitor.tick(lineTick)

            if not line:
                continue
            if line.startswith('#'):
                continue

            if line.startswith('$STOP'):
                return
            if line.startswith('$PAUSE'):
                pause = True
                continue
            if line.startswith('$RESUME'):
                pause = False
                continue

            if pause:
                continue

            # Replace rig root reference here
            if line.find('$RIGROOT') > -1:
                if editRigRootIdent is None:
                    scene = rs.Scene()
                    editRig = scene.editRig
                    editRigRootIdent = editRig.rootModoItem.id
                line = line.replace('$RIGROOT', editRigRootIdent)

            line = line.replace('$KIT', kitPath)

            # Replacing item reference
            itemRef = line.find('$ITEM')
            if itemRef > -1:

                startPos = itemRef + 6  # first letter of item name
                endPos = line.find('>')
                refName = line[startPos:endPos]
                rs.log.out('refname for item: %s' % refName)
                try:
                    item = modox.SceneUtils.findItemFast(refName)
                except LookupError:
                    pass
                else:
                    stringToReplace = '$ITEM<' + refName + '>'
                    rs.log.out('item ident: %s' % item.Ident())
                    line = line.replace(stringToReplace, item.Ident())

            if line.startswith('$CONNECT'):
                parsed = line.split('>')
                line = _connectPlug(parsed[1], parsed[2], editRigRootIdent)
            elif line.startswith('$ATTACH_GUIDE'):
                parsed = line.split('>')
                line = _attachGuide(parsed[1], parsed[2], editRigRootIdent)

            if line:
                rs.run(line)

def _connectPlug(plugModoName, socketModoName, rigRootIdent):
    scene = modo.Scene()
    try:
        plug = scene.item(plugModoName)
        socket = scene.item(socketModoName)
    except LookupError:
        rs.log.out('Bad plug or socket reference: %s / %s' % (plugModoName, socketModoName))
        return None

    scene.select([plug, socket], add=False)

    return 'rs.item.connectPlug rootItem:{%s}' % rigRootIdent

def _attachGuide(guideDrivenModoName, guideDriverModoName, rigRootIdent):
    scene = modo.Scene()

    try:
        driven = scene.item(guideDrivenModoName)
        driver = scene.item(guideDriverModoName)
    except LookupError:
        rs.log.out('Bad guide reference: %s / %s' % (driven, driver))
        return None

    return 'rs.guide.attachToOther guideFrom:{%s} guideTo:{%s} rootItem:{%s}' % (driven.id, driver.id, rigRootIdent)
