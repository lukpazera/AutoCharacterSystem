# python

"""
    Based on Gwynne Reddick example code.
"""

import traceback
import struct
import chunk

try:
    from StringIO import StringIO  # for Python 2
except ImportError:
    from io import StringIO  # for Python 3

import lx
import lxu


class SubChunk(chunk.Chunk):
    """ LXO subchunks need own class because chunk size
    is 2 bytes long instead of 4.
    """

    def __init__(self, file, align=True, bigendian=True, inclheader=False):
        self.closed = False
        self.align = align  # whether to align to word (2-byte) boundaries
        if bigendian:
            strflag = '>'
        else:
            strflag = '<'
        self.file = file
        self.chunkname = file.read(4)
        if len(self.chunkname) < 4:
            raise EOFError
        try:
            self.chunksize = struct.unpack(strflag + 'H', file.read(2))[0]
        except struct.error:
            raise EOFError

        self.size_read = 0
        try:
            self.offset = self.file.tell()
        except (AttributeError, IOError):
            self.seekable = False
        else:
            self.seekable = True


class LXORead:
    def __init__(self):
        self.filename = ''
        self.lx_file = None

        # Basic information about the file
        self.form_id = ''
        self.form_data_size = 0
        self.form_type = ''

    def Start(self, filename):
        """ Open and start reading the file.
        """
        # TODO: Look for what exceptions should be there

        # open is a built in function to open a file
        # rb is read binary mode
        if not filename:
            return False

        self.filename = filename
        try:
            self.lx_file = open(self.filename, 'rb')
        except Exception:
            return False

        # read first chunk / form id
        # struct.unpack method reads a set of strings/integers, etc. outlined in first argument
        # from set of binary data passed in second argument
        # data is returned as tuple ALWAYS, even if only 1 element is returned
        try:
            self.form_id, self.form_data_size, self.form_type = struct.unpack('>4s1L4s', self.lx_file.read(12))
        except Exception:
            lx.out('Bad File...')
            return False

        # In Python 3 all the variables returned from struct.unpack will be byte arrays.
        # In Python 2 they are all strings.
        # So we need to force convert them to strings.
        try:
            self.form_id = str(self.form_id, 'utf-8')
            self.form_type = str(self.form_type, 'utf-8')
        except TypeError:
            pass

        # lx.out(self.form_id)
        # lx.out(self.form_data_size)
        # lx.out(self.form_type)
        return True

    def Close(self):
        self.lx_file.close()

    def Description(self):
        """ Get description tag (if file is a preset)
        """
        d_desc = ''
        while 1:
            try:
                lxchunk = chunk.Chunk(self.lx_file)
            except EOFError:
                break

            # count -= 1
            chunk_id = lxchunk.getname()
            chunk_size = lxchunk.getsize()

            #lx.out(chunk_id, chunk_size)
            if chunk_id == 'DESC':
                d_type = self._get_string(self.lx_file)
                d_desc = self._get_string(self.lx_file)
                #lx.out('----')
                #lx.out(d_type)
                #lx.out(d_desc)
            elif chunk_id == 'PRVW':
                lxchunk.skip()
                break
            else:
                lxchunk.skip()
        return d_desc

    def ItemTags(self, item_type, tag_ids):
        """ Get item tags for a first item
        of a given item type from preset.
        Return a list of tag strings with indexes same as
        ones from tag_id_strings. So to get proper tag strings
        for required tags use the same index as in passed tag_id_strings argument.
        tag_id_strings --- list of tags to return
        *** NOTE *** This is very hacky here but the search only really goes
        if first items are groups and then requested item type HAS to follow.
        If not - searching is stopped. This is OK for assm presets for ACS
        but NOTE THAT THIS METHOD IS NOT GENERAL. It's basically custom method
        for the ACS preset drop server.
        """
        try:
            tag_string_list = []
            if not isinstance(tag_ids, list):
                tag_ids = [tag_ids]
            while 1:
                try:
                    lxchunk = chunk.Chunk(self.lx_file)
                except EOFError:
                    break

                # Read overall item chunk info
                # It's not specific to item chunk, any chunk has that.
                chunk_id = lxchunk.getname()
                chunk_size = lxchunk.getsize()

                # Proof against python3 where chunk id comes as byte array and not string.
                try:
                    chunk_id = str(chunk_id, 'utf-8')
                except TypeError:
                    pass

                if chunk_id == 'ITEM':
                    itemtype, itemname, uniqueID, offset = self._get_item_chunk(lxchunk)
                    if itemtype == item_type:
                        lxchunk.seek(offset)
                        tag_string_list = self._get_item_tag_subchunks(lxchunk, tag_ids)
                        break
                    # This is custom piece of code
                    # BREAKS method generality
                    elif itemtype != 'group':
                        break
                    lxchunk.skip()
                else:
                    lxchunk.skip()
            return tag_string_list
        except:
            lx.out(traceback.format_exc())
            raise

    def _get_string(self, data):
        """ Returns an unpacked string stripped of any null padding.
        """
        string = ''
        while 1:
            char = data.read(1)

            # Python 3 stuff to make sure we're not dealing with byte arrays
            try:
                char = str(char, 'utf-8')
            except TypeError:
                pass
                
            if char == '\0':
                if (len(string) % 2 == 0):
                    # This reading is done only to advance the pointer within data.
                    # No need to force convert char into string for fixing
                    # python3 byte array stuff.
                    char = data.read(1)
            
                return string
            string += char

    def _get_item_chunk(self, lxchunk):
        """ Read main item chunk.
        Item Type
        Item Name
        """
        try:
            offset = 0

            chunk = lxchunk.read()
            # Usual python3 proofing, force convert byte array into string.
            try:
                chunkString = chunk.decode('utf-8', 'ignore')
            except TypeError:
                chunkString = chunk

            data = StringIO(chunkString)
            itemtype = self._get_string(data)
            itemname = self._get_string(data)

            strData = data.read(4)
            try:
                dataToUnpack = bytes(strData, 'utf-8')
            except TypeError:
                dataToUnpack = strData

            uniqueID = struct.unpack(">L", dataToUnpack)[0]
            offset = data.tell()
            return (itemtype, itemname, uniqueID, offset)
        except:
            lx.out(traceback.format_exc())

    def _get_item_tag_subchunks(self, data, tag_ids):
        """ Process item tag subchunks.
        tags_n --- number of tags to find
        tags_to_go --- tags to find counter, used to terminate search early if all tags found.
        """
        tag_strings = []
        tags_n = len(tag_ids)
        tags_to_go = tags_n
        for x in range(tags_n):
            tag_strings.append('')
        while 1:
            try:
                itemchunk = SubChunk(data)
            except EOFError:
                break
            name = itemchunk.chunkname
            
            # Python 3 thing, make sure we have string here
            try:
                name = str(name, 'utf-8')
            except TypeError:
                pass
                
            try:
                if name == 'ITAG':
                    # I HAVE TO READ TAG ID AND STRING
                    # OTHERWISE THE DATA POINTER WILL BE POINTING TO WRONG THING
                    # IT WON'T BE AT THE BEGINNING OF NEXT TAG!!!
                    tagID = struct.unpack(">L", data.read(4))[0]
                    tag_string = self._get_string(data)
                    for x in range(tags_n):
                        if tagID == tag_ids[x]:
                            tag_strings[x] = tag_string
                            tags_to_go -= 1
                    if not tags_to_go:
                        break
                # IF CHUNK IS NOT THE RIGHT ONE WE NEED TO CLOSE IT
                # MEANING SKIPPING AT THE END OF IT IN THE FILE!!!
                else:
                    itemchunk.close()
            except:
                lx.out(traceback.format_exc())
                raise
        return tag_strings

