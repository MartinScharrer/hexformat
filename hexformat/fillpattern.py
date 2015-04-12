""" Provide auto-scaling fill patterns including a random pattern.

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

from random import randint
import math
import copy

class FillPattern(object):
    """General fill pattern class which instances contain a underlying pattern with is automatically repeated if required.

        The underlying pattern is a bytearray which is repeated on demand to fit into a given official length or a slice of any length.
        An internal start offset for the underlying pattern is used when an instance is produced as slice with a non-zero start offset.
       
        Args:
          pattern (byte or iterable of bytes):  The basic fill pattern which will be repeated.
                          Either a byte sized integer (0..255) or an iterable of such integers 
                          (usually a bytearray, str or suitable list or tuple).
          length (None or int, optional): Official length of FillPattern. Only used if used with len() or str() etc.     
                                          If None then the length of the pattern is used instead.
                                          
        Raises:
          ValueError: if pattern argument is numeric but outside of the byte range of 0..255.     
    """

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
    

    @classmethod
    def frompattern(cls, pattern, length=None):
        """Returns instance by either returning existing one or generate new instance from pattern list. \
           The intended use of this method is as filter of user input, so that an instance or pattern can be passed.
        
            Args:
              pattern (cls, byte or iterable of bytes): If pattern is already an instance of the same class it is used,
                             either directly or as a length adjusted copy if the length argument differs from its length.
                             Otherwise it must be a byte or iterable of bytes which is simply passed to the class constructor.
              length (None or int, optional): Official length of FillPattern. Only used if used with len() or str() etc.     
                                              If None then the length of the pattern is used instead.
                                              
            Returns:
              Instance of class based on the given pattern and length.
        """    
        if isinstance(pattern, cls):
            if length is None or length == len(pattern):
                return pattern
            else:
                return pattern[0:length]
        else:
            return cls(pattern, length)

    @classmethod
    def fromnumber(cls, number, width=4, bigendian=True, length=None):
        """Generate instance from integer number.
        
            Args:
              number (int or long):  a numerical value which will be used for the pattern.
              width (int or long; optional):  byte width of the number. Usually 1 till 4. If number is narrower than this width it is zero padded.
              bigendian (bool; optional):  If True (default) the number will be turned into a list of bytes from most to least significant byte ("MSB first", "Motorola" style).
                                   Otherwise the byte order will be from least to most significant byte ("LSB first", "Intel" style).
                                   For any other byte order the method :meth:`frompattern` must be used with a byte list.
              length (None or int, optional): Official length of FillPattern. Only used if used with len() or str() etc.     
                                              If None then the length of the pattern is used instead.
                                              
            Returns:
              New instance of class.
              
            Raises:
              ValueError: If number or width are anything except an int or long or if with is non-positive.
        """
        if not isinstance(number, (int,long)) or not isinstance(width, (int,long)) or width < 1:
            raise ValueError("number and width must be integers and width must be positive.")
        pattern = [0,]*width
        for n in range(0,width):
            pattern[n] = number & 0xFF
            number >>= 8
        if bigendian:
            pattern = reversed(pattern)
        return cls(pattern, length)

    def __len__(self):
        """Return official length."""
        return self._length

    def setlength(self, length):
        """Set official length.
        
           Args:
             length (int): Official length of FillPattern. Only used if used with len() or str() etc.
        """
        self._length = int(length)

    def __mul__(self, m):
        """Return copy of itself with an official length scaled by the given integer.
        
           Args:
             m (int or long; >0): Factor for with the length of the FillPattern shall be multiplied 
             
           Returns:
             A copy of itself with an official length scaled by the given integer.
             
           Raises:
             ValueError: if m is not a positive int or long.             
        """ 
        if not isinstance(m,(int,long)) or m <= 0:
            raise  ValueError("can't multiply instance by non-int or non-positive integer")
        return self[0:self._length * m]

    def __imul__(self, m):
        """Scale official length by the given integer.
        
           Args:
             m (int or long; >0): Factor for with the length of the FillPattern shall be multiplied 
             
           Raises:
             ValueError: if m is not a positive int or long.
        """     
        if not isinstance(m,(int,long)) or m <= 0:
            raise ValueError("can't multiply instance by non-int or non-positive integer")
        self._length *= int(m)
        return self

    def __iter__(self):
        """Yields every element over official length."""
        plen = len(self._pattern)
        for i in xrange(0,self._length):
            n = (self._offset + i) % plen
            yield self._pattern[n]

    def __str__(self):
        """Return string representation with official length of fillpattern."""
        scale = int(math.ceil( float(self._length + self._offset) / len(self._pattern) ))
        s = str(self._pattern * scale)
        if self._offset > 0:
            s = s[self._offset:self._offset+self._length]
        elif len(s) > self._length:
            s = s[0:self._length]
        return s

    def __getslice__(self, i, j):
        """Return slice using a deep copy with adjusted offset and length."""
        other = copy.deepcopy(self)
        other._offset += i
        other._length  = j - i
        plen = len(self._pattern)
        if other._offset > plen:
            other._length -= int(other._offset / plen)
            other._offset  = other._offset % plen
        return other

    def __getitem__(self, i):
        """Return item at given official index by repeating internal pattern."""
        n = (self._offset + i) % len(self._pattern)
        return self._pattern[n]

        
class RandomContent(FillPattern):
    """Specific FillPattern subclass to produce random content. 
    
        Return random content instead any given pattern.
        Every call produces a different random content. 
        For this the Python :meth:`random.randint` method is used.

        Args:
            pattern (None or byte or iterable of bytes; optional):  Pattern content is ignored, but might be used to set length.
            length (None or int, optional): Official length. Only used if used with len() or str() etc.     
                                            If None then the length of the pattern is used
                                            If it is also None the length is set to 1.
                                          
        Raises:
            AttributeError: May be raised by len(pattern) if input is not as requested above.     
    """
    
    def __init__(self, pattern=None, length=None):
        if length is None:
            if pattern is None:
                length = 1
            else:
                length = len(pattern)
        pattern = [0,]
        super(RandomContent, self).__init__(pattern, length)

    def __mul__(self, factor):
        """Return new instance with length scaled by factor.
        
           Args:
             factor (int or long; >0): Factor for with the length shall be multiplied 
             
           Returns:
             A copy of itself with an official length scaled by the given integer.
             
           Raises:
             ValueError: if factor is not a positive int or long.             
        """
        if not isinstance(factor,(int,long)) or factor <= 0:
            raise  ValueError("can't multiply instance by non-int or non-positive integer")
        return self.__class__(self._length * int(factor))
        
    def __str__(self):
        """Return string with random content with the official length of the instance."""
        return "".join([chr(n) for n in self])

    def __iter__(self):
        """Yield random byte values. The number of bytes is the official length of the instance."""
        for n in xrange(0,self._length):
            yield randint(0, 255)
        
    def __getitem__(self, i):
        """Return random byte value independent from input value."""
        return randint(0, 255)
