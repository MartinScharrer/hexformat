from random import randint
import math
import copy

class FillPattern(object):

    @classmethod
    def frompattern(cls, pattern, length=None):
        if isinstance(pattern, cls):
            if length is None or length == len(pattern):
                return pattern
            else:
                return pattern[0:int(length)]
        else:
            if length is None:
                length = len(pattern)
            return cls(pattern, length)

    @classmethod
    def fromnumber(cls, number, width=4, bigendian=True, length=None):
        if not isinstance(number, (int,long)) or not isinstance(width, (int,long)):
            raise ValueError("number and width must be integers")
        pattern = [0,]*width
        for n in range(0,width):
            pattern[n] = number & 0xFF
            number >>= 8
        if bigendian:
            pattern = reversed(pattern)
        return cls(pattern, length)

    def __init__(self, pattern=0xFF, length=None):
        if isinstance(pattern,(int,long)):
            if pattern < 0x100:
                pattern = [pattern,]
            else:
                raise ValueError("numeric pattern must be a single byte (0..255)")
        self._pattern = bytearray(pattern)
        if length is None:
            length = len(self._pattern)
        self._length = length
        self._offset = 0

    def __len__(self):
        return self._length
        
    def setlength(self, length):
        self._length = length

    def __mul__(self, m):
        if not isinstance(m,(int,long)) or m <= 0:
            raise  ValueError("can't multiply instance by non-int or non-positive integer")
        return self[0:self._length * m]

    def __imul__(self, m):
        if not isinstance(m,(int,long)) or m <= 0:
            raise ValueError("can't multiply instance by non-int or non-positive integer")
        self._length *= int(m)
        return self

    def __iter__(self):
        plen = len(self._pattern)
        for i in xrange(0,self._length):
            n = (self._offset + i) % plen
            yield self._pattern[n]

    def __str__(self):
        scale = int(math.ceil( float(self._length + self._offset) / len(self._pattern) ))
        s = str(self._pattern) * scale
        if self._offset > 0:
            s = s[self._offset:self._offset+self._length]
        elif len(s) > self._length:
            s = s[0:self._length]
        return s

    def __getslice__(self, i, j):
        other = copy.deepcopy(self)
        other._offset += i
        other._length  = j - i
        plen = len(self._pattern)
        if other._offset > plen:
            other._length -= int(other._offset / plen)
            other._offset  = other._offset % plen
        return other

    def __getitem__(self, i):
        n = (self._offset + i) % len(self._pattern)
        return self._pattern[n]

        
class RandomContent(FillPattern):
    def __init__(self, pattern=None, length=1):
        try:
            self._length = int(length)
        except TypeError:
            self._length = len(length)

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
        return randint(0, 255)

    def _produce(self, length):
        length = int(length) * self._length
        n = 0
        while n < length:
            n += 1
            yield randint(0, 255)

