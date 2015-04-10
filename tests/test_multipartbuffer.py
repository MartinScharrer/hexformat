""" Unit tests for multipartbuffer module.

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


from hexformat.multipartbuffer import MultiPartBuffer, Buffer
from hexformat import IntelHex, RandomContent
import sys
sys.path.append('..')


def Xtest1():
    m = MultiPartBuffer()
    assert m._parts == []
    assert m.set(0,"Test") is m # returns self
    assert m._parts == [[0,Buffer("Test")]]
    assert m.fill(0x100,0x8,[0xAA,0xBB,0xCC,0xDD]) is m # returns self
    assert m.get(0x100, 0x8) == Buffer([0xAA,0xBB,0xCC,0xDD,0xAA,0xBB,0xCC,0xDD])
    assert m.fill(0x200,0x8) is m # returns self
    assert m.get(0x200, 0x8) == Buffer([0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
    assert m.delete(0x100, 0x4) == m # returns self
    assert len(m.parts()) == 3
    assert m._parts[1][0] == 0x104
    
def Xtest2():
    m = MultiPartBuffer()
    m.fill(0,0x1000, RandomContent())
    m.fill(0x1000,0x1000, RandomContent())
    m.fill(0x10000,0x10000, RandomContent())
    assert m.tobinfile("test2.bin") is m # retuns self
    n = MultiPartBuffer.frombinfile("test2.bin")
    m.fillgaps()
    assert m == n
    assert m._parts == n._parts
    ih = IntelHex.frombinfile("test2.bin")
    assert ih._parts == m._parts
    assert ih.toihexfile("test2.hex") is ih # returns self
    ih2 = IntelHex.fromihexfile("test2.hex")
    assert ih == ih2
    
def test_multipartbuffer_init():
    """Init must set _parts to an empty list"""
    assert MultiPartBuffer()._parts == list()
    
def test_multipartbuffer_repr():
    """Instance shall return suitable represenation"""
    assert isinstance(MultiPartBuffer().__repr__(), str) # check for string, not for content
    
def test_multipartbuffer_eq():
    """Instance must be logical equal to other instance with equal data content"""
    m1 = MultiPartBuffer()
    m2 = MultiPartBuffer()
    assert m1 == m2
    m1.fill(0x100,0x100,"Test")
    m2.fill(0x100,0x100,"Test")
    assert m1 == m2
    m1.fill(0x0,0x100,"Test")
    m2.fill(0x0,0x100,"Test")
    assert m1 == m2
    m1.fillgaps()
    m2.fillgaps()
    assert m1 == m2
    
    