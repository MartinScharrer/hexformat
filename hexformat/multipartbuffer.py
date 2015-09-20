""" Provide class to handle a data buffer with multiple disconnected parts.

  License::

    Copyright (C) 2015  Martin Scharrer <martin@scharrer-online.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from fillpattern import FillPattern

class MultiPartBuffer(object):
    """Class to handle disconnected binary data.

       Each segment (simply called "part") is identified by its starting address and its content (a Buffer instance).
       
       Attributes:
         _STANDARD_FORMAT (str): The standard format used by :meth:`.fromfh` and :meth:`.fromfile` if no format was given.
         _padding (int, iterable or FillPattern): Standard fill pattern.
    """
    _STANDARD_FORMAT = 'bin'
    _padding = 0xFF

    def __init__(self):
        self._parts = list()

    def __repr__(self):
        """Print representation including class name, id, number of parts, range and used size."""
        start, totalsize = self.range()
        return "<{:s} at 0x{:X}: {:d} parts in range 0x{:X} + 0x{:X}; used 0x{:X}>".format(self.__class__.__name__, id(self), len(self._parts), start, totalsize, self.usedsize())

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
        buffer = Buffer(data)
        if beforeindex is None:
            self._parts.append( [ address, buffer ] )
        else:
            self._parts.insert(beforeindex, [ address, buffer ])

    def _find(self, address, size, create=True):
        """Find buffer corresponding to data block given by address and size.
        
           Args:
             address (int): Starting address of data block.
             size (int): Size of data block.
             create (bool): If True a new (empty) buffer is created if no suitable one already exists.
        
           Returns:
             Tuple (buffer index, mod). The meaning of <mod> is
                0: Buffer of given index contains at least part of the given range. Always returned if create=True.
                1: No buffer containing the given range found. Index states next buffer with an higher address.
                -1: Address lies after all buffers. Index states last buffer before address.
        """
        dataend = address + size
        for index,part in enumerate(self._parts):
            bufstart, buffer = part
            bufend = bufstart + len(buffer)
            if (address < bufstart):
                if (dataend < bufstart):
                    if create:
                        self._create(index, address)
                        return (index, 0)
                    else:
                        return (index, 1)
                if (dataend >= bufstart):
                    return (index, 0)
            elif (address <= bufend):
                return (index, 0)
            else:
                pass
        # If this line is reached no matching buffer was found and address lies after all buffers
        index = (len(self._parts) - 1)
        if create:
            self._create(None, address)
            index += 1
            return (index, 0)
        else:
            return (index, -1)

    def _insert(self, index, newdata, datasize, dataoffset):
        """Insert new data at begin of existing buffer. Reduce starting address of buffer accordantly.
        
           Args:
             index (int): Index of buffer.
             newdata (Buffer): Data buffer with new data to be inserted. 
             datasize (int): Size of data be added. Can be smaller than data buffer size if not all content should be inserted.
             dataoffset (int): Starting read offset of newdata.
        """
        data = None
        if dataoffset == 0 and datasize == len(newdata):
            data = newdata
        else:
            data = newdata[dataoffset:dataoffset+datasize]
        self._parts[index][1] = Buffer(data) + self._parts[index][1]
        self._parts[index][0] -= datasize   # adjust address

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
        data = None
        if dataoffset == 0 and datasize == len(newdata):
            data = newdata
        else:
            data = newdata[dataoffset:dataoffset+datasize]
        self._parts[index][1] [bufferoffset:bufferoffset+datasize] = data

    def _extend(self, index, newdata, datasize, dataoffset):
        """Extend given buffer with the new data.
        
           Args:
             index (int): Index of buffer where data will be appended.
             newdata (Buffer): Data buffer with new data. 
             datasize (int): Size of data. Can be smaller than data buffer size if not all content should be inserted.
             dataoffset (int): Starting read offset of newdata.       
        """
        data = None
        if dataoffset == 0 and datasize == len(newdata):
            data = newdata
        else:
            data = newdata[dataoffset:dataoffset+datasize]
        self._parts[index][1].extend( data )

    def _merge(self, index):
        """Merge the given buffer with the next following one.
        
           Args:
             index (int): Index of first buffer which will be merged with the next buffer.
        """
        nextpart = self._parts.pop(index+1)
        self._parts[index][1].extend( nextpart[1] )
        
    def setint(self, address, intvalue, datasize, bigendian=True, overwrite=True):
        """Set integer value at given address."""
        datasize = int(datasize)
        bytes = bytearray(datasize)
        order = range(0,datasize)
        if bigendian:
            order.reverse()
        for n in order:
            bytes[n] = intvalue & 0xFF
            intvalue >>= 8
        return self.set(address, bytes, datasize, 0, overwrite)

    def set(self, address, newdata, datasize=None, dataoffset=0, overwrite=True):
        """Add <newdata> starting at <address>.
           The data size can be given explicitly, otherwise it is taken as len(newdata).
           Additionally a data offset can be specified to read the data starting from this index from <newdata>.
        """
        if datasize is None:
            datasize = len(newdata) - dataoffset
        (index, mod) = self._find(address, datasize, create=True)
        endaddress = address + datasize

        bufferstart, buffer = self._parts[index]
        bufferend = bufferstart + len(buffer)

        # Insert left overlapping data
        if address < bufferstart:
            before = bufferstart - address
            self._insert( index, newdata, before, dataoffset)
            # Adjust values for remaining data
            datasize -= before
            dataoffset += before
            address += before

        # Overwrite existing data
        if datasize > 0:
            size = min(datasize, bufferend-address)
            if overwrite:
                self._set( index, address, newdata, size, dataoffset)
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
                self._extend( index, newdata, after, dataoffset )
            else:
                gap = nextbufferstart - bufferend
                self._extend( index, newdata, gap, dataoffset )
                datasize -= gap
                dataoffset += gap
                address += gap
                self._merge( index )
                self.set( address, newdata, datasize, dataoffset, overwrite )
        return self

    def crop(self, address, size=None):
        """Crop content to range <address>+<size> by deleting all other content."""
        address,size = self._checkaddrnsize(address,size)
        start,totalsize = self.range()
        end = start + totalsize
        self.delete(start, address-start)
        self.delete(address+size, end-address)
        return self
        
    def __getslice__(self, i, j):
        """Return new instance with content cropped to given range."""
        sliceinst = self.copy()
        sliceinst.crop(i, j-i)
        return sliceinst

    def delete(self, address, size=None):
        """Deletes <size> bytes starting from <address>. Does nothing if <size> is non-positive."""
        address,size = self._checkaddrnsize(address,size)
        while size > 0:
            (index, mod) = self._find(address, size, create=True)
            bufferstart, buffer = self._parts[index]
            buffersize = len(buffer)
            if address < bufferstart:
                size -= bufferstart - address
                address = bufferstart
            leading  = address - bufferstart
            trailing = bufferstart + buffersize - address - size
            trailaddress = address + size
            if trailing > 0:
                if leading > 0:
                    self._parts[index][1] = buffer[0:leading]
                    self._create(index+1, trailaddress, buffer[buffersize-trailing:buffersize])
                else:
                    self._parts[index][1] = buffer[buffersize-trailing:buffersize]
                    self._parts[index][0] = trailaddress
                break
            else:
                nextbufferstart = None
                if index < len(self._parts)-1:
                    nextbufferstart = self._parts[index+1][0]

                if leading > 0:
                    self._parts[index][1] = buffer[0:leading]
                else:
                    self._parts.pop(index) # index now points to NEXT part

                if nextbufferstart is None:
                    break
                size = -trailing
                address = bufferstart + buffersize
                gap = nextbufferstart - address
                if gap < size:
                    address += gap
                    size -= gap
                else:
                    break
        return self

    def _filler(self, size, fillpattern):
        """Generate buffer with given fillpattern and size."""
        size = int(size)
        if isinstance(fillpattern, BaseException) or ( type(fillpattern) == type and issubclass(fillpattern, BaseException) ):
            raise fillpattern
        if fillpattern is None:
            fillpattern = self._padding
        fillpattern = FillPattern.frompattern(fillpattern)
        return Buffer(fillpattern[0:size])

    def _checkaddrnsize(self, address, size):
        """Helper method: Ensure proper address and size values.

        If address is None the starting address of the instance is substituted.
        Also if size is None the remaining size to the end of the last buffer is substituted.
        """
        if address is None or size is None:
            start,totalsize = self.range()
            if address is None:
                address = start
            if size is None:
                size = start + totalsize - address
        return (address,size)

    def fill(self, address=None, size=None, fillpattern=None, overwrite=False):
        """Fill with <fillpattern> from <address> for <size> bytes.
           Filling pattern can be a single byte (0..255) or list-like object.
           If <overwrite> is False (default) then only gaps are filled.
           If <address> is None the first existing address is used.
           If <size> is None the remaining size is used.
        """
        address,size = self._checkaddrnsize(address,size)
        self.set(address, self._filler(size, fillpattern), size, 0, overwrite)
        return self

    def unfill(self, address=None, size=None, unfillpattern=None, mingapsize=16):
        """Removes <unfillpattern> and leaves a gap, as long a resulting new gap would be least <mingapsize> large."""
        if len(self._parts) == 0:
            return self
        if unfillpattern is None:
            unfillpattern = self._padding
        if isinstance(unfillpattern, int):
            unfillpattern = [ unfillpattern, ]
        unfillpattern = Buffer(unfillpattern)
        ufvlen = len(unfillpattern)
        address,size = self._checkaddrnsize(address,size)
        (index, mod) = self._find(address, size, create=False)
        if mod == -1:
            return self
        elif mod == 1:
            start = self._parts[index][0]
            dist = start - address
            size -= dist
            index = 0
        uflist = list()
        while index < len(self._parts) and size > 0:
            bufferstart,buffer = self._parts[index]
            buffersize = len(buffer)
            maxpos = min(buffersize,size)
            startpos = address - bufferstart
            pos = startpos
            try:
                while pos < maxpos:
                    delstartpos = buffer.index(unfillpattern, pos, maxpos)
                    pos = delstartpos + ufvlen
                    while buffer.startswith(unfillpattern, pos, maxpos):
                        pos += ufvlen
                    ufsize = pos - delstartpos
                    if ufsize >= mingapsize or pos == buffersize or delstartpos == startpos: # always delete at part boundaries
                        uflist.append((bufferstart+delstartpos,ufsize))
            except ValueError:
                pass
            index += 1
            size -= maxpos

        for deladdr,delsize in uflist:
            self.delete(deladdr,delsize)
        return self

    def get(self, address, size, fillpattern=None):
        """Get <size> bytes from <address>. Fill missing bytes with <fillpattern>.
           Where <fillpattern> can be:
             1) A byte-sized integer, i.e. in range 0..255.
             2) A list-like object which has all of the following properties:
                a) can be converted to a list of bytes
                d) is indexable
                c) should be multipliable
             3) A type which produces a list-like object as mentioned in 2) if
                instanciated with no argument or with the requested size as only argument.
             4) An exception class or instance.
                If given then no filling is performed but the exception is raised if filling would be required.
        """
        address,size = self._checkaddrnsize(address,size)
        (index, mod) = self._find(address, size, create=False)
        endaddress = address + size

        retbuffer = Buffer()

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
            insize = min(size, bufferend-pos)
            if insize > 0:
                if len(retbuffer) > 0:
                    retbuffer.extend( buffer[ pos : pos+insize ] )
                else:
                    retbuffer = buffer[ pos : pos+insize ]
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
                    retbuffer.extend( self._filler(after, fillpattern) )
                else:
                    gap = nextbufferstart - bufferend
                    retbuffer.extend( self._filler(gap, fillpattern) )
                    size -= gap
                    address += gap
                    retbuffer.extend( self.get( address, size, fillpattern) )
        return retbuffer

    def range(self):
        """Get range of content as (address, size) tuple. The range may contain unfilled gaps."""
        if len(self._parts) == 0:
            return (0,0)
        else:
            start = self._parts[0][0]
            lastaddress, buffer = self._parts[-1]
            totalsize = lastaddress + len(buffer) - start
            return (start, totalsize)

    def usedsize(self):
        """Returns used data size, i.e. without the size of any gaps"""
        return sum([ len(buffer) for addr,buffer in self._parts ])


    def parts(self):
        """Return a list with (address,length) tuples for all parts."""
        return [ (start, len(data)) for start,data in self._parts ]

    def gaps(self):
        """Return a list with (address,length) tuples for all gaps between the existing parts."""
        gaplist = list()
        for n in range(0,len(self._parts)-1):
            address,buffer = self._parts[n]
            nextaddress = self._parts[n+1][0]
            endaddress = address + len(buffer)
            gap = nextaddress - endaddress
            gaplist.append( [endaddress, gap] )
        return gaplist

    def fillgaps(self, fillpattern=None):
        """Fill all gaps with given fillpattern."""
        for address,size in self.gaps():
            self.fill(address, size, fillpattern)
        return self

    def fillbegin(self, fillpattern=None):
        """ """
        if len(self._parts) > 0:
            address = self._parts[0][0]
            self.fill(0, address, fillpattern)
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
        fh.write( self.get(start, size, fillpattern) )
        return self

    def todict(self):
        """Return a dictionary with a numeric key for all used bytes like intelhex.IntelHex does it."""
        d = { addr:byte for addr,byte in enumerate(buffer, address) for address, buffer in self._parts }
        return d

    def loaddict(self, d, overwrite=True):
        """Load data from dictionary where each key must be numeric and represent an address and the corresponding value the byte value."""
        for addr,byte in d.iteritems():
            self.set(addr, (byte,), 1, overwrite=overwrite)
        return self

    def __iadd__(self, other):
        """Add content of other instance to itself, overwriting existing data if parts overlap.
        
           Args:
             other (MultiPartBuffer, dict or iterable): Second summand.
               If a dict then the keys must be address and the values a buffer.
               If an iterable it must yield (address, data) combinations. 
        """
        self._iadd(other, True)

    def __ior__(self, other):
        """Add content of other instance to itself, keeping existing data if parts overlap.
        
           Args:
             other (MultiPartBuffer, dict or iterable): Second summand.
               If a dict then the keys must be address and the values a buffer.
               If an iterable it must yield (address, data) combinations. 
        """
        self._iadd(other, False)

    def _iadd(self, other, overwrite):
        """Add content of other instance to itself, overwriting or keeping existing data if parts overlap.
            
           Args:
             other (MultiPartBuffer, dict or iterable): Second summand.
               If a dict then the keys must be address and the values a buffer.
               If an iterable it must yield (address, data) combinations. 
             overwrite (bool): If True existing data will be overwritten if parts overlap.
        """
        source = None
        if isinstance(other, MultiPartBuffer):
            source = other._parts
        elif isinstance(other, dict):
            source = other.iteritems()
        else:
            source = other
        try:
            for address,buffer in source:
                self.set(address, buffer, overwrite=overwrite)
        except Exception as e:
            raise TypeError(e)
        return self

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
        sum = self.copy()
        sum.__iadd__(other)
        return sum

    def copy(self):
        """Return a deep copy of the instance."""
        import copy
        return copy.deepcopy(self)

    def filter(self, filterfunc, address=None, size=None, fillpattern=None):
        """Call filterfunc(bufferaddr, buffer, bufferstartindex, buffersize) on all parts matching <address> and <size>.
           If <address> is None the first existing address is used.
           If <size> is None the remaining size is used.
           If fillpattern is NOT None the given range is filled and the filter function will be called with the resulting single part.
        """
        address,size = self._checkaddrnsize(address,size)
        if size <= 0: # don't filter over a non-positive range
            return self
        if fillpattern is not None:
            self.fill(address, size, fillpattern)
        (startindex, mod) = self._find(address, size, create=False)
        if mod == -1: # range not included (was not filled)
            return self
        endaddress = address + size
        (lastindex, mod) = self._find(endaddress-1, 0, create=False)
        if mod == 1:
            lastindex -= 1
        for bufferaddr,buffer in self._parts[startindex:lastindex+1]:
            bufferstartindex = max(address - bufferaddr, 0)
            buffersize = min( len(buffer) - bufferstartindex, endaddress - bufferaddr)
            filterfunc(bufferaddr, buffer, bufferstartindex, buffersize)

    @classmethod
    def fromfile(cls, filename, format=None, *args, **kvargs):
        """ """
        with open(filename, "rb") as fh:
            return cls.fromfh(fh, *args, format=format, **kvargs)

    @classmethod
    def fromfh(cls, fh, format=None, *args, **kvargs):
        """ """
        if format is None:
            format = cls._STANDARD_FORMAT
        methodname = "from" + format.lower() + "fh"
        if hasattr(cls, methodname):
            return getattr(cls, methodname)(fh, *args, **kvargs)
        else:
            raise ValueError

    def tofile(cls, filename, format=None, *args, **kvargs):
        """ """
        opt = "w"
        if format == "bin" or (format is None and cls._STANDARD_FORMAT == "bin"):
            opt = "wb"
        with open(filename, opt) as fh:
            return cls.fromfh(fh, *args, format=format, **kvargs)

    def tofh(cls, fh, format=None, *args, **kvargs):
        """ """
        if format is None:
            format = cls._STANDARD_FORMAT
        methodname = "to" + format.lower() + "fh"
        if hasattr(cls, methodname):
            return getattr(cls, methodname)(fh, *args, **kvargs)
        else:
            raise ValueError

    @classmethod
    def fromfh(cls, fh, format=None, *args, **kvargs):
        """ """
        if format is None:
            format = cls._STANDARD_FORMAT
        methodname = "load" + format.lower() + "fh"
        self = cls()
        if hasattr(self, methodname):
            getattr(self, methodname)(fh, *args, **kvargs)
            return self
        else:
            raise ValueError

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
        buffer = bytearray( fh.read(size) )
        self.set(address, buffer)
        return self

    def loadbinfile(cls, filename, address=0, size=-1, offset=0):
        """ """
        with open(filename, "rb") as fh:
            return cls.loadbinfh(fh, address, size, offset)


class Buffer(bytearray):
    """Buffer class to abstract real buffer class."""
    pass


