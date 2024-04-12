# python

""" ---------------------------------------------------------------------------
    Rigging System Preset File Drop Server.
    Provides support for dragging and dropping preset files into the scene.
    ---------------------------------------------------------------------------
"""


import traceback
import time

import lx
import lxifc
import modox
import rs
from rs.const import DropActionCode as d
from rs import io as io

sSERVER_NAME = 'rs.presetDropServer'

ACTION_CODES = {0: d.POSE,
                1: d.MIRRORPOSE,
                2: d.NEWACTION
                }


class RSPresetDropServer(lxifc.Drop):

    def __init__(self):
        """ Initialize action strings from message tables.
        """
        self.platform_service = lx.service.Platform()
        self.preset_service = lx.service.PresetBrowser()
        self.message_service = lx.service.Message()
        self.message = lx.object.Message(self.message_service.Allocate())

        self.action_messages = []
        self.message.SetMessage('rs.presetDropServer', 'Pose', 0)
        self.action_messages.append(self.message_service.MessageText(self.message))
        self.message.SetMessage('rs.presetDropServer', 'PoseMirror', 0)
        self.action_messages.append(self.message_service.MessageText(self.message))

        self.message.SetMessage('rs.presetDropServer', 'ActionNew', 0)
        self.action_messages.append(self.message_service.MessageText(self.message))

        self.preset_filename = ''
        self.preset_type_string = ''

    def drop_Recognize(self, source_object):
        """ Recognize if the source object matches any drop actions.
        - Preset type must be item, category scene item and destination
        - Preset needs to have group item first (assembly), then group locator
        - the group locator needs to have preset type tag.
        - the palette of options will be chosen based on what is in this tag.
        - rig description tag can be used to warn about applying new preset to old.
        """
        # Source object is a value array
        # there might be multiple source objects - need a way to deal with that
        value_array = lx.object.ValueArray(source_object)
        count = value_array.Count()
        recognized = False
        for x in range(count):
            self.preset_filename = value_array.GetString(x)

            try:
                server_name, category = self.preset_service.RecognizeFile(self.preset_filename, 0)
            except Exception:
                server_name = ''
                category = ''

            if not server_name or not category:
                continue

            # It has to be an item preset
            # server name and category have to match
            if not server_name == modox.c.PresetServerName.ITEM or \
                    not category == modox.c.PresetCategory.SCENEITEM:
                continue

            # If the preset matches initially the file needs to be scanned
            # in search of the preset type tag on first group locator item.
            lxo_read = io.LXORead()
            if not lxo_read.Start(self.preset_filename):
                continue

            # desc = lxo_read.Description()
            # Look for 2 tags - preset type and rig description (to know from which rig version was the preset saved)
            tag_ids = [rs.preset.Preset.TAG_PRESET_IDENTIFIER_INT]
            tag_strings = lxo_read.ItemTags('groupLocator', tag_ids)
            lxo_read.Close()

            if tag_strings and tag_strings[0]:
                self.preset_type_string = tag_strings[0]

                recognized = True
                break  # TODO: This enables the drop once at least one preset is valid! Is it good?

        return recognized

    def drop_ActionList(self, source, dest, addDropAction):
        """ Add potential actions to t he list.
        Actions are added via the AddAction method and action
        needs to have integer number.
        """
        # Don't present any actions when there are no rigs in scene.
        # When no actions are added the Drop() method won't be called.
        if not rs.Scene.anyRigsInSceneFast():
            return lx.symbol.e_OK

        action_list = []

        # Test destination item to present choices for user.
        # Make sure not to add any actions if there is no pre dest item.
        # CODE NOT USED RIGHT NOW BUT MAY NEED TO BE USED AT SOME POINT
        # IF ACTIONS DEPEND ON DESTINATION ITEM.
        # dest_item = lx.object.Item()
        # try:
        #     item_predest = lx.object.SceneItemPreDest(dest)
        # except TypeError:
        #     return None
        # else:
        #     if item_predest.test():
        #         try:
        #             dest_item = lx.object.Item(item_predest.Item()[1])
        #         except TypeError:
        #             pass

        if self.preset_type_string == 'pose':
            action_list.append(0)
            action_list.append(1)
        elif self.preset_type_string == 'action':
            action_list.append(2)

        for action_code in action_list:
            lx.object.AddDropAction(addDropAction).AddAction(action_code, self.action_messages[action_code])

        return lx.symbol.e_OK

    def drop_Drop(self, source, dest, action):
        """
        Performs the drop.

        Do something based on action code passed to ActionList.
        NOTE: Action ALWAYS has FIRST added action value,
        even if no action was selected by user!!!
        So first action can be considered default action.
        Because I use assembly presets I still need to run preset.do command, as if user
        just loaded a preset. Therefore drop can only set some additional properties
        for preset loader to read from and determine extra preset options or actions.
        This is done by using 2 user values:
        - rs.c.UserValue.PRESET_DROP_ACTION_CODE - to pass any of the actions picked by user from the drop popup.
        - rs.c.UserValue.PRESET_DEST_IDENT --- to pass ident of the destination item.
        """
        dest_ident = ''
        action_code = ''
        dest_item = lx.object.Item()

        try:
            item_predest = lx.object.SceneItemPreDest(dest)
        except TypeError:
            item_predest = lx.object.SceneItemPreDest()
        if item_predest.test():
            # Test against destination item if no action was choosen by user
            # item_predest = lx.object.SceneItemPreDest(dest)
            try:
                dest_item = lx.object.Item(item_predest.Item()[1])
            except TypeError:
                # Get container item, when clicking on empty viewport space
                # This is getting scene's Environment item.
                # Could be useful to know if user dropped into empty space?
                # This is how to get container item:
                # dest_item = lx.object.Item(item_predest.ContainerItem())
                # I don't need it there though
                pass
        if dest_item.test():
            dest_ident = dest_item.Ident()

        try:
            action_code = ACTION_CODES[action]
        except KeyError:
            pass

        rs.service.userValue.set(rs.c.UserValue.PRESET_DROP_ACTION_CODE, action_code)
        rs.service.userValue.set(rs.c.UserValue.PRESET_DEST_IDENT, dest_ident)
        rs.service.userValue.set(rs.c.UserValue.PRESET_FILENAME, self.preset_filename)
        lx.eval('!preset.do {%s}' % self.preset_filename)


# action names has to be a string with all actions separated by spaces.
actionNames = ''
actionNames += '2@Pose '
actionNames += '3@PoseMirror '
actionNames += '4@ActionNew '
tags = {lx.symbol.sDROP_SOURCETYPE: lx.symbol.sDROPSOURCE_FILES,
        lx.symbol.sDROP_ACTIONNAMES: actionNames,
        lx.symbol.sSRV_USERNAME: "@rs.presetDropServer@Username@"
        }

lx.bless(RSPresetDropServer, sSERVER_NAME, tags)