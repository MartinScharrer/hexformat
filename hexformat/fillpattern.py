""" Provide auto-scaling fill patterns including a random pattern.

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

import copy
import random
import sys

if sys.version_info < (3,):
    # noinspection PyUnresolvedReferences
    integer_types = (int, long,)
else:
    integer_types = (int,)

try:
    int_to_bytes = int.to_bytes
except AttributeError:
    def int_to_bytes(value, length, byteorder, signed=False):
        length = int(length)
        databytes = bytearray(length)
        limit = 2 ** (length * 8 - 1)
        if (signed and not (-limit <= value < limit)) or (not signed and not (0 <= value < 2 * limit)):
            raise OverflowError("invalid int")
        if signed and value < 0:
            value += 2 * limit
        for n in range(0, length):
            databytes[n] = value & 0xFF
            value >>= 8
        if byteorder == 'big':
            databytes.reverse()
        elif byteorder == 'little':
            pass
        else:
            raise ValueError("byteorder must be either 'little' or 'big'")
        return databytes


class FillPattern(object):
    """General fill pattern class which instances contain a underlying pattern with is automatically repeated if \
       required.

        The underlying pattern is a bytearray which is repeated on demand to fit into a given official length or a slice
        of any length. An internal start offset for the underlying pattern is used when an instance is produced as slice
        with a non-zero start offset.
       
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
        if isinstance(pattern, integer_types):
            if pattern < 0x100:
                pattern = [pattern, ]
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
                      If None then the length of the pattern is used instead.
              length (int): Official length of pattern. If None the length of the pattern is used.
                      If smaller than the pattern length, only the first `length` bytes are used from the pattern.
                                              
            Returns:
              Instance of class based on the given pattern and length.
        """
        if isinstance(pattern, cls):
            return pattern[0:length]
        else:
            return cls(pattern, length)

    @classmethod
    def fromnumber(cls, number, width=4, byteorder='big', length=None, signed=False):
        """Generate instance from integer number. (Python 3 only)
        
            Args:
              number (int):  a numerical value which will be used for the pattern.
              width (int):  byte width of the number. Usually 1 till 4. If number is narrower than this width it is
                            zero padded.
              byteorder ('big'|'little'):  If 'big' (default) the number will be turned into a list of bytes from most
                                   to least significant byte ("MSB first", "Motorola" style).
                                   Otherwise the byte order will be from least to most significant byte ("LSB first",
                                   "Intel" style). For any other byte order the method :meth:`frompattern` must be used
                                   with a byte list.
              length (None or int, optional): Official length of FillPattern. Only used if used with len() or str() etc.     
                                              If None then the length of the pattern is used instead.
              signed (bool; optional): determines if number is represented in two's complement. If False and number is
                                       negative an OverflowError is raised.
                                              
            Returns:
              New instance of the same class.
        """
        pattern = int_to_bytes(number, width, byteorder, signed=signed)
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
        if not isinstance(m, integer_types) or m <= 0:
            raise ValueError("can't multiply instance by non-int or non-positive integer")
        return self[0:self._length * m]

    def __imul__(self, m):
        """Scale official length by the given integer.
        
           Args:
             m (int or long; >0): Factor for with the length of the FillPattern shall be multiplied 
             
           Raises:
             ValueError: if m is not a positive int or long.
        """
        if not isinstance(m, integer_types) or m <= 0:
            raise ValueError("can't multiply instance by non-int or non-positive integer")
        self._length *= int(m)
        return self

    def __iter__(self):
        """Yields every element over official length."""
        plen = len(self._pattern)
        for i in range(0, self._length):
            n = (self._offset + i) % plen
            yield self._pattern[n]

    # noinspection PyProtectedMember
    def __getitem__(self, i):
        """Return item at given official index by repeating internal pattern."""
        try:
            n = (self._offset + int(i)) % len(self._pattern)
            return self._pattern[n]
        except TypeError:
            other = copy.deepcopy(self)
            start = i.start
            stop = i.stop
            if i.step is not None:
                raise KeyError("Step not supported")
            if start is None:
                start = 0
            elif start < 0:
                start = self._length + start
            if stop is None:
                stop = self._length
            elif stop < 0:
                stop = self._length + stop
            other._offset += start
            other._length = stop - start
            plen = len(self._pattern)
            if other._offset > plen:
                other._offset %= plen
            return other


class RandomContent(FillPattern):
    """Specific FillPattern subclass to produce random content. 
    
        Return random content instead any given pattern.
        Every call produces a different random content. 
        For this the Python :meth:`random.randint` method is used.

        Args:
            length (int): Official length. Only used if used with len() etc.

        Raises:
            AttributeError: May be raised by len(pattern) if input is not as requested above.     
    """

    def __init__(self, length=1):
        pattern = [0, ]
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
        if not isinstance(factor, integer_types) or factor <= 0:
            raise ValueError("can't multiply instance by non-int or non-positive integer")
        return self.__class__(self._length * int(factor))

    def __iter__(self):
        """Yield random byte values. The number of bytes is the official length of the instance."""
        for n in range(0, self._length):
            yield random.randint(0, 255)

    def __getitem__(self, i):
        """Return random byte value independent from input value."""
        if isinstance(i, slice):
            return super(RandomContent, self).__getitem__(i)
        return random.randint(0, 255)
