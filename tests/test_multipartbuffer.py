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
    
    