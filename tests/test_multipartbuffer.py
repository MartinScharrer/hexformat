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
from nose.tools import assert_is, assert_equal, assert_list_equal, assert_sequence_equal, raises, assert_less_equal
from hexformat.multipartbuffer import MultiPartBuffer, Buffer
import tempfile
import os
import random

sys.path.append('..')


def randomdata(length):
    # noinspection PyUnusedLocal
    return bytearray((random.randint(0, 255) for n in range(0, length)))


def filldata(length, data=0xFF):
    return bytearray((data,)) * length


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
    assert_sequence_equal(mp.get(900, 10, 0xFF), bytearray(b"\xFF"*10))


def test_get_betweendata():
    mp = MultiPartBuffer()
    mp.set(800, bytearray(10))
    mp.set(1000, bytearray(10))
    assert_sequence_equal(mp.get(1100, 10, 0xFF), bytearray(b"\xFF"*10))


def test_get_overlapstart():
    mp = MultiPartBuffer()
    testdata = randomdata(10)
    mp.set(1000, testdata)
    assert_sequence_equal(mp.get(990, 15, 0xFF), bytearray(b"\xFF"*10) + testdata[0:5])


def test_get_overlapend():
    mp = MultiPartBuffer()
    testdata = randomdata(10)
    mp.set(1000, testdata)
    assert_sequence_equal(mp.get(1005, 15, 0xFF), testdata[5:] + bytearray(b"\xFF"*10))


def test_get_overlapboth():
    mp = MultiPartBuffer()
    testdata = randomdata(10)
    mp.set(1000, testdata)
    assert_sequence_equal(mp.get(990, 30, 0xFF), bytearray(b"\xFF"*10) + testdata + bytearray(b"\xFF"*10))


def test_get_3():
    testdata = randomdata(100)
    mp = MultiPartBuffer()
    mp.set(1000, testdata)
    assert_sequence_equal(mp.get(None, 80), testdata[0:80])


def test_get_zerosize():
    adr = 1000
    length = 100
    end = adr + length
    testdata = randomdata(length)
    mp = MultiPartBuffer()
    mp.set(adr, testdata)
    assert_sequence_equal(mp.get(None, 0), bytearray())
    assert_sequence_equal(mp.get(adr-1, 0), bytearray())
    assert_sequence_equal(mp.get(adr, 0), bytearray())
    assert_sequence_equal(mp.get(adr + 1, 0), bytearray())
    assert_sequence_equal(mp.get(adr - 1, 0), bytearray())
    assert_sequence_equal(mp.get(end, 0), bytearray())
    assert_sequence_equal(mp.get(end + 1, 0), bytearray())
    assert_sequence_equal(mp.get(end - 1, 0), bytearray())
    assert_sequence_equal(mp.get(end - 2, 0), bytearray())


def test_setint():
    mp = MultiPartBuffer()
    mp.setint(address=0x100, intvalue=0xDEADBEEF, datasize=4, byteorder='big', signed=False, overwrite=True)
    assert_sequence_equal(mp.get(None, None), bytearray.fromhex("DEADBEEF"))
    mp.setint(address=0x100, intvalue=0xFEEDAFFE, datasize=4, byteorder='big', signed=False, overwrite=False)
    assert_sequence_equal(mp.get(None, None), bytearray.fromhex("DEADBEEF"))


def test_crop():
    testdata = randomdata(100)
    mp = MultiPartBuffer()
    mp.set(1000, testdata)
    mp.crop(1010, 80)
    assert_sequence_equal(mp.get(None, None), testdata[10:-10])
    mp.crop(1020)
    assert_sequence_equal(mp.get(None, None), testdata[20:-10])
    mp.crop(None)
    assert_sequence_equal(mp.get(None, None), testdata[20:-10])


def test_extract():
    testdata = randomdata(100)
    mp = MultiPartBuffer()
    mp.set(1000, testdata)
    mp2 = mp.extract(1010, 80)
    assert_sequence_equal(mp.get(None, None), testdata)
    assert_sequence_equal(mp2.get(None, None), testdata[10:-10])
    mp3 = mp.extract(1020, None, False)
    assert_sequence_equal(mp.get(None, None), testdata[0:20])
    assert_sequence_equal(mp3.get(None, None), testdata[20:])


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
    assert_sequence_equal(mp.get(1010, 100), testdata)
    assert_list_equal(mp.parts(), [(1010, 100), ])
    mp.offset(-100)
    assert_sequence_equal(mp.get(910, 100), testdata)
    assert_list_equal(mp.parts(), [(910, 100), ])
    mp.offset(None)
    assert_sequence_equal(mp.get(0, 100), testdata)
    assert_list_equal(mp.parts(), [(0, 100), ])


@raises(ValueError)
def test_offset_error():
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


def test_start():
    mp = MultiPartBuffer()
    yield assert_equal, mp.start(), 0
    mp.set(0x1000, bytearray(10))
    yield assert_equal, mp.start(), 0x1000
    mp.set(0x500, bytearray(10))
    yield assert_equal, mp.start(), 0x500
    mp.set(0x1500, bytearray(10))
    yield assert_equal, mp.start(), 0x500


def test_end():
    mp = MultiPartBuffer()
    yield assert_equal, 0, mp.end()
    adr = random.randint(0, 2**32-1)
    size = random.randint(0, 2**16-1)
    mp.set(adr, bytearray(size))
    yield assert_equal, adr+size, mp.end()


def test_relocate_1():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer()
    mp.set(0x200, testdata)
    mp.relocate(0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_equal, mp.range(), (0x100, 0x100)
    yield assert_sequence_equal, mp.get(0x100, 0x100), testdata


def test_relocate_2():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer()
    mp.set(0x200, testdata)
    mp.relocate(0x100, 0x200, 0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_equal, mp.range(), (0x100, 0x100)
    yield assert_sequence_equal, mp.get(0x100, 0x100), testdata


def test_relocate_3():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer()
    mp.set(0x200, testdata)
    mp.relocate(0x100, 0x220, 0x10)
    yield assert_equal, mp.start(), 0x100
    yield assert_equal, mp.range(), (0x100, 0x200)
    yield assert_list_equal, mp.parts(), [(0x100, 0x10), (0x200, 0x20), (0x230, 0x100-0x30)]
    yield assert_sequence_equal, mp.get(0x100, 0x10), testdata[0x20:0x30]
    yield assert_sequence_equal, mp.get(0x200, 0x20), testdata[0x00:0x20]
    yield assert_sequence_equal, mp.get(0x230, None), testdata[0x30:]


def test_relocate_4():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer()
    mp.set(0x100, testdata)
    mp.relocate(0x100, 0x1F0, 0x10, False)
    yield assert_equal, mp.start(), 0x100
    yield assert_equal, mp.range(), (0x100, 0xF0)
    yield assert_list_equal, mp.parts(), [(0x100, 0xF0), ]
    yield assert_sequence_equal, mp.get(0x100, 0xF0), testdata[:0xF0]
    yield assert_sequence_equal, mp.get(None, None), testdata[:0xF0]


def test_delete():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer()
    mp.set(0x100, testdata)
    mp.delete(0xF0, 0x20)
    yield assert_sequence_equal, mp.get(None, None), testdata[0x10:]
    mp.delete(0x1F0, 0x20)
    yield assert_sequence_equal, mp.get(None, None), testdata[0x10:-0x10]
    mp.delete(0x150, 0x10)
    yield assert_list_equal, mp.parts(), [(0x110, 0x40), (0x160, 0x90)]


def test_delete_all():
    testdata = bytearray(100)
    mp = MultiPartBuffer()
    mp.set(10000, testdata)
    mp.delete(9999, 102)
    yield assert_list_equal, mp.parts(), []


# noinspection PyProtectedMember
def test_delete_2():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp = MultiPartBuffer()
    mp.set(200, testdata1)
    mp.set(400, testdata2)
    mp.delete(100, 350)
    yield assert_list_equal, mp._parts, [[450, testdata2[50:]], ]


def test_delete_overlap():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer()
    mp.set(0x100, testdata)
    mp.delete(0xF0, 0x20)
    yield assert_sequence_equal, mp.get(None, None), testdata[0x10:]
    mp.delete(0x1F0, 0x20)
    yield assert_sequence_equal, mp.get(None, None), testdata[0x10:-0x10]
    mp.delete(0x150, 0x10)
    yield assert_list_equal, mp.parts(), [(0x110, 0x40), (0x160, 0x90)]


# noinspection PyProtectedMember
def test_filler_1():
    mp = MultiPartBuffer()
    mp._padding = 0xAA
    yield assert_sequence_equal, b'\x5A' * 10, mp._filler(10, 0x5A)
    yield assert_sequence_equal, b'\xAA' * 20, mp._filler(20, None)


class MyExept(ValueError):
    pass


# noinspection PyProtectedMember
@raises(MyExept)
def test_filler_2():
    mp = MultiPartBuffer()
    return mp._filler(1, MyExept)


# noinspection PyProtectedMember
def test_copy():
    mp = MultiPartBuffer()
    for n in range(0, random.randint(1, 10)):
        adr = random.randint(0, 2 ** 16 - 1)
        size = random.randint(0, 2 ** 16 - 1)
        mp.set(adr, randomdata(size))
    mp2 = mp.copy()
    yield assert_equal, mp._parts, mp2._parts
    yield assert_equal, mp.__dict__, mp2.__dict__


# noinspection PyProtectedMember
def test_loaddict():
    mp = MultiPartBuffer()
    mp.loaddict({100: 0xDE, 101: 0xAD, 102: 0xBE, 103: 0xEF, 200: 0x00, 0: 0x11})
    yield assert_sequence_equal, mp._parts, [[0, bytearray((0x11, ))],
                                             [100, bytearray.fromhex('DEADBEEF')],
                                             [200, bytearray((0x00, ))]]
    mp.loaddict({100: 0xFF, 101: 0xFF, 102: 0x00, 103: 0xAA, 200: 0xBB, 1: 0x22}, False)
    yield assert_sequence_equal, mp._parts, [[0, bytearray((0x11, 0x22))],
                                             [100, bytearray.fromhex('DEADBEEF')],
                                             [200, bytearray((0x00,))]]
    testdata = randomdata(210)
    mp.loaddict({n: b for n, b in enumerate(testdata)})
    yield assert_list_equal, mp._parts, [[0, testdata], ]


def test_ior():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp1 = MultiPartBuffer().set(100, testdata1)
    mp2 = MultiPartBuffer().set(180, testdata2)
    mp1 |= mp2
    assert_sequence_equal(mp1[:], testdata1 + testdata2[20:])


def test_or():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp1 = MultiPartBuffer().set(100, testdata1)
    mp2 = MultiPartBuffer().set(150, testdata2)
    mp = mp1 | mp2
    assert_sequence_equal(mp[:], testdata1 + testdata2[50:])


def test_iand():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp1 = MultiPartBuffer().set(100, testdata1)
    mp2 = MultiPartBuffer().set(180, testdata2)
    mp1 += mp2
    assert_sequence_equal(mp1[:], testdata1[:-20] + testdata2)


def test_and():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp1 = MultiPartBuffer().set(100, testdata1)
    mp2 = MultiPartBuffer().set(150, testdata2)
    mp = mp1 + mp2
    testdata = testdata1[0:50] + testdata2
    yield assert_sequence_equal, mp[:], testdata


def test_unfill_empty():
    mp = MultiPartBuffer()
    assert_is(mp.unfill(), mp)
    assert_list_equal(mp.parts(), [])


def test_unfill_mingapsize():
    mp = MultiPartBuffer()
    mp.set(100, bytearray(100))
    mp.set(210, bytearray(100))
    fillpattern = randomdata(1)
    mp.fill(fillpattern=fillpattern)
    mp2 = mp.copy()
    mp.unfill(unfillpattern=fillpattern, mingapsize=16)
    assert_equal(mp, mp2)


def test_unfill_multiple():
    mp = MultiPartBuffer()
    fillbyte = randomdata(1)[0]
    mp.set(1000, bytearray(1000))
    mp.set(1100, filldata(100, fillbyte))
    mp.set(1500, filldata(100, fillbyte))
    mp.set(1800, filldata(100, fillbyte))
    mp.unfill(unfillpattern=fillbyte)
    assert_list_equal(mp.parts(), [(1000, 100), (1200, 300), (1600, 200), (1900, 100)])


def test_unfill_end():
    mp = MultiPartBuffer()
    fillpattern = randomdata(1)
    mp.set(100, bytearray(100))
    mp2 = mp.copy()
    mp.set(200, fillpattern * 100)
    mp.unfill(unfillpattern=fillpattern)
    assert_equal(mp, mp2)


def test_unfill_start():
    mp = MultiPartBuffer()
    fillpattern = randomdata(1)
    mp.set(200, bytearray(100))
    mp2 = mp.copy()
    mp.set(100, fillpattern * 100)
    mp.unfill(unfillpattern=fillpattern)
    assert_equal(mp, mp2)


def test_unfill_1():
    mp = MultiPartBuffer()
    mp.set(100, bytearray(100))
    mp.set(300, bytearray(100))
    mp2 = mp.copy()
    fillpattern = randomdata(10)
    mp.fill(fillpattern=fillpattern)
    mp.unfill(unfillpattern=fillpattern)
    assert_equal(mp, mp2)


def test_unfill_2():
    mp = MultiPartBuffer()
    mp.set(100, bytearray(100))
    mp.set(300, bytearray(100))
    fillpattern = bytearray.fromhex("DEADBEEF")
    mp2 = mp.copy()
    mp.set(200, fillpattern*25)
    mp.unfill(None, None, fillpattern)
    assert_equal(mp, mp2)


def test_unfill_beyond():
    mp = MultiPartBuffer()
    mp.set(100, bytearray(100))
    mp2 = mp.copy()
    ret = mp.unfill(1000, 100)
    assert_is(mp, ret)
    assert_equal(mp, mp2)


def test_unfill_before():
    mp = MultiPartBuffer()
    mp.set(120, bytearray(90))
    mp2 = mp.copy()
    mp.set(100, bytearray.fromhex("FF")*20)
    ret = mp.unfill(90, 100)
    assert_is(mp, ret)
    assert_equal(mp, mp2)


def test_unfill_3():
    mp = MultiPartBuffer()
    fillpattern = bytearray.fromhex("A1")*10
    testdata1 = randomdata(50)
    testdata2 = randomdata(50)
    mp.set(100, testdata1)
    mp.set(550, testdata2)
    mp2 = mp.copy()
    mp.set(150, fillpattern*5)
    mp.set(500, fillpattern*5)
    ret = mp.unfill(unfillpattern=fillpattern, mingapsize=10)
    assert_is(mp, ret)
    assert_equal(mp, mp2)


def test_loadbinfile():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    with open(filename, "wb") as fh:
        fh.write(testdata)

    mp = MultiPartBuffer()
    mp.loadbinfile(filename)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer()
    mp.loadbinfile(filename, address=0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer()
    mp.loadbinfile(filename, address=0x1000, size=512)
    yield assert_equal, mp.start(), 0x1000
    yield assert_sequence_equal, mp.get(None, None), testdata[0:512]

    mp = MultiPartBuffer()
    mp.loadbinfile(filename, offset=100)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata[100:]


def test_loadbinfh():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    with open(filename, "wb") as fh:
        fh.write(testdata)

    mp = MultiPartBuffer()
    with open(filename, "rb") as fh:
        mp.loadbinfh(fh)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer()
    with open(filename, "rb") as fh:
        mp.loadbinfh(fh, address=0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer()
    with open(filename, "rb") as fh:
        mp.loadbinfh(fh, address=0x1000, size=512)
    yield assert_equal, mp.start(), 0x1000
    yield assert_sequence_equal, mp.get(None, None), testdata[0:512]

    mp = MultiPartBuffer()
    with open(filename, "rb") as fh:
        mp.loadbinfh(fh, offset=100)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata[100:]


def test_frombinfile():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    with open(filename, "wb") as fh:
        fh.write(testdata)

    mp = MultiPartBuffer.frombinfile(filename)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer.frombinfile(filename, address=0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer.frombinfile(filename, address=0x1000, size=512)
    yield assert_equal, mp.start(), 0x1000
    yield assert_sequence_equal, mp.get(None, None), testdata[0:512]

    mp = MultiPartBuffer.frombinfile(filename, offset=100)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata[100:]


def test_frombinfh():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    with open(filename, "wb") as fh:
        fh.write(testdata)

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.frombinfh(fh)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.frombinfh(fh, address=0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_sequence_equal, mp.get(None, None), testdata

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.frombinfh(fh, address=0x1000, size=512)
    yield assert_equal, mp.start(), 0x1000
    yield assert_sequence_equal, mp.get(None, None), testdata[0:512]

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.frombinfh(fh, offset=100)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata[100:]


def test_fromfile_1():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    with open(filename, "wb") as fh:
        fh.write(testdata)

    mp = MultiPartBuffer.fromfile(filename)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer.fromfile(filename, address=0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer.fromfile(filename, address=0x1000, size=512)
    yield assert_equal, mp.start(), 0x1000
    yield assert_sequence_equal, mp.get(None, None), testdata[0:512]

    mp = MultiPartBuffer.fromfile(filename, offset=100)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata[100:]


def test_fromfile_2():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    with open(filename, "wb") as fh:
        fh.write(testdata)

    mp = MultiPartBuffer.fromfile(filename, 'bin')
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer.fromfile(filename, 'bin', address=0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_sequence_equal, mp.get(None, None), testdata

    mp = MultiPartBuffer.fromfile(filename, 'bin', address=0x1000, size=512)
    yield assert_equal, mp.start(), 0x1000
    yield assert_sequence_equal, mp.get(None, None), testdata[0:512]

    mp = MultiPartBuffer.fromfile(filename, 'bin', offset=100)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata[100:]


@raises(ValueError)
def test_fromfile_failure():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1)
    with open(filename, "wb") as fh:
        fh.write(testdata)
    MultiPartBuffer.fromfile(filename, 'invalid')


def test_fromfh_1():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    with open(filename, "wb") as fh:
        fh.write(testdata)

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.fromfh(fh)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.fromfh(fh, address=0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_sequence_equal, mp.get(None, None), testdata

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.fromfh(fh, address=0x1000, size=512)
    yield assert_equal, mp.start(), 0x1000
    yield assert_sequence_equal, mp.get(None, None), testdata[0:512]

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.fromfh(fh, offset=100)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata[100:]


def test_fromfh_2():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    with open(filename, "wb") as fh:
        fh.write(testdata)

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.fromfh(fh, 'bin')
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.fromfh(fh, 'bin', address=0x100)
    yield assert_equal, mp.start(), 0x100
    yield assert_sequence_equal, mp.get(None, None), testdata

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.fromfh(fh, 'bin', address=0x1000, size=512)
    yield assert_equal, mp.start(), 0x1000
    yield assert_sequence_equal, mp.get(None, None), testdata[0:512]

    with open(filename, "rb") as fh:
        mp = MultiPartBuffer.fromfh(fh, 'bin', offset=100)
    yield assert_equal, mp.start(), 0
    yield assert_sequence_equal, mp.get(None, None), testdata[100:]


@raises(ValueError)
def test_fromfh_failure():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1)
    with open(filename, "wb") as fh:
        fh.write(testdata)

    with open(filename, "rb") as fh:
        MultiPartBuffer.fromfh(fh, 'invalid')


def test_add_mp():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    mp1 = MultiPartBuffer().set(0x0000, testdata1)
    mp2 = MultiPartBuffer().set(0x1000, testdata2)
    mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
    mp1.add(mp2)
    assert_equal(mp1, mpb)


def test_add_mp_nooverwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mp2 = MultiPartBuffer().set(0x80, testdata2)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
    mp1.add(mp2, overwrite=False)
    assert_equal(mp1, mpb)


def test_add_mp_overwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mp2 = MultiPartBuffer().set(0x80, testdata2)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
    mp1.add(mp2, overwrite=True)
    assert_equal(mp1, mpb)


def test_add_dict_byte():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testdict = {n: byte for n, byte in enumerate(testdata2, start=0x1000)}
    mp1 = MultiPartBuffer().set(0x0000, testdata1)
    mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
    mp1.add(testdict)
    assert_equal(mp1, mpb)


def test_add_dict_byte_overwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testdict = {n: byte for n, byte in enumerate(testdata2, start=0x80)}
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
    mp1.add(testdict, overwrite=True)
    assert_equal(mp1, mpb)


def test_add_dict_byte_nooverwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testdict = {n: byte for n, byte in enumerate(testdata2, start=0x80)}
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
    mp1.add(testdict, overwrite=False)
    assert_equal(mp1, mpb)


def test_add_dict_buffer():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testdict = {(0x1000+n): testdata2[n:n+0x10] for n in range(0, 0x100, 0x10)}
    mp1 = MultiPartBuffer().set(0x0000, testdata1)
    mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
    mp1.add(testdict)
    assert_equal(mp1, mpb)


def test_add_dict_buffer_overwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testdict = {(0x80+n): testdata2[n:n+0x10] for n in range(0, 0x100, 0x10)}
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
    mp1.add(testdict, overwrite=True)
    assert_equal(mp1, mpb)


def test_add_dict_buffer_nooverwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testdict = {(0x80+n): [b for b in testdata2[n:n+0x10]] for n in range(0, 0x100, 0x10)}
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
    mp1.add(testdict, overwrite=False)
    assert_equal(mp1, mpb)


def test_add_list_byte():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testlist = [(n, byte) for n, byte in enumerate(testdata2, start=0x1000)]
    mp1 = MultiPartBuffer().set(0x0000, testdata1)
    mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
    mp1.add(testlist)
    assert_equal(mp1, mpb)


def test_add_list_byte_overwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testlist = [(n, byte) for n, byte in enumerate(testdata2, start=0x80)]
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
    mp1.add(testlist, overwrite=True)
    assert_equal(mp1, mpb)


def test_add_list_byte_nooverwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testlist = [(n, byte) for n, byte in enumerate(testdata2, start=0x80)]
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
    mp1.add(testlist, overwrite=False)
    assert_equal(mp1, mpb)


def test_add_list_buffer():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testlist = [((0x1000+n), testdata2[n:n+0x10]) for n in range(0, 0x100, 0x10)]
    mp1 = MultiPartBuffer().set(0x0000, testdata1)
    mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
    mp1.add(testlist)
    assert_equal(mp1, mpb)


def test_add_list_buffer_overwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testlist = [((0x80+n), testdata2[n:n+0x10]) for n in range(0, 0x100, 0x10)]
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
    mp1.add(testlist, overwrite=True)
    assert_equal(mp1, mpb)


def test_add_list_buffer_nooverwrite():
    testdata1 = randomdata(0x100)
    testdata2 = randomdata(0x100)
    testlist = [((0x80+n), [b for b in testdata2[n:n+0x10]]) for n in range(0, 0x100, 0x10)]
    mp1 = MultiPartBuffer().set(0x00, testdata1)
    mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
    mp1.add(testlist, overwrite=False)
    assert_equal(mp1, mpb)


@raises(TypeError)
def test_add_failure():
    mp = MultiPartBuffer()
    mp.add(set(range(0, 10)))


def test_fillfront_0():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer().set(0x20, testdata)
    ret = mp.fillfront()
    assert_is(mp, ret)
    assert_equal(mp.start(), 0)
    assert_sequence_equal(mp.get(None, None), (bytearray.fromhex("FF"*0x20)) + testdata)


def test_fillfront_1():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer().set(0x20, testdata)
    ret = mp.fillfront(fillpattern=0xA1)
    assert_is(mp, ret)
    assert_equal(mp.start(), 0)
    assert_sequence_equal(mp.get(None, None), (bytearray.fromhex("A1"*0x20)) + testdata)


def test_fillfront_2():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer().set(0x20, testdata)
    ret = mp.fillfront(0x20, 0xAA)
    assert_is(mp, ret)
    assert_equal(mp.start(), 0x20)
    assert_sequence_equal(mp.get(None, None), testdata)


def test_fillfront_3():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer().set(0x20, testdata)
    ret = mp.fillfront(0x30, 0xAA)
    assert_is(mp, ret)
    assert_equal(mp.start(), 0x20)
    assert_sequence_equal(mp.get(None, None), testdata)


def test_fillfront_4():
    mp = MultiPartBuffer()
    ret = mp.fillfront()
    assert_is(mp, ret)
    assert_equal(mp.start(), 0)
    assert_equal(mp.end(), 0)


def test_fillend_1():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer().set(0x20, testdata)
    ret = mp.fillend(0x200)
    assert_is(mp, ret)
    assert_equal(mp.end(), 0x200)
    assert_sequence_equal(mp.get(None, None), testdata + (bytearray.fromhex("FF"*(0x100-0x20))))


def test_fillend_2():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer().set(0x20, testdata)
    ret = mp.fillend(0x200, 0x5A)
    assert_is(mp, ret)
    assert_equal(mp.end(), 0x200)
    assert_sequence_equal(mp.get(None, None), testdata + (bytearray.fromhex("5A"*(0x100-0x20))))


def test_fillend_3():
    testdata = randomdata(0x100)
    mp = MultiPartBuffer().set(0x20, testdata)
    ret = mp.fillend(0x30, 0xAA)
    assert_is(mp, ret)
    assert_equal(mp.start(), 0x20)
    assert_sequence_equal(mp.get(None, None), testdata)


def test_fillend_4():
    mp = MultiPartBuffer()
    ret = mp.fillend(0x100, 0x2E)
    assert_is(mp, ret)
    assert_equal(mp.start(), 0)
    assert_equal(mp.end(), 0x100)
    assert_sequence_equal(mp.get(None, None), (bytearray.fromhex("2E" * 0x100)))


def test_todict():
    testdata = randomdata(100)
    mp = MultiPartBuffer().set(1000, testdata)
    d1 = {n: b for n, b in enumerate(testdata, 1000)}
    d2 = mp.todict()
    assert_equal(d1, d2)


def test_tobinfile_1():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(100, testdata)
    ret = mp.tobinfile(filename)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfile_2():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(1000, testdata)
    ret = mp.tobinfile(filename, address=1000)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfile_3():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(1000, testdata)
    ret = mp.tobinfile(filename, size=1024)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfile_4():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(1000, testdata)
    ret = mp.tobinfile(filename, address=1000, size=1024)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfile_5():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(0, testdata)
    ret = mp.tobinfile(filename, address=-1, size=1024)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfile_6():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(0, testdata)
    ret = mp.tobinfile(filename, address=12000)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(bytearray(), readdata)


def test_tobinfh_1():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(100, testdata)
    with open(filename, "wb") as fh:
        ret = mp.tobinfh(fh)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfh_2():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(1000, testdata)
    with open(filename, "wb") as fh:
        ret = mp.tobinfh(fh, address=1000)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfh_3():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(1000, testdata)
    with open(filename, "wb") as fh:
        ret = mp.tobinfh(fh, size=1024)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfh_4():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(1000, testdata)
    with open(filename, "wb") as fh:
        ret = mp.tobinfh(fh, address=1000, size=1024)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfh_5():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(0, testdata)
    with open(filename, "wb") as fh:
        ret = mp.tobinfh(fh, address=-1, size=1024)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(testdata, readdata)


def test_tobinfh_6():
    dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
    filename = os.path.join(dirname, "testdata.bin")
    testdata = randomdata(1024)
    mp = MultiPartBuffer().set(0, testdata)
    with open(filename, "wb") as fh:
        ret = mp.tobinfh(fh, address=12000)
    assert_is(ret, mp)
    with open(filename, "rb") as fh:
        readdata = fh.read()
    assert_sequence_equal(bytearray(), readdata)


def test_filter_nonpositivesize():
    mp = MultiPartBuffer().set(123, bytearray(456))

    def nevercalled():
        raise Exception
    assert_is(mp, mp.filter(nevercalled, size=0))
    assert_is(mp, mp.filter(nevercalled, size=-1))
    assert_is(mp, mp.filter(nevercalled, address=0, size=0))
    assert_is(mp, mp.filter(nevercalled, address=1000, size=0))


def test_filter_outsiderange():
    mp = MultiPartBuffer().set(123, bytearray(456))

    def nevercalled():
        raise Exception
    assert_is(mp, mp.filter(nevercalled, address=100, size=10))
    assert_is(mp, mp.filter(nevercalled, address=900, size=10))


def test_filter_fill_1():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2)
    filler = bytearray((0xFF,))
    called = 0

    def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
        nonlocal called
        called += 1
        assert_equal(called, 1)
        assert_equal(bufferaddr, 100)
        assert_sequence_equal(buffer, testdata1 + bytearray(filler*100) + testdata2)
        assert_equal(bufferstartindex, 0)
        assert_equal(bufferendindex, 300)

    assert_is(mp, mp.filter(filterfunc, fillpattern=filler))


def test_filter_fill_2():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2)
    filler = bytearray((0xFF,))
    called = 0

    def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
        nonlocal called
        called += 1
        assert_equal(called, 1)
        assert_equal(bufferaddr, 100)
        assert_sequence_equal(buffer, testdata1 + bytearray(filler*100) + testdata2)
        assert_equal(bufferstartindex, 50)
        assert_equal(bufferendindex, 250)
        assert_sequence_equal(buffer[bufferstartindex:bufferendindex],
                              testdata1[50:] + bytearray(filler * 100) + testdata2[:50])

    assert_is(mp, mp.filter(filterfunc, address=150, size=200, fillpattern=filler))


def test_filter_overlap_1():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2)
    filler = bytearray((0xFF,))
    called = 0

    def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
        nonlocal called
        called += 1
        assert_equal(called, 1)
        assert_equal(bufferaddr, 100)
        assert_sequence_equal(buffer, testdata1)
        assert_equal(bufferstartindex, 50)
        assert_equal(bufferendindex, 100)
        assert_sequence_equal(buffer[bufferstartindex:bufferendindex], testdata1[50:])

    assert_is(mp, mp.filter(filterfunc, address=150, size=100))


def test_filter_overlap_2():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2)
    called = 0

    def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
        nonlocal called
        called += 1
        assert_less_equal(called, 2)
        if called == 1:
            assert_equal(bufferaddr, 100)
            assert_sequence_equal(buffer, testdata1)
            assert_equal(bufferstartindex, 50)
            assert_equal(bufferendindex, 100)
            assert_sequence_equal(buffer[bufferstartindex:bufferendindex], testdata1[50:])
        else:
            assert_equal(bufferaddr, 300)
            assert_sequence_equal(buffer, testdata2)
            assert_equal(bufferstartindex, 0)
            assert_equal(bufferendindex, 50)
            assert_sequence_equal(buffer[bufferstartindex:bufferendindex], testdata2[:50])

    assert_is(mp, mp.filter(filterfunc, address=150, size=200))


def test_filter_overlap_3():
    testdata1 = randomdata(100)
    testdata2 = randomdata(100)
    mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2).set(500, bytearray(100))
    called = 0

    def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
        nonlocal called
        called += 1
        assert_less_equal(called, 2)
        if called == 1:
            assert_equal(bufferaddr, 100)
            assert_sequence_equal(buffer, testdata1)
            assert_equal(bufferstartindex, 50)
            assert_equal(bufferendindex, 100)
            assert_sequence_equal(buffer[bufferstartindex:bufferendindex], testdata1[50:])
        else:
            assert_equal(bufferaddr, 300)
            assert_sequence_equal(buffer, testdata2)
            assert_equal(bufferstartindex, 0)
            assert_equal(bufferendindex, 100)
            assert_sequence_equal(buffer[bufferstartindex:bufferendindex], testdata2)

    assert_is(mp, mp.filter(filterfunc, address=150, size=300))
