""" Provide class to handle a data buffer with multiple disconnected parts.

  License::

    MIT License

    Copyright (c) 2015-2022 by Martin Scharrer <martin.scharrer@web.de>

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software
    and associated documentation files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
    BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import collections.abc as collections
import copy

from hexformat.fillpattern import FillPattern, int_to_bytes

MOD_USABLE_BUFFER_FOUND = 0
MOD_NO_BUFFER_FOUND_NEXT_HIGHER_USED = 1
MOD_BEYOND_END_LAST_BUFFER_USED = -1


def ensurebuffer(buforint):
    if isinstance(buforint, bytearray):
        return buforint
    elif isinstance(buforint, collections.Sequence):
        return bytearray(buforint)
    else:
        return bytearray((buforint,))


class MultiPartBuffer(object):
    # noinspection PyUnresolvedReferences
    """Class to handle disconnected binary data.

       Each segment (simply called "part") is identified by its starting address and its content (a Buffer instance).

       Attributes:
         _STANDARD_FORMAT (str): The standard format used by :meth:`.fromfh` and :meth:`.fromfile` if no format
                                 was given.
         _padding (int, iterable or FillPattern): Standard fill pattern.
    """
    _STANDARD_FORMAT = 'bin'
    _padding = 0xFF

    def __init__(self):
        super(MultiPartBuffer, self).__init__()
        self._parts = list()

    def __repr__(self):
        """Print representation including class name, id, number of parts, range and used size."""
        start, totalsize = self.range()
        return "<{:s} at 0x{:X}: {:d} parts in range 0x{:X} + 0x{:X}; used 0x{:X}>".format(self.__class__.__name__,
                                                                                           id(self), len(self._parts),
                                                                                           start, totalsize,
                                                                                           self.usedsize())

    # noinspection PyProtectedMember
    def __eq__(self, other):
        """Compare with other instance for equality."""
        return self._parts == other._parts

    def _create(self, beforeindex, address, data=list()):
        """Create new buffer before index or at end if index is None.
        
           Args:
             beforeindex (int): The data will be inserted before this index.
             address (int): Address of first byte in data buffer.
             data (Buffer): Data to be stored.
        """
        buffer = bytearray(data)
        if beforeindex is None:
            self._parts.append([address, buffer])
        else:
            self._parts.insert(beforeindex, [address, buffer])

    def _find(self, address, size, create=True):
        """Find buffer corresponding to data block given by address and size.
        
           Args:
             address (int): Starting address of data block.
             size (int): Size of data block.
             create (bool): If True a new (empty) buffer is created if no suitable one already exists.
        
           Returns:
             Tuple (buffer index, mod). The meaning of <mod> is
                0: MOD_USABLE_BUFFER_FOUND: Buffer of given index contains at least part of the given range. Always
                                            returned if create=True.
                1: MOD_NO_BUFFER_FOUND_NEXT_HIGHER_USED: No buffer containing the given range found. Index states next
                                                         buffer with an higher address.
                -1: MOD_BEYOND_END_LAST_BUFFER_USED: Address lies after all buffers. Index states last buffer before
                                                     address.
        """
        dataend = address + size
        for index, part in enumerate(self._parts):
            bufstart, buffer = part
            bufend = bufstart + len(buffer)
            if address < bufstart:
                if dataend < bufstart:
                    if create:
                        self._create(index, address)
                        return index, MOD_USABLE_BUFFER_FOUND
                    else:
                        return index, MOD_NO_BUFFER_FOUND_NEXT_HIGHER_USED
                else:
                    return index, MOD_USABLE_BUFFER_FOUND
            elif address <= bufend:
                return index, MOD_USABLE_BUFFER_FOUND
        # If this line is reached no matching buffer was found and address lies after all buffers
        index = (len(self._parts) - 1)
        if create:
            self._create(None, address)
            index += 1
            return index, MOD_USABLE_BUFFER_FOUND
        else:
            return index, MOD_BEYOND_END_LAST_BUFFER_USED

    def _insert(self, index, newdata, datasize, dataoffset):
        """Insert new data at begin of existing buffer. Reduce starting address of buffer accordantly.
        
           Args:
             index (int): Index of buffer.
             newdata (Buffer): Data buffer with new data to be inserted. 
             datasize (int): Size of data be added. Can be smaller than data buffer size if not all content should be
                             inserted.
             dataoffset (int): Starting read offset of newdata.
        """
        if dataoffset == 0 and datasize == len(newdata):
            data = newdata
        else:
            data = newdata[dataoffset:dataoffset + datasize]
        self._parts[index][1] = bytearray(data) + self._parts[index][1]
        self._parts[index][0] -= datasize  # adjust address

    def _set(self, index, address, newdata, datasize, dataoffset):
        """Store new data in given buffer at given address. New data is read from given offset for the given size.
        
           Args:
             index (int): Index of buffer where data will be stored.
             address (int): Address of first data byte.
             newdata (Buffer): Data buffer with new data. 
             datasize (int): Size of data. Can be smaller than data buffer size if not all content should be inserted.
             dataoffset (int): Starting read offset of newdata.        
        """
        bufferstart = self._parts[index][0]
        bufferoffset = address - bufferstart
        self._parts[index][1][bufferoffset:bufferoffset + datasize] = newdata[dataoffset:dataoffset + datasize]

    def _extend(self, index, newdata, datasize, dataoffset):
        """Extend given buffer with the new data.
        
           Args:
             index (int): Index of buffer where data will be appended.
             newdata (Buffer): Data buffer with new data. 
             datasize (int): Size of data. Can be smaller than data buffer size if not all content should be inserted.
             dataoffset (int): Starting read offset of newdata.       
        """
        if dataoffset == 0 and datasize == len(newdata):
            data = newdata
        else:
            data = newdata[dataoffset:dataoffset + datasize]
        self._parts[index][1].extend(data)

    def _merge(self, index):
        """Merge the given buffer with the next following one.
        
           Args:
             index (int): Index of first buffer which will be merged with the next buffer.
        """
        nextpart = self._parts.pop(index + 1)
        self._parts[index][1].extend(nextpart[1])

    def setint(self, address, intvalue, datasize, byteorder='big', signed=False, overwrite=True):
        """Set integer value at given address."""
        databytes = int_to_bytes(intvalue, datasize, byteorder, signed=signed)
        return self.set(address, databytes, datasize, 0, overwrite)

    def set(self, address, newdata, datasize=None, dataoffset=0, overwrite=True):
        """Add <newdata> starting at <address>.
           The data size can be given explicitly, otherwise it is taken as len(newdata).
           Additionally a data offset can be specified to read the data starting from this index from <newdata>.
        """
        if datasize is None:
            datasize = len(newdata) - dataoffset

        if datasize == 0:
            return self

        (index, mod) = self._find(address, datasize, create=True)
        endaddress = address + datasize

        bufferstart, buffer = self._parts[index]
        bufferend = bufferstart + len(buffer)

        # Insert left overlapping data
        if address < bufferstart:
            before = bufferstart - address
            self._insert(index, newdata, before, dataoffset)
            # Adjust values for remaining data
            datasize -= before
            dataoffset += before
            address += before

        # Overwrite existing data
        if datasize > 0:
            size = min(datasize, bufferend - address)
            if overwrite:
                self._set(index, address, newdata, size, dataoffset)
            datasize -= size
            dataoffset += size
            address += size

        # Insert right overlapping data
        if endaddress > bufferend:
            nextindex = index + 1

            nextbufferstart = None
            if nextindex < len(self._parts):
                nextbufferstart = self._parts[nextindex][0]

            # Check if data does not reach into next buffer
            if nextbufferstart is None or nextbufferstart > endaddress:
                after = endaddress - bufferend
                self._extend(index, newdata, after, dataoffset)
            else:
                gap = nextbufferstart - bufferend
                self._extend(index, newdata, gap, dataoffset)
                datasize -= gap
                dataoffset += gap
                address += gap
                self._merge(index)
                self.set(address, newdata, datasize, dataoffset, overwrite)
        return self

    def crop(self, address, size=None):
        """Crop content to range <address>+<size> by deleting all other content."""
        address, size = self._checkaddrnsize(address, size)
        start, totalsize = self.range()
        end = start + totalsize
        self.delete(start, address - start)
        self.delete(address + size, end - address)
        return self

    def extract(self, address, size=None, keep=True):
        """Extract given range and return it as new instance. Gaps in the range are preserved.
           The <keep> argument controls if the range is kept in the original instance or deleted.
        """
        new = self.copy()
        new.crop(address, size)
        if not keep:
            self.delete(address, size)
        return new

    def includesgaps(self, address=None, size=None):
        address, size = self._checkaddrnsize(address, size)
        (index, mod) = self._find(address, size, False)
        if mod == MOD_USABLE_BUFFER_FOUND:
            (start, data) = self._parts[index]
            end = start + len(data)
            if (address < start) or (end < (address + size)):
                return True
            return False
        else:
            if len(self._parts) == 0 and address == 0 and size == 0:
                return False
            return True

    def offset(self, offset):
        """Add an offset to all addresses.
           A ValueError is raised if offset < -start, as this would lead to negative addresses.
           If offset is None, the negative start address is used, i.e. the first byte is moved to address 0.
        """
        start = self.start()
        if offset is None:
            offset = -start
        else:
            offset = int(offset)
        if offset < -start:
            raise ValueError("offset < -start")
        for part in self._parts:
            part[0] += offset
        return self

    def relocate(self, newaddress, address=None, size=None, overwrite=True):
        """Relocate given range to new address.
           If address is None the start address is used.
           If size is None the remaining size from address to the endaddress is used.
           The <overwrite> argument determines if existing data in the new range is overwritten
           or if the overlapping bytes of the relocated data are discarded. 
        """
        newaddress = int(newaddress)
        address, size = self._checkaddrnsize(address, size)
        start, totalsize = self.range()
        if address == start and size == totalsize:
            self.offset(newaddress - address)
        else:
            data = self.get(address, size)
            self.delete(address, size)
            self.set(newaddress, data, overwrite=overwrite)
        return self

    def __getitem__(self, n):
        try:
            return self.get(int(n), 1)[0]
        except TypeError:
            if n.step is not None:
                raise IndexError("Slice step not supported")
            # _checkaddrnsize is used here while n.stop is not the size but the end address.
            # However, if None the correct size is returned and if not the value is adjusted later
            address, size = self._checkaddrnsize(n.start, n.stop)
            if n.stop is not None:
                size -= address
            return self.get(address, size)

    def delete(self, address, size=None):
        """Deletes <size> bytes starting from <address>. Does nothing if <size> is non-positive."""
        address, size = self._checkaddrnsize(address, size)
        while size > 0:
            (index, mod) = self._find(address, size, create=True)
            bufferstart, buffer = self._parts[index]
            buffersize = len(buffer)
            if address < bufferstart:
                size -= bufferstart - address
                address = bufferstart
            leading = address - bufferstart
            trailing = bufferstart + buffersize - address - size
            trailaddress = address + size
            if trailing > 0:
                if leading > 0:
                    self._parts[index][1] = buffer[0:leading]
                    self._create(index + 1, trailaddress, buffer[buffersize - trailing:buffersize])
                else:
                    self._parts[index][1] = buffer[buffersize - trailing:buffersize]
                    self._parts[index][0] = trailaddress
                break
            else:
                nextbufferstart = None
                if index < len(self._parts) - 1:
                    nextbufferstart = self._parts[index + 1][0]

                if leading > 0:
                    self._parts[index][1] = buffer[0:leading]
                else:
                    self._parts.pop(index)  # index now points to NEXT part

                if nextbufferstart is None:
                    break
                size = -trailing
                address = bufferstart + buffersize
                gap = nextbufferstart - address
                address += gap
                size -= gap
        return self

    def _filler(self, size, fillpattern):
        """Generate buffer with given fillpattern and size."""
        size = int(size)
        if isinstance(fillpattern, BaseException) or (
            type(fillpattern) == type and issubclass(fillpattern, BaseException)):
            raise fillpattern
        if fillpattern is None:
            fillpattern = self._padding
        fillpattern = FillPattern.frompattern(fillpattern)
        return bytearray(fillpattern[0:size])

    def _checkaddrnsize(self, address, size):
        """Helper method: Ensure proper address and size values.

        If address is None the starting address of the instance is substituted.
        Also if size is None the remaining size to the end of the last buffer is substituted.
        """
        if address is None or size is None:
            start, totalsize = self.range()
            if address is None:
                address = start
            if size is None:
                size = start + totalsize - address
        return address, size

    def fill(self, address=None, size=None, fillpattern=None, overwrite=False):
        """Fill with <fillpattern> from <address> for <size> bytes.
           Filling pattern can be a single byte (0..255) or list-like object.
           If <overwrite> is False (default) then only gaps are filled.
           If <address> is None the first existing address is used.
           If <size> is None the remaining size is used.
        """
        address, size = self._checkaddrnsize(address, size)
        self.set(address, self._filler(size, fillpattern), size, 0, overwrite)
        return self

    def unfill(self, address=None, size=None, unfillpattern=None, mingapsize=16):
        """Removes <unfillpattern> and leaves a gap, as long a resulting new gap would be least <mingapsize> large."""
        if len(self._parts) == 0:
            return self
        if unfillpattern is None:
            unfillpattern = self._padding
        if isinstance(unfillpattern, int):
            unfillpattern = [unfillpattern, ]
        unfillpattern = bytearray(unfillpattern)
        ufvlen = len(unfillpattern)
        address, size = self._checkaddrnsize(address, size)
        (index, mod) = self._find(address, size, create=False)
        if mod != MOD_USABLE_BUFFER_FOUND:
            return self
        uflist = list()
        while index < len(self._parts) and size > 0:
            bufferstart, buffer = self._parts[index]
            buffersize = len(buffer)
            startpos = address - bufferstart
            if startpos < 0:
                size += startpos
                startpos = 0
            maxpos = min(buffersize, size)
            pos = startpos
            try:
                while pos < maxpos:
                    delstartpos = buffer.index(unfillpattern, pos, maxpos)
                    pos = delstartpos + ufvlen
                    while buffer.startswith(unfillpattern, pos, maxpos):
                        pos += ufvlen
                    ufsize = pos - delstartpos
                    # always delete at part boundaries
                    if ufsize >= mingapsize or pos == buffersize or delstartpos == startpos:
                        uflist.append((bufferstart + delstartpos, ufsize))
            except ValueError:
                pass
            index += 1
            size -= maxpos
            address += buffersize

        for deladdr, delsize in uflist:
            self.delete(deladdr, delsize)
        return self

    def get(self, address, size, fillpattern=None):
        """ Get <size> bytes from <address>. Fill missing bytes with <fillpattern>.

            Where <fillpattern> can be:
             1. A byte-sized integer, i.e. in range 0..255.
             2. A list-like object which has all of the following properties:
                 - can be converted to a list of bytes
                 - is indexable
                 - should be multipliable
             3. A type which produces a list-like object as mentioned in 2) if
                instanciated with no argument or with the requested size as only argument.
             4. An exception class or instance.
                If given then no filling is performed but the exception is raised if filling would be required.
        """
        address, size = self._checkaddrnsize(address, size)
        (index, mod) = self._find(address, size, create=False)
        endaddress = address + size

        retbuffer = bytearray()

        if mod != 0:
            return self._filler(size, fillpattern)
        else:
            bufferstart, buffer = self._parts[index]
            bufferend = bufferstart + len(buffer)

            if address < bufferstart:
                before = bufferstart - address
                retbuffer = self._filler(before, fillpattern)
                size -= before
                address += before

            pos = address - bufferstart
            insize = min(size, bufferend - pos)
            if insize > 0:
                if len(retbuffer) > 0:
                    retbuffer.extend(buffer[pos: pos + insize])
                else:
                    retbuffer = buffer[pos: pos + insize]
                size -= insize
                address += insize

            if endaddress > bufferend:
                nextindex = index + 1

                nextbufferstart = None
                if nextindex < len(self._parts):
                    nextbufferstart = self._parts[nextindex][0]
                # Check if data does not reach into next buffer
                if nextbufferstart is None or nextbufferstart > endaddress:
                    after = endaddress - bufferend
                    retbuffer.extend(self._filler(after, fillpattern))
                else:
                    gap = nextbufferstart - bufferend
                    retbuffer.extend(self._filler(gap, fillpattern))
                    size -= gap
                    address += gap
                    retbuffer.extend(self.get(address, size, fillpattern))
        return retbuffer

    def range(self):
        """Get range of content as (start address, size) tuple. The range may contain unfilled gaps.
           An empty buffer with return (0, 0).
        """
        if len(self._parts) == 0:
            return 0, 0
        else:
            start = self._parts[0][0]
            lastaddress, buffer = self._parts[-1]
            totalsize = lastaddress + len(buffer) - start
            return start, totalsize

    def start(self):
        """Get start address. An empty buffer with return 0."""
        if len(self._parts) == 0:
            return 0
        else:
            return self._parts[0][0]

    def end(self):
        """Get end address, i.e. the address one after the very last byte of data.
           An empty buffer will return 0.
        """
        (start, totalsize) = self.range()
        return start + totalsize

    def usedsize(self):
        """Returns used data size, i.e. without the size of any gaps"""
        return sum([len(buffer) for addr, buffer in self._parts])

    def parts(self):
        """Return a list with (address,length) tuples for all parts."""
        return [(start, len(data)) for start, data in self._parts]

    def gaps(self):
        """Return a list with (address,length) tuples for all gaps between the existing parts."""
        gaplist = list()
        for n in range(0, len(self._parts) - 1):
            address, buffer = self._parts[n]
            nextaddress = self._parts[n + 1][0]
            endaddress = address + len(buffer)
            gap = nextaddress - endaddress
            gaplist.append([endaddress, gap])
        return gaplist

    def fillgaps(self, fillpattern=None):
        """Fill all gaps with given fillpattern."""
        for address, size in self.gaps():
            self.fill(address, size, fillpattern)
        return self

    def fillfront(self, startaddress=0, fillpattern=None):
        """Fill the data range in front starting from the given address (0 by default)
           to the beginning of the buffer.
        """
        if len(self._parts) > 0:
            endaddress = self._parts[0][0]
            size = endaddress - startaddress
            if size > 0:
                self.fill(startaddress, size, fillpattern)
        return self

    def fillend(self, endaddress, fillpattern=None):
        """Fill the data range after the buffer up to the given address.
        """
        (startaddress, totalsize) = self.range()
        startaddress += totalsize
        size = endaddress - startaddress
        if size > 0:
            self.fill(startaddress, size, fillpattern)
        return self

    def tobinfile(self, filename, address=None, size=None, fillpattern=None):
        """ """
        with open(filename, "wb") as fh:
            return self.tobinfh(fh, address, size, fillpattern)

    def tobinfh(self, fh, address=None, size=None, fillpattern=None):
        """ """
        start, esize = self.range()
        if address is not None:
            if address < 0:
                address = 0
            endaddress = start + esize
            esize = endaddress - address
            start = address
            if esize < 0:
                esize = 0
        if size is None:
            size = esize
        fh.write(self.get(start, size, fillpattern))
        return self

    def todict(self):
        """Return a dictionary with a numeric key for all used bytes like intelhex.IntelHex does it."""
        d = {addr: byte for address, buffer in self._parts for addr, byte in enumerate(buffer, address)}
        return d

    def loaddict(self, d, overwrite=True):
        """Load data from dictionary where each key must be numeric and represent an address and the corresponding \
        value the byte value."""
        for addr, byte in d.items():
            self.set(addr, (byte,), 1, overwrite=overwrite)
        return self

    def __iadd__(self, other):
        """Add content of other instance to itself, overwriting existing data if parts overlap.
        
           Args:
             other (MultiPartBuffer, dict or iterable): Second summand.
               If a dict then the keys must be address and the values a buffer.
               If an iterable it must yield (address, data) combinations. 
        """
        return self.add(other, True)

    def __add__(self, other):
        """Add two instances together and return the sum as new instance.

           Args:
             other (MultiPartBuffer, dict or iterable): Second summand.
               If a dict then the keys must be address and the values a buffer.
               If an iterable it must yield (address, data) combinations.

           Returns:
             New instance with the data of both sources combined.
             Overlapping parts will be set to the data of the second summand.
        """
        newinst = self.copy()
        newinst.__iadd__(other)
        return newinst

    def __ior__(self, other):
        """Add content of other instance to itself, keeping existing data if parts overlap.
        
           Args:
             other (MultiPartBuffer, dict or iterable): Second summand.
               If a dict then the keys must be address and the values a buffer.
               If an iterable it must yield (address, data) combinations. 
        """
        return self.add(other, False)

    def __or__(self, other):
        inst = self.copy()
        return inst.add(other, False)

    def add(self, other, overwrite=True):
        """Add content of other instance to itself, overwriting or keeping existing data if parts overlap.
            
           Args:
             other (MultiPartBuffer, dict or iterable): Second summand.
               If a dict then the keys must be address and the values a buffer.
               If an iterable it must yield (address, data) combinations. 
             overwrite (bool): If True existing data will be overwritten if parts overlap.
        """
        if isinstance(other, MultiPartBuffer):
            source = other._parts
        elif isinstance(other, dict):
            source = iter(other.items())
        else:
            source = other
        try:
            for address, buffer in source:
                self.set(address, ensurebuffer(buffer), overwrite=overwrite)
        except Exception as e:
            raise TypeError(e)
        return self

    def copy(self):
        """Return a deep copy of the instance."""
        return copy.deepcopy(self)

    def filter(self, filterfunc, address=None, size=None, fillpattern=None):
        """Call filterfunc(bufferaddr, buffer, bufferstartindex, buffersize) on all parts matching <address> and <size>.
           If <address> is None the first existing address is used.
           If <size> is None the remaining size is used.
           If fillpattern is NOT None the given range is filled and the filter function will be called with the
           resulting single part.
        """
        address, size = self._checkaddrnsize(address, size)
        if size <= 0:  # don't filter over a non-positive range
            return self
        if fillpattern is not None:
            self.fill(address, size, fillpattern)
        (startindex, mod1) = self._find(address, size, create=False)
        if mod1 != MOD_USABLE_BUFFER_FOUND:  # range not included (was not filled)
            return self
        endaddress = address + size
        (lastindex, mod2) = self._find(endaddress - 1, 0, create=False)
        if mod2 == MOD_NO_BUFFER_FOUND_NEXT_HIGHER_USED:
            lastindex -= 1
        for bufferaddr, buffer in self._parts[startindex:lastindex + 1]:
            bufferstartindex = max(address - bufferaddr, 0)
            bufferendindex = min(len(buffer), endaddress - bufferaddr)
            filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex)
        return self

    @classmethod
    def fromfile(cls, filename, fformat=None, *args, **kvargs):
        """ """
        if fformat is None:
            fformat = cls._STANDARD_FORMAT
        methodname = "from" + fformat.lower() + "file"
        if hasattr(cls, methodname):
            return getattr(cls, methodname)(filename, *args, **kvargs)
        else:
            with open(filename, "r") as fh:
                return cls.fromfh(fh, *args, fformat=fformat, **kvargs)

    def loadfile(self, filename, fformat=None, *args, **kvargs):
        """ """
        with open(filename, "rb") as fh:
            return self.loadfh(fh, fformat, *args, **kvargs)

    def tofile(self, filename, fformat=None, *args, **kvargs):
        """ """
        opt = "w"
        if fformat == "bin" or (fformat is None and self._STANDARD_FORMAT == "bin"):
            opt = "wb"
        with open(filename, opt) as fh:
            self.tofh(fh, *args, fformat=fformat, **kvargs)
        return self

    def tofh(self, fh, fformat=None, *args, **kvargs):
        """ """
        if fformat is None:
            fformat = self._STANDARD_FORMAT
        methodname = "to" + fformat.lower() + "fh"
        if hasattr(self, methodname):
            getattr(self, methodname)(fh, *args, **kvargs)
        else:
            raise ValueError
        return self

    def loadfh(self, fh, fformat=None, *args, **kvargs):
        """ """
        if fformat is None:
            fformat = self._STANDARD_FORMAT
        methodname = "load" + fformat.lower() + "fh"
        if hasattr(self, methodname):
            getattr(self, methodname)(fh, *args, **kvargs)
        else:
            raise ValueError
        return self

    @classmethod
    def fromfh(cls, fh, fformat=None, *args, **kvargs):
        """ """
        if fformat is None:
            fformat = cls._STANDARD_FORMAT
        methodname = "load" + fformat.lower() + "fh"
        self = cls()
        if hasattr(self, methodname):
            getattr(self, methodname)(fh, *args, **kvargs)
        else:
            raise ValueError
        return self

    @classmethod
    def frombinfile(cls, filename, address=0, size=-1, offset=0):
        """ """
        with open(filename, "rb") as fh:
            return cls.frombinfh(fh, address, size, offset)

    @classmethod
    def frombinfh(cls, fh, address=0, size=-1, offset=0):
        """ """
        self = cls()
        self.loadbinfh(fh, address, size, offset)
        return self

    def loadbinfh(self, fh, address=0, size=-1, offset=0):
        """ """
        if offset != 0:
            fh.seek(offset, (offset < 0) and 2 or 0)
        buffer = bytearray(fh.read(size))
        self.set(address, buffer)
        return self

    def loadbinfile(self, filename, address=0, size=-1, offset=0):
        """ """
        with open(filename, "rb") as fh:
            return self.loadbinfh(fh, address, size, offset)
