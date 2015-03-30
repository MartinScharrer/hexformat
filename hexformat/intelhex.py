import random


def hexstr2int(hexstr):
    return int(hexstr, 16)
    
class HexfileCrcError(Exception):
    pass
    
class Buffer(bytearray):
    pass
    
class RandomContent(object):
    def __init__(self, length=1):
        self._length = int(length)
        
    def __len__(self):
        return self._length
        
    def __mul__(self, m):
        return self.__class__( self._length * int(m) )
        
    def __imul__(self, m):
        self._length *= int(m)
       
    def __iter__(self):
        return self._produce( 1 )

    def __str__(self):
        return str(Buffer(self._produce( 1 )))
        
    def __getslice__(self, i, j):
        return self.__class__( j - i )

    def __getitem__(self, i):
        return random.randint(0, 255)
        
    def _produce(self, length):
        length = int(length) * self._length
        n = 0
        while n < length:
            n += 1
            yield random.randint(0, 255)
            
    
    
class SplitFile(object):

    def __init__(self):
        self._parts = list()
        
    def parts(self):
        return [ (start, len(data)) for start,data in self._parts ]
        
    def __str__(self):
        return "\n".join([ "%d+%d: %s" % (start, len(data), str(data)) for start,data in self._parts ])
        
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
        self._parts[index][0] -= datasize
        data = None
        if dataoffset == 0 and datasize == len(newdata):
            data = newdata
        else:
            data = newdata[dataoffset:dataoffset+datasize]
        self._parts[index][1].insert( data )
        
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

class IntelHex(SplitFile):
    def tofile(self, fh, format='hex'):
        import intelhex
        ih = intelhex.IntelHex()
        for start,buffer in self._parts:
            ih.fromdict(dict([ (start+n), byte ] for n,byte in enumerate1(buffer) ))
        ih.tofile(fh, format)
        
class SRecord(object):
    _addresslength = (2,2,3,4,None,2,None,4,3,2)
        
    @classmethod
    def _parseline(cls, line):
        try:
            line = line.rstrip("\r\n")
            startcode = line[0]
            if startcode != "S":
                raise ValueError
            recordtype = int(line[1])
            bytes = bytearray.fromhex(line[2:])
        except:
            raise ValueError            
        bytecount = bytes[0]
        if bytecount != len(bytes)-1:
            raise ValueError
        crccorrect = ( (sum(bytes) & 0xFF) == 0xFF)
        al = cls._addresslength[recordtype]
        adresse = hexstr2int(line[4:4+2*al])      
        datasize = bytecount - al - 1
        data = bytes[1+al:-1]
        return (recordtype, adresse, data, datasize, crccorrect)
        
    @classmethod
    def fromfile(cls, frep, format='auto'):
        format = format.lower()
        if format == 'srec':
            return cls.fromsrecfile(frep)
        elif format == 'bin':
            return cls.frombinfile(frep)
    
    @classmethod
    def fromsrecfile(cls, frep):
        self = cls()
        if not hasattr(frep, "readline"):
            frep = open(frep, "r")
        
        line = frep.readline()
        while line != '':
            (recordtype, bytecount, adresse, data, datasize, crccorrect) = cls._parseline(line)
            if recordtype >= 1 and recordtype <= 3:
                self.add(adresse, data, datasize)
            line = frep.readline()
