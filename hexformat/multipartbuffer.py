
class Buffer(bytearray):
    pass


class MultiPartBuffer(object):

    def __init__(self):
        self._parts = list()

    def __str__(self):
        return str(self.parts())

    def __repr__(self):
        return str(self)

    def _create(self, beforeindex, address, data=list()):
        """Create new buffer before index or at end if index is None"""
        buffer = Buffer(data)
        if beforeindex is None:
            self._parts.append( [ address, buffer ] )
        else:
            self._parts.insert(beforeindex, [ address, buffer ])

    def _find(self, address, size, create=True):
        """Returns (buffer index, mod) for given address and size.
           The meaning of <mod> is:
              0  Buffer of given index contains at least part of the given range. Always returned if create=True.
              1  No buffer containing the given range found. Index states next buffer with an higher address.
             -1  Address lies after all buffers. Index states last buffer before address.
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
        data = None
        if dataoffset == 0 and datasize == len(newdata):
            data = newdata
        else:
            data = newdata[dataoffset:dataoffset+datasize]
        self._parts[index][1] = Buffer(data) + self._parts[index][1]
        self._parts[index][0] -= datasize

    def _set(self, index, address, newdata, datasize, dataoffset):
        bufferstart = self._parts[index][0]
        bufferoffset = address - bufferstart
        data = None
        if dataoffset == 0 and datasize == len(newdata):
            data = newdata
        else:
            data = newdata[dataoffset:dataoffset+datasize]
        self._parts[index][1] [bufferoffset:bufferoffset+datasize] = data

    def _extend(self, index, newdata, datasize, dataoffset):
        data = None
        if dataoffset == 0 and datasize == len(newdata):
            data = newdata
        else:
            data = newdata[dataoffset:dataoffset+datasize]
        self._parts[index][1].extend( data )

    def _merge(self, index):
        """Merge the given buffer with the next one"""
        nextpart = self._parts.pop(index+1)
        self._parts[index][1].extend( nextpart[1] )

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
                return
            else:
                gap = nextbufferstart - bufferend
                self._extend( index, newdata, gap, dataoffset )
                datasize -= gap
                dataoffset += gap
                address += gap
                self._merge( index )
                self.set( address, newdata, datasize, dataoffset, overwrite )

    def clip(self, address, size=None):
        """Clip content to range <address>+<size> by deleting all other content."""
        address,size = self._checkaddrnsize(address,size)
        start,totalsize = self.range()
        end = start + totalsize
        self.delete(start, address-start)
        self.delete(address+size, end-address)
        return self
        
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
        size = int(size)
        if isinstance(fillpattern, BaseException) or ( type(fillpattern) == type and issubclass(fillpattern, BaseException) ):
            raise fillpattern
        if isinstance(fillpattern, int):
            fillpattern = [ fillpattern, ]
        elif type(fillpattern) == type:
            try:
                fillpattern = fillpattern( size )
            except TypeError:
                fillpattern = fillpattern()
        num = int( size / len(fillpattern) )
        buffer = None
        try:
            buffer = Buffer(fillpattern * num)
        except:
            buffer = Buffer(fillpattern) * num
        rest = size - len(buffer)
        if rest > 0:
            buffer.extend(fillpattern[0:rest])
        return buffer

    def _checkaddrnsize(self,address, size):
        if address is None or size is None:
            start,totalsize = self.range()
            if address is None:
                address = start
            if size is None:
                size = start + totalsize - address
        return (address,size)
    
    def fill(self, address=None, size=None, fillpattern=0xFF, overwrite=False):
        """Fill with <fillpattern> from <address> for <size> bytes.
           Filling pattern can be a single byte (0..255) or list-like object.
           If <overwrite> is False (default) then only gaps are filled.
           If <address> is None the first existing address is used.
           If <size> is None the remaining size is used.
        """
        address,size = self._checkaddrnsize(address,size)
        self.set(address, self._filler(size, fillpattern), size, 0, overwrite)
        return self

    def unfill(self, address=None, size=None, unfillpattern=0xFF, mingapsize=16):
        """Removes <unfillpattern> and leaves a gap, as long a resulting new gap would be least <mingapsize> large."""
        if len(self._parts) == 0:
            return self
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

    def get(self, address, size, fillpattern=0xFF):
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
                    retbuffer.extend( self._filler(after , fillpattern) )
                else:
                    gap = nextbufferstart - bufferend
                    retbuffer.extend( self._filler(gap , fillpattern) )
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

    def parts(self):
        return [ (start, len(data)) for start,data in self._parts ]

    def gaps(self):
        gaplist = list()
        for n in range(0,len(self._parts)-1):
            address,buffer = self._parts[n]
            nextaddress = self._parts[n+1][0]
            endaddress = address + len(buffer)
            gap = nextaddress - endaddress
            gaplist.append( [endaddress, gap] )
        return gaplist

    def fillgaps(self, fillpattern=0xFF):
        for address,size in self.gaps():
            self.fill(address, size, fillpattern)

    def fillbegin(self, fillpattern=0xFF):
        if len(self._parts) > 0:
            address = self._parts[0][0]
            self.fill(0, address, fillpattern)

    def tobinfile(self, filename, address=None, size=None, fillpattern=0xFF, options="w"):
        with open(filename, options) as fh:
            self.tobinfh(fh, address, size, fillpattern)

    def tobinfh(self, fh, address=None, size=None, fillpattern=0xFF):
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

    def todict(self):
        d = { addr:byte for addr,byte in enumerate(buffer, address) for address, buffer in self._parts }
        return d
        
    def fromdict(self, d, overwrite=True):
        for addr,byte in d.iteritems():
            self.set(addr, (byte,), 1, overwrite=overwrite)

    def __iadd__(self, other):
        self._iadd(other, True)
        
    def __ior__(self, other):
        self._iadd(other, False)
        
    def _iadd(self, other, overwrite):
        source = None
        if isinstance(other, MultiPartBuffer):
            source = other._parts
        elif isinstance(other, dict):
            source = other.iteritems()
        else:
            source = other
        try:
            print repr(other)
            for address,buffer in source:
                self.set(address, buffer, overwrite=overwrite)
        except Exception as e:
            raise TypeError(e)
        return self
        
    def __add__(self, other):
        sum = self.copy()
        sum.__iadd__(other)
        return sum
        
    def copy(self):
        import copy
        return copy.deepcopy(self)
        
    def filter(self, filterfunc, address=None, size=None, fillpattern=0xFF):
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
            
        