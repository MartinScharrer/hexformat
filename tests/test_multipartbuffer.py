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

import sys

from hexformat.intelhex import IntelHex
from hexformat.fillpattern import RandomContent
from nose.tools import assert_equal, assert_list_equal, assert_sequence_equal, raises
from hexformat.multipartbuffer import MultiPartBuffer, Buffer
import random

sys.path.append('..')


def randomdata(length):
    # noinspection PyUnusedLocal
    return bytearray((random.randint(0, 255) for n in range(0, length)))


# noinspection PyProtectedMember
def test1():
    m = MultiPartBuffer()
    assert_equal(m._parts, [])
    assert m.set(0, bytearray(10)) is m  # returns self
    assert_equal(m._parts, [[0, Buffer(bytearray(10))]])
    assert m.fill(0x100, 0x8, [0xAA, 0xBB, 0xCC, 0xDD]) is m  # returns self
    assert_equal(m.get(0x100, 0x8), Buffer([0xAA, 0xBB, 0xCC, 0xDD, 0xAA, 0xBB, 0xCC, 0xDD]))
    assert m.fill(0x200, 0x8) is m  # returns self
    assert_equal(m.get(0x200, 0x8), Buffer([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]))
    assert_equal(m.delete(0x100, 0x4), m)  # returns self
    assert_equal(len(m.parts()), 3)
    assert_equal(m._parts[1][0], 0x104)


# noinspection PyProtectedMember
def test2():
    m = MultiPartBuffer()
    m.fill(0, 0x1000, RandomContent())
    m.fill(0x1000, 0x1000, RandomContent())
    m.fill(0x10000, 0x10000, RandomContent())
    assert m.tobinfile("test2.bin") is m  # retuns self
    n = MultiPartBuffer.frombinfile("test2.bin")
    m.fillgaps()
    assert_equal(m, n)
    assert_equal(m._parts, n._parts)
    ih = IntelHex.frombinfile("test2.bin")
    assert_equal(ih._parts, m._parts)
    assert ih.toihexfile("test2.hex") is ih  # returns self
    ih2 = IntelHex.fromihexfile("test2.hex")
    assert_equal(ih, ih2)


# noinspection PyProtectedMember
def test_multipartbuffer_init():
    """Init must set _parts to an empty list"""
    assert_equal(MultiPartBuffer()._parts, list())


def test_multipartbuffer_repr():
    """Instance shall return suitable represenation"""
    assert isinstance(MultiPartBuffer().__repr__(), str)  # check for string, not for content


def test_multipartbuffer_eq():
    """Instance must be logical equal to other instance with equal data content"""
    m1 = MultiPartBuffer()
    m2 = MultiPartBuffer()
    assert_equal(m1, m2)
    m1.fill(0x100, 0x100, bytearray(b"Test"))
    m2.fill(0x100, 0x100, bytearray(b"Test"))
    assert_equal(m1, m2)
    m1.fill(0x0, 0x100, bytearray(b"Test"))
    m2.fill(0x0, 0x100, bytearray(b"Test"))
    assert_equal(m1, m2)
    m1.fillgaps()
    m2.fillgaps()
    assert_equal(m1, m2)


def test_create():
    data = [
        bytearray.fromhex("0123456789"),
        bytearray.fromhex("DEADBEEF"),
        bytearray.fromhex("FEEDAFFE"),
    ]
    mp = MultiPartBuffer()
    mp.set(0x200, data[0])
    assert_list_equal(mp.parts(), [(0x200, len(data[0])), ])
    mp.set(0x100, data[1])
    assert_list_equal(mp.parts(), [(0x100, len(data[1])), (0x200, len(data[0]))])
    mp.set(0x300, data[2])
    assert_list_equal(mp.parts(), [(0x100, len(data[1])), (0x200, len(data[0])), (0x300, len(data[2]))])


# noinspection PyProtectedMember
def test_insert_borders():
    data = [
        randomdata(100),
        randomdata(100),
        randomdata(100),
    ]
    mp = MultiPartBuffer()
    mp.set(1000, data[0])
    assert_list_equal(mp._parts, [[1000, data[0]]])
    mp.set(900, data[1])
    assert_list_equal(mp._parts, [[900, data[1]+data[0]]])
    mp.set(1100, data[2])
    assert_list_equal(mp._parts, [[900, data[1] + data[0] + data[2]]])


# noinspection PyProtectedMember
def test_insert_overlap():
    data = [
        randomdata(100),
        randomdata(100),
        randomdata(100),
    ]
    mp = MultiPartBuffer()
    mp.set(1000, data[0])
    assert_list_equal(mp._parts, [[1000, data[0]]])
    mp.set(950, data[1])
    assert_list_equal(mp._parts, [[950, data[1] + data[0][50:]]])
    mp.set(1080, data[2])
    assert_list_equal(mp._parts, [[950, data[1] + data[0][50:-20] + data[2]]])


def test_get_beforedata():
    mp = MultiPartBuffer()
    mp.set(1000, bytearray(10))
    assert_equal(mp.get(900, 10, 0xFF), bytearray(b"\xFF"*10))


def test_get_betweendata():
    mp = MultiPartBuffer()
    mp.set(800, bytearray(10))
    mp.set(1000, bytearray(10))
    assert_equal(mp.get(1100, 10, 0xFF), bytearray(b"\xFF"*10))


def test_setint():
    mp = MultiPartBuffer()
    mp.setint(address=0x100, intvalue=0xDEADBEEF, datasize=4, byteorder='big', signed=False, overwrite=True)
    assert_equal(mp.get(None, None), bytearray.fromhex("DEADBEEF"))
    mp.setint(address=0x100, intvalue=0xFEEDAFFE, datasize=4, byteorder='big', signed=False, overwrite=False)
    assert_equal(mp.get(None, None), bytearray.fromhex("DEADBEEF"))


def test_crop():
    testdata = randomdata(100)
    mp = MultiPartBuffer()
    mp.set(1000, testdata)
    mp.crop(1010, 80)
    assert_equal(mp.get(None, None), testdata[10:-10])
    mp.crop(1020)
    assert_equal(mp.get(None, None), testdata[20:-10])
    mp.crop(None)
    assert_equal(mp.get(None, None), testdata[20:-10])


def test_extract():
    testdata = randomdata(100)
    mp = MultiPartBuffer()
    mp.set(1000, testdata)
    mp2 = mp.extract(1010, 80)
    assert_equal(mp.get(None, None), testdata)
    assert_equal(mp2.get(None, None), testdata[10:-10])
    mp3 = mp.extract(1020, None, False)
    assert_equal(mp.get(None, None), testdata[0:20])
    assert_equal(mp3.get(None, None), testdata[20:])


def test_includesgaps():
    mp = MultiPartBuffer()
    mp.set(1000, bytearray(100))
    assert_equal(False, mp.includesgaps(None, None))
    mp.set(2000, bytearray(100))
    assert_equal(True, mp.includesgaps(999, 2))
    assert_equal(True, mp.includesgaps(990, 3000))
    assert_equal(True, mp.includesgaps(1099, 2))
    assert_equal(True, mp.includesgaps(1000, 1100))
    assert_equal(True, mp.includesgaps(2099, 2))
    assert_equal(False, mp.includesgaps(1010, 10))
    assert_equal(False, mp.includesgaps(2000, 100))


def test_includesgaps_empty():
    mp = MultiPartBuffer()
    assert_equal(False, mp.includesgaps(0, 0))
    assert_equal(True, mp.includesgaps(1, 0))
    assert_equal(True, mp.includesgaps(0, 1))


def test_offset():
    testdata = randomdata(100)
    mp = MultiPartBuffer()
    mp.set(1000, testdata)
    mp.offset(10)
    assert_equal(mp.get(1010, 100), testdata)
    assert_equal(mp.parts(), [(1010, 100), ])
    mp.offset(-100)
    assert_equal(mp.get(910, 100), testdata)
    assert_equal(mp.parts(), [(910, 100), ])
    mp.offset(None)
    assert_equal(mp.get(0, 100), testdata)
    assert_equal(mp.parts(), [(0, 100), ])


@raises(ValueError)
def test_offset():
    testdata = randomdata(100)
    mp = MultiPartBuffer()
    mp.set(100, testdata)
    mp.offset(-200)


def test_getitem():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer()
    mp.set(0x1000, testdata)
    yield assert_equal, mp[0x1000], testdata[0]
    yield assert_equal, mp[0x1000], mp.get(0x1000, 0x1)[0]
    yield assert_equal, len(mp[0x1000:0x1100]), 0x100
    yield assert_sequence_equal, mp[0x1000:0x1100], mp.get(0x1000, 0x100)
    yield assert_sequence_equal, mp[0x1000:0x1100], testdata


@raises(IndexError)
def test_getitem_step():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer()
    mp.set(0x1000, testdata)
    return mp[0x1000:0x1004:2]
