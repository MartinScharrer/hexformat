
class Buffer(bytearray):
    pass


class MultiPartBuffer(object):
    _STANDARD_FORMAT = 'bin'

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
        """Returns buffer index for given address and size"""
        dataend = address + size
        for index,part in enumerate(self._parts):
            bufstart, buffer = part
            bufend = bufstart + len(buffer)
            if (address < bufstart):
                if (dataend < bufstart):
                    if create:
                        self._create(index, address)
                        return index
                    else:
                        return "before"
                if (dataend >= bufstart):
                    return index
            elif (address <= bufend):
                return index
            else:
                pass
        # If this line is reached no matching buffer was found and address lies after all buffers
        if create:
            self._create(None, address)
            return (len(self._parts) - 1)
        else:
            return "after"

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

    def set(self, address, newdata, datasize=None, dataoffset=0):
        if datasize is None:
            datasize = len(newdata) - dataoffset
        index = self._find(address, datasize, create=True)
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
                self.set( address, newdata, datasize, dataoffset )

    def delete(self, address, size):
        while size > 0:
            index = self._find(address, size, create=True)
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

    def fill(self, address, size, fillpattern=0xFF):
        """Fill with <fillpattern> from <address> for <size> bytes"""
        self.set(address, self._filler(size, fillpattern), size, 0)

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
        index = self._find(address, size, create=False)
        endaddress = address + size

        retbuffer = Buffer()

        if not isinstance(index, int):
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

    def tobinfile(self, filename, address=None, size=None, fillpattern=0xFF):
        with open(filename, "wb") as fh:
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

    @classmethod
    def fromfile(cls, filename, format=None, *args, **kvargs):
        with open(filename, "rb") as fh:
            return cls.fromfh(fh, *args, format=format, **kvargs)

    @classmethod
    def fromfh(cls, fh, format=None, *args, **kvargs):
        if format is None:
            format = cls._STANDARD_FORMAT
        methodname = "from" + format.lower() + "fh"
        if hasattr(cls, methodname):
            return getattr(cls, methodname)(fh, *args, **kvargs)
        else:
            raise ValueError

    @classmethod
    def frombinfile(cls, filename, address=0, size=-1, offset=0):
        with open(filename, "rb") as fh:
            return cls.frombinfh(fh, address, size, offset)

    @classmethod
    def frombinfh(cls, fh, address=0, size=-1, offset=0):
        self = cls()
        self.loadbinfh(fh, address, size, offset)
        return self

    def loadbinfh(self, fh, address=0, size=-1, offset=0):
        if offset != 0:
            fh.seek(offset, (offset < 0) and 2 or 0)
        buffer = bytearray( fh.read(size) )
        self.set(address, buffer)
        return self

    def loadbinfile(cls, filename, address=0, size=-1, offset=0):
        with open(filename, "rb") as fh:
            return cls.loadbinfh(fh, address, size, offset)
