

import lx
import lxu
import modo

import rs


class CmdClearEventQueue(lxu.command.BasicCommand):
    """ Command used to clear event queue on the C++ side.
    
    The command doesn't do anything but is picked up by
    listener on C++ side.
    
    The command is set as UI command, should not affect undo stack.
    """

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

    def cmd_Flags(self):
        return lx.symbol.fCMD_UI
    
    def basic_Enable (self, msg):
        return True

    def basic_Execute(self, msg, flags):
        pass

rs.cmd.bless(CmdClearEventQueue, 'rs.sys.clearEventQueue')


class CmdParseEventQueue(rs.Command):
    """ Parses event queue and processes all the events in the queue.
    
    This command needs to be defined to be within an undo group
    so it doesn't add its own undo step but it undoed with previous command
    in one step. This is defined via configs with a setup like this:
    
    <atom type="CommandUndoGroup">
        <hash type="Command" key="my.command">myUndoGroup</hash>
        <hash type="GroupBehavior" key="myUndoGroup">undoPlusPrevious</hash>
    </atom>
    
    Replace myUndoGroup and my.command respectively.
    See the general.cfg for the actual setup.
    """
    
    ARG_QUEUE = 'ident'

    def arguments(self):
        queueArg = rs.cmd.Argument(self.ARG_QUEUE, 'string')
        queueArg.defaultValue = ''
        return [queueArg]

    def enable(self, msg):
        return True

    def flags(self):
        return lx.symbol.fCMD_UNDO
    
    def execute(self, msg, flags):
        lx.eval('!rs.sys.clearEventQueue')

        queue = self.getArgumentValue(self.ARG_QUEUE)
        events = queue.split(';')
        
        for event in events:
            e = event.split(':')

            identifier = e[0]
            if len(e) > 1:
                arguments = e[1].split(',')
            else:
                arguments = []

            try:
                eventObj = rs.service.systemComponent.get(rs.c.SystemComponentType.SCENE_EVENT, identifier)
            except LookupError:
                if rs.debug.output:
                    rs.log.out('Unrecognised scene event!', rs.log.MSG_ERROR)
                continue
            else:
                eventObj.process(arguments)


rs.cmd.bless(CmdParseEventQueue, 'rs.sys.parseEventQueue')
