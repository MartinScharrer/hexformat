""" Unit tests for multipartbuffer module.

  License::
  
    Copyright (C) 2015-2022  Martin Scharrer <martin.scharrer@web.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
from hexformat.fillpattern import RandomContent
from hexformat.intelhex import IntelHex
from hexformat.multipartbuffer import MultiPartBuffer
import unittest
import tempfile
import os
import random
import shutil

sys.path.append('..')

callcount = 0
dirname = ""
filename = ""


def randomdata(length):
    # noinspection PyUnusedLocal
    return bytearray((random.randint(0, 255) for n in range(0, length)))


def filldata(length, data=0xFF):
    return bytearray((data,)) * length


class MyExept(ValueError):
    pass


class TestMultiPartBuffer(unittest.TestCase):

    def setUp(self):
        global dirname
        global filename
        dirname = tempfile.mkdtemp(prefix="test_multipartbuffer_")
        # sys.stderr.write("Tempdir: {:s}\n".format(dirname))
        filename = os.path.join(dirname, "testdata.bin")

    def tearDown(self):
        # noinspection PyBroadException
        try:
            shutil.rmtree(dirname)
        except OSError:
            pass

    # noinspection PyProtectedMember
    def test1(self):
        m = MultiPartBuffer()
        self.assertEqual(m._parts, [])
        assert m.set(0, bytearray(10)) is m  # returns self
        self.assertEqual(m._parts, [[0, bytearray(bytearray(10))]])
        assert m.fill(0x100, 0x8, [0xAA, 0xBB, 0xCC, 0xDD]) is m  # returns self
        self.assertEqual(m.get(0x100, 0x8), bytearray([0xAA, 0xBB, 0xCC, 0xDD, 0xAA, 0xBB, 0xCC, 0xDD]))
        assert m.fill(0x200, 0x8) is m  # returns self
        self.assertEqual(m.get(0x200, 0x8), bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]))
        self.assertEqual(m.delete(0x100, 0x4), m)  # returns self
        self.assertEqual(len(m.parts()), 3)
        self.assertEqual(m._parts[1][0], 0x104)

    # noinspection PyProtectedMember
    def test2(self):
        m = MultiPartBuffer()
        m.fill(0, 0x1000, RandomContent())
        m.fill(0x1000, 0x1000, RandomContent())
        m.fill(0x10000, 0x10000, RandomContent())
        assert m.tobinfile("test2.bin") is m  # retuns self
        n = MultiPartBuffer.frombinfile("test2.bin")
        m.fillgaps()
        self.assertEqual(m, n)
        self.assertEqual(m._parts, n._parts)
        ih = IntelHex.frombinfile("test2.bin")
        self.assertEqual(ih._parts, m._parts)
        assert ih.toihexfile("test2.hex") is ih  # returns self
        ih2 = IntelHex.fromihexfile("test2.hex")
        self.assertEqual(ih, ih2)

    # noinspection PyProtectedMember
    def test_multipartbuffer_init(self):
        """Init must set _parts to an empty list"""
        self.assertEqual(MultiPartBuffer()._parts, list())

    def test_multipartbuffer_repr(self):
        """Instance shall return suitable represenation"""
        assert isinstance(MultiPartBuffer().__repr__(), str)  # check for string, not for content

    def test_multipartbuffer_eq(self):
        """Instance must be logical equal to other instance with equal data content"""
        m1 = MultiPartBuffer()
        m2 = MultiPartBuffer()
        self.assertEqual(m1, m2)
        m1.fill(0x100, 0x100, bytearray(b"Test"))
        m2.fill(0x100, 0x100, bytearray(b"Test"))
        self.assertEqual(m1, m2)
        m1.fill(0x0, 0x100, bytearray(b"Test"))
        m2.fill(0x0, 0x100, bytearray(b"Test"))
        self.assertEqual(m1, m2)
        m1.fillgaps()
        m2.fillgaps()
        self.assertEqual(m1, m2)

    def test_create(self):
        data = [
            bytearray.fromhex("0123456789"),
            bytearray.fromhex("DEADBEEF"),
            bytearray.fromhex("FEEDAFFE"),
        ]
        mp = MultiPartBuffer()
        mp.set(0x200, data[0])
        self.assertListEqual(mp.parts(), [(0x200, len(data[0])), ])
        mp.set(0x100, data[1])
        self.assertListEqual(mp.parts(), [(0x100, len(data[1])), (0x200, len(data[0]))])
        mp.set(0x300, data[2])
        self.assertListEqual(mp.parts(), [(0x100, len(data[1])), (0x200, len(data[0])), (0x300, len(data[2]))])

    # noinspection PyProtectedMember
    def test_insert_borders(self):
        data = [
            randomdata(100),
            randomdata(100),
            randomdata(100),
        ]
        mp = MultiPartBuffer()
        mp.set(1000, data[0])
        self.assertListEqual(mp._parts, [[1000, data[0]]])
        mp.set(900, data[1])
        self.assertListEqual(mp._parts, [[900, data[1] + data[0]]])
        mp.set(1100, data[2])
        self.assertListEqual(mp._parts, [[900, data[1] + data[0] + data[2]]])

    # noinspection PyProtectedMember
    def test_insert_overlap(self):
        data = [
            randomdata(100),
            randomdata(100),
            randomdata(100),
        ]
        mp = MultiPartBuffer()
        mp.set(1000, data[0])
        self.assertListEqual(mp._parts, [[1000, data[0]]])
        mp.set(950, data[1])
        self.assertListEqual(mp._parts, [[950, data[1] + data[0][50:]]])
        mp.set(1080, data[2])
        self.assertListEqual(mp._parts, [[950, data[1] + data[0][50:-20] + data[2]]])

    def test_get_beforedata(self):
        mp = MultiPartBuffer()
        mp.set(1000, bytearray(10))
        self.assertSequenceEqual(mp.get(900, 10, 0xFF), bytearray(b"\xFF" * 10))

    def test_get_betweendata(self):
        mp = MultiPartBuffer()
        mp.set(800, bytearray(10))
        mp.set(1000, bytearray(10))
        self.assertSequenceEqual(mp.get(1100, 10, 0xFF), bytearray(b"\xFF" * 10))

    def test_get_overlapstart(self):
        mp = MultiPartBuffer()
        testdata = randomdata(10)
        mp.set(1000, testdata)
        self.assertSequenceEqual(mp.get(990, 15, 0xFF), bytearray(b"\xFF" * 10) + testdata[0:5])

    def test_get_overlapend(self):
        mp = MultiPartBuffer()
        testdata = randomdata(10)
        mp.set(1000, testdata)
        self.assertSequenceEqual(mp.get(1005, 15, 0xFF), testdata[5:] + bytearray(b"\xFF" * 10))

    def test_get_overlapboth(self):
        mp = MultiPartBuffer()
        testdata = randomdata(10)
        mp.set(1000, testdata)
        self.assertSequenceEqual(mp.get(990, 30, 0xFF), bytearray(b"\xFF" * 10) + testdata + bytearray(b"\xFF" * 10))

    def test_get_3(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer()
        mp.set(1000, testdata)
        self.assertSequenceEqual(mp.get(None, 80), testdata[0:80])

    def test_get_zerosize(self):
        adr = 1000
        length = 100
        end = adr + length
        testdata = randomdata(length)
        mp = MultiPartBuffer()
        mp.set(adr, testdata)
        self.assertSequenceEqual(mp.get(None, 0), bytearray())
        self.assertSequenceEqual(mp.get(adr - 1, 0), bytearray())
        self.assertSequenceEqual(mp.get(adr, 0), bytearray())
        self.assertSequenceEqual(mp.get(adr + 1, 0), bytearray())
        self.assertSequenceEqual(mp.get(adr - 1, 0), bytearray())
        self.assertSequenceEqual(mp.get(end, 0), bytearray())
        self.assertSequenceEqual(mp.get(end + 1, 0), bytearray())
        self.assertSequenceEqual(mp.get(end - 1, 0), bytearray())
        self.assertSequenceEqual(mp.get(end - 2, 0), bytearray())

    def test_setint(self):
        mp = MultiPartBuffer()
        mp.setint(address=0x100, intvalue=0xDEADBEEF, datasize=4, byteorder='big', signed=False, overwrite=True)
        self.assertSequenceEqual(mp.get(None, None), bytearray.fromhex("DEADBEEF"))
        mp.setint(address=0x100, intvalue=0xFEEDAFFE, datasize=4, byteorder='big', signed=False, overwrite=False)
        self.assertSequenceEqual(mp.get(None, None), bytearray.fromhex("DEADBEEF"))

    def test_crop(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer()
        mp.set(1000, testdata)
        mp.crop(1010, 80)
        self.assertSequenceEqual(mp.get(None, None), testdata[10:-10])
        mp.crop(1020)
        self.assertSequenceEqual(mp.get(None, None), testdata[20:-10])
        mp.crop(None)
        self.assertSequenceEqual(mp.get(None, None), testdata[20:-10])

    def test_extract(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer()
        mp.set(1000, testdata)
        mp2 = mp.extract(1010, 80)
        self.assertSequenceEqual(mp.get(None, None), testdata)
        self.assertSequenceEqual(mp2.get(None, None), testdata[10:-10])
        mp3 = mp.extract(1020, None, False)
        self.assertSequenceEqual(mp.get(None, None), testdata[0:20])
        self.assertSequenceEqual(mp3.get(None, None), testdata[20:])

    def test_includesgaps(self):
        mp = MultiPartBuffer()
        mp.set(1000, bytearray(100))
        self.assertEqual(False, mp.includesgaps(None, None))
        mp.set(2000, bytearray(100))
        self.assertEqual(True, mp.includesgaps(999, 2))
        self.assertEqual(True, mp.includesgaps(990, 3000))
        self.assertEqual(True, mp.includesgaps(1099, 2))
        self.assertEqual(True, mp.includesgaps(1000, 1100))
        self.assertEqual(True, mp.includesgaps(2099, 2))
        self.assertEqual(False, mp.includesgaps(1010, 10))
        self.assertEqual(False, mp.includesgaps(2000, 100))

    def test_includesgaps_empty(self):
        mp = MultiPartBuffer()
        self.assertEqual(False, mp.includesgaps(0, 0))
        self.assertEqual(True, mp.includesgaps(1, 0))
        self.assertEqual(True, mp.includesgaps(0, 1))

    def test_offset(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer()
        mp.set(1000, testdata)
        mp.offset(10)
        self.assertSequenceEqual(mp.get(1010, 100), testdata)
        self.assertListEqual(mp.parts(), [(1010, 100), ])
        mp.offset(-100)
        self.assertSequenceEqual(mp.get(910, 100), testdata)
        self.assertListEqual(mp.parts(), [(910, 100), ])
        mp.offset(None)
        self.assertSequenceEqual(mp.get(0, 100), testdata)
        self.assertListEqual(mp.parts(), [(0, 100), ])

    def test_offset_error(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer()
        mp.set(100, testdata)
        with self.assertRaises(ValueError):
            mp.offset(-200)

    def test_getitem(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer()
        mp.set(0x1000, testdata)
        yield self.assertEqual, mp[0x1000], testdata[0]
        yield self.assertEqual, mp[0x1000], mp.get(0x1000, 0x1)[0]
        yield self.assertEqual, len(mp[0x1000:0x1100]), 0x100
        yield self.assertSequenceEqual, mp[0x1000:0x1100], mp.get(0x1000, 0x100)
        yield self.assertSequenceEqual, mp[0x1000:0x1100], testdata

    def test_getitem_step(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer()
        mp.set(0x1000, testdata)
        with self.assertRaises(IndexError):
            return mp[0x1000:0x1004:2]

    def test_start(self):
        mp = MultiPartBuffer()
        yield self.assertEqual, mp.start(), 0
        mp.set(0x1000, bytearray(10))
        yield self.assertEqual, mp.start(), 0x1000
        mp.set(0x500, bytearray(10))
        yield self.assertEqual, mp.start(), 0x500
        mp.set(0x1500, bytearray(10))
        yield self.assertEqual, mp.start(), 0x500

    def test_end(self):
        mp = MultiPartBuffer()
        yield self.assertEqual, 0, mp.end()
        adr = random.randint(0, 2 ** 32 - 1)
        size = random.randint(0, 2 ** 16 - 1)
        mp.set(adr, bytearray(size))
        yield self.assertEqual, adr + size, mp.end()

    def test_relocate_1(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer()
        mp.set(0x200, testdata)
        mp.relocate(0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertEqual, mp.range(), (0x100, 0x100)
        yield self.assertSequenceEqual, mp.get(0x100, 0x100), testdata

    def test_relocate_2(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer()
        mp.set(0x200, testdata)
        mp.relocate(0x100, 0x200, 0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertEqual, mp.range(), (0x100, 0x100)
        yield self.assertSequenceEqual, mp.get(0x100, 0x100), testdata

    def test_relocate_3(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer()
        mp.set(0x200, testdata)
        mp.relocate(0x100, 0x220, 0x10)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertEqual, mp.range(), (0x100, 0x200)
        yield self.assertListEqual, mp.parts(), [(0x100, 0x10), (0x200, 0x20), (0x230, 0x100 - 0x30)]
        yield self.assertSequenceEqual, mp.get(0x100, 0x10), testdata[0x20:0x30]
        yield self.assertSequenceEqual, mp.get(0x200, 0x20), testdata[0x00:0x20]
        yield self.assertSequenceEqual, mp.get(0x230, None), testdata[0x30:]

    def test_relocate_4(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer()
        mp.set(0x100, testdata)
        mp.relocate(0x100, 0x1F0, 0x10, False)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertEqual, mp.range(), (0x100, 0xF0)
        yield self.assertListEqual, mp.parts(), [(0x100, 0xF0), ]
        yield self.assertSequenceEqual, mp.get(0x100, 0xF0), testdata[:0xF0]
        yield self.assertSequenceEqual, mp.get(None, None), testdata[:0xF0]

    def test_delete(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer()
        mp.set(0x100, testdata)
        mp.delete(0xF0, 0x20)
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0x10:]
        mp.delete(0x1F0, 0x20)
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0x10:-0x10]
        mp.delete(0x150, 0x10)
        yield self.assertListEqual, mp.parts(), [(0x110, 0x40), (0x160, 0x90)]

    def test_delete_all(self):
        testdata = bytearray(100)
        mp = MultiPartBuffer()
        mp.set(10000, testdata)
        mp.delete(9999, 102)
        yield self.assertListEqual, mp.parts(), []

    # noinspection PyProtectedMember
    def test_delete_2(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp = MultiPartBuffer()
        mp.set(200, testdata1)
        mp.set(400, testdata2)
        mp.delete(100, 350)
        yield self.assertListEqual, mp._parts, [[450, testdata2[50:]], ]

    def test_delete_overlap(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer()
        mp.set(0x100, testdata)
        mp.delete(0xF0, 0x20)
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0x10:]
        mp.delete(0x1F0, 0x20)
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0x10:-0x10]
        mp.delete(0x150, 0x10)
        yield self.assertListEqual, mp.parts(), [(0x110, 0x40), (0x160, 0x90)]

    # noinspection PyProtectedMember
    def test_filler_1(self):
        mp = MultiPartBuffer()
        mp._padding = 0xAA
        yield self.assertSequenceEqual, b'\x5A' * 10, mp._filler(10, 0x5A)
        yield self.assertSequenceEqual, b'\xAA' * 20, mp._filler(20, None)

    # noinspection PyProtectedMember
    def test_filler_2(self):
        mp = MultiPartBuffer()
        with self.assertRaises(MyExept):
            return mp._filler(1, MyExept)

    # noinspection PyProtectedMember
    def test_copy(self):
        mp = MultiPartBuffer()
        for n in range(0, random.randint(1, 10)):
            adr = random.randint(0, 2 ** 16 - 1)
            size = random.randint(0, 2 ** 16 - 1)
            mp.set(adr, randomdata(size))
        mp2 = mp.copy()
        yield self.assertEqual, mp._parts, mp2._parts
        yield self.assertEqual, mp.__dict__, mp2.__dict__

    # noinspection PyProtectedMember
    def test_loaddict(self):
        mp = MultiPartBuffer()
        mp.loaddict({100: 0xDE, 101: 0xAD, 102: 0xBE, 103: 0xEF, 200: 0x00, 0: 0x11})
        yield self.assertSequenceEqual, mp._parts, [[0, bytearray((0x11,))],
                                                    [100, bytearray.fromhex('DEADBEEF')],
                                                    [200, bytearray((0x00,))]]
        mp.loaddict({100: 0xFF, 101: 0xFF, 102: 0x00, 103: 0xAA, 200: 0xBB, 1: 0x22}, False)
        yield self.assertSequenceEqual, mp._parts, [[0, bytearray((0x11, 0x22))],
                                                    [100, bytearray.fromhex('DEADBEEF')],
                                                    [200, bytearray((0x00,))]]
        testdata = randomdata(210)
        mp.loaddict({n: b for n, b in enumerate(testdata)})
        yield self.assertListEqual, mp._parts, [[0, testdata], ]

    def test_ior(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp1 = MultiPartBuffer().set(100, testdata1)
        mp2 = MultiPartBuffer().set(180, testdata2)
        mp1 |= mp2
        self.assertSequenceEqual(mp1[:], testdata1 + testdata2[20:])

    def test_or(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp1 = MultiPartBuffer().set(100, testdata1)
        mp2 = MultiPartBuffer().set(150, testdata2)
        mp = mp1 | mp2
        self.assertSequenceEqual(mp[:], testdata1 + testdata2[50:])

    def test_iand(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp1 = MultiPartBuffer().set(100, testdata1)
        mp2 = MultiPartBuffer().set(180, testdata2)
        mp1 += mp2
        self.assertSequenceEqual(mp1[:], testdata1[:-20] + testdata2)

    def test_and(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp1 = MultiPartBuffer().set(100, testdata1)
        mp2 = MultiPartBuffer().set(150, testdata2)
        mp = mp1 + mp2
        testdata = testdata1[0:50] + testdata2
        yield self.assertSequenceEqual, mp[:], testdata

    def test_unfill_empty(self):
        mp = MultiPartBuffer()
        self.assertIs(mp.unfill(), mp)
        self.assertListEqual(mp.parts(), [])

    def test_unfill_mingapsize(self):
        mp = MultiPartBuffer()
        mp.set(100, bytearray(100))
        mp.set(210, bytearray(100))
        fillpattern = randomdata(1)
        mp.fill(fillpattern=fillpattern)
        mp2 = mp.copy()
        mp.unfill(unfillpattern=fillpattern, mingapsize=16)
        self.assertEqual(mp, mp2)

    def test_unfill_multiple(self):
        mp = MultiPartBuffer()
        fillbyte = randomdata(1)[0]
        mp.set(1000, bytearray(1000))
        mp.set(1100, filldata(100, fillbyte))
        mp.set(1500, filldata(100, fillbyte))
        mp.set(1800, filldata(100, fillbyte))
        mp.unfill(unfillpattern=fillbyte)
        self.assertListEqual(mp.parts(), [(1000, 100), (1200, 300), (1600, 200), (1900, 100)])

    def test_unfill_end(self):
        mp = MultiPartBuffer()
        fillpattern = randomdata(1)
        mp.set(100, bytearray(100))
        mp2 = mp.copy()
        mp.set(200, fillpattern * 100)
        mp.unfill(unfillpattern=fillpattern)
        self.assertEqual(mp, mp2)

    def test_unfill_start(self):
        mp = MultiPartBuffer()
        fillpattern = randomdata(1)
        mp.set(200, bytearray(100))
        mp2 = mp.copy()
        mp.set(100, fillpattern * 100)
        mp.unfill(unfillpattern=fillpattern)
        self.assertEqual(mp, mp2)

    def test_unfill_1(self):
        mp = MultiPartBuffer()
        mp.set(100, bytearray(100))
        mp.set(300, bytearray(100))
        mp2 = mp.copy()
        fillpattern = randomdata(10)
        mp.fill(fillpattern=fillpattern)
        mp.unfill(unfillpattern=fillpattern)
        self.assertEqual(mp, mp2)

    def test_unfill_2(self):
        mp = MultiPartBuffer()
        mp.set(100, bytearray(100))
        mp.set(300, bytearray(100))
        fillpattern = bytearray.fromhex("DEADBEEF")
        mp2 = mp.copy()
        mp.set(200, fillpattern * 25)
        mp.unfill(None, None, fillpattern)
        self.assertEqual(mp, mp2)

    def test_unfill_beyond(self):
        mp = MultiPartBuffer()
        mp.set(100, bytearray(100))
        mp2 = mp.copy()
        ret = mp.unfill(1000, 100)
        self.assertIs(mp, ret)
        self.assertEqual(mp, mp2)

    def test_unfill_before(self):
        mp = MultiPartBuffer()
        mp.set(120, bytearray(90))
        mp2 = mp.copy()
        mp.set(100, bytearray.fromhex("FF") * 20)
        ret = mp.unfill(90, 100)
        self.assertIs(mp, ret)
        self.assertEqual(mp, mp2)

    def test_unfill_3(self):
        mp = MultiPartBuffer()
        fillpattern = bytearray.fromhex("A1") * 10
        testdata1 = randomdata(50)
        testdata2 = randomdata(50)
        mp.set(100, testdata1)
        mp.set(550, testdata2)
        mp2 = mp.copy()
        mp.set(150, fillpattern * 5)
        mp.set(500, fillpattern * 5)
        ret = mp.unfill(unfillpattern=fillpattern, mingapsize=10)
        self.assertIs(mp, ret)
        self.assertEqual(mp, mp2)

    def test_loadbinfile(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        mp = MultiPartBuffer()
        mp.loadbinfile(filename)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer()
        mp.loadbinfile(filename, address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer()
        mp.loadbinfile(filename, address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        mp = MultiPartBuffer()
        mp.loadbinfile(filename, offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_loadbinfh(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        mp = MultiPartBuffer()
        with open(filename, "rb") as fh:
            mp.loadbinfh(fh)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer()
        with open(filename, "rb") as fh:
            mp.loadbinfh(fh, address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer()
        with open(filename, "rb") as fh:
            mp.loadbinfh(fh, address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        mp = MultiPartBuffer()
        with open(filename, "rb") as fh:
            mp.loadbinfh(fh, offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_frombinfile(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        mp = MultiPartBuffer.frombinfile(filename)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer.frombinfile(filename, address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer.frombinfile(filename, address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        mp = MultiPartBuffer.frombinfile(filename, offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_frombinfh(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.frombinfh(fh)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.frombinfh(fh, address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.frombinfh(fh, address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.frombinfh(fh, offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_fromfile_1(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        mp = MultiPartBuffer.fromfile(filename)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer.fromfile(filename, address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer.fromfile(filename, address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        mp = MultiPartBuffer.fromfile(filename, offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_fromfile_2(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        mp = MultiPartBuffer.fromfile(filename, 'bin')
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer.fromfile(filename, 'bin', address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer.fromfile(filename, 'bin', address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        mp = MultiPartBuffer.fromfile(filename, 'bin', offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_fromfile_failure(self):
        testdata = randomdata(1)
        with open(filename, "wb") as fh:
            fh.write(testdata)
        with self.assertRaises(ValueError):
            MultiPartBuffer.fromfile(filename, 'invalid')

    def test_fromfh_1(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.fromfh(fh)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.fromfh(fh, address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.fromfh(fh, address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.fromfh(fh, offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_fromfh_2(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.fromfh(fh, 'bin')
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.fromfh(fh, 'bin', address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.fromfh(fh, 'bin', address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer.fromfh(fh, 'bin', offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_fromfh_failure(self):
        testdata = randomdata(1)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        with open(filename, "rb") as fh:
            with self.assertRaises(ValueError):
                MultiPartBuffer.fromfh(fh, 'invalid')

    def test_loadfile_1(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        mp = MultiPartBuffer().loadfile(filename)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer().loadfile(filename, address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer().loadfile(filename, address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        mp = MultiPartBuffer().loadfile(filename, offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_loadfile_2(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        mp = MultiPartBuffer().loadfile(filename, 'bin')
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer().loadfile(filename, 'bin', address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        mp = MultiPartBuffer().loadfile(filename, 'bin', address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        mp = MultiPartBuffer().loadfile(filename, 'bin', offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_loadfile_failure(self):
        testdata = randomdata(1)
        with open(filename, "wb") as fh:
            fh.write(testdata)
        with self.assertRaises(ValueError):
            MultiPartBuffer().loadfile(filename, 'invalid')

    def test_loadfh_1(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer().loadfh(fh)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer().loadfh(fh, address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer().loadfh(fh, address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer().loadfh(fh, offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_loadfh_2(self):
        testdata = randomdata(1024)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer().loadfh(fh, 'bin')
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer().loadfh(fh, 'bin', address=0x100)
        yield self.assertEqual, mp.start(), 0x100
        yield self.assertSequenceEqual, mp.get(None, None), testdata

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer().loadfh(fh, 'bin', address=0x1000, size=512)
        yield self.assertEqual, mp.start(), 0x1000
        yield self.assertSequenceEqual, mp.get(None, None), testdata[0:512]

        with open(filename, "rb") as fh:
            mp = MultiPartBuffer().loadfh(fh, 'bin', offset=100)
        yield self.assertEqual, mp.start(), 0
        yield self.assertSequenceEqual, mp.get(None, None), testdata[100:]

    def test_loadfh_failure(self):
        testdata = randomdata(1)
        with open(filename, "wb") as fh:
            fh.write(testdata)

        with open(filename, "rb") as fh:
            with self.assertRaises(ValueError):
                MultiPartBuffer().loadfh(fh, 'invalid')

    def test_add_mp(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        mp1 = MultiPartBuffer().set(0x0000, testdata1)
        mp2 = MultiPartBuffer().set(0x1000, testdata2)
        mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
        mp1.add(mp2)
        self.assertEqual(mp1, mpb)

    def test_add_mp_nooverwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mp2 = MultiPartBuffer().set(0x80, testdata2)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
        mp1.add(mp2, overwrite=False)
        self.assertEqual(mp1, mpb)

    def test_add_mp_overwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mp2 = MultiPartBuffer().set(0x80, testdata2)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
        mp1.add(mp2, overwrite=True)
        self.assertEqual(mp1, mpb)

    def test_add_dict_byte(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testdict = {n: byte for n, byte in enumerate(testdata2, start=0x1000)}
        mp1 = MultiPartBuffer().set(0x0000, testdata1)
        mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
        mp1.add(testdict)
        self.assertEqual(mp1, mpb)

    def test_add_dict_byte_overwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testdict = {n: byte for n, byte in enumerate(testdata2, start=0x80)}
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
        mp1.add(testdict, overwrite=True)
        self.assertEqual(mp1, mpb)

    def test_add_dict_byte_nooverwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testdict = {n: byte for n, byte in enumerate(testdata2, start=0x80)}
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
        mp1.add(testdict, overwrite=False)
        self.assertEqual(mp1, mpb)

    def test_add_dict_buffer(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testdict = {(0x1000 + n): testdata2[n:n + 0x10] for n in range(0, 0x100, 0x10)}
        mp1 = MultiPartBuffer().set(0x0000, testdata1)
        mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
        mp1.add(testdict)
        self.assertEqual(mp1, mpb)

    def test_add_dict_buffer_overwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testdict = {(0x80 + n): testdata2[n:n + 0x10] for n in range(0, 0x100, 0x10)}
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
        mp1.add(testdict, overwrite=True)
        self.assertEqual(mp1, mpb)

    def test_add_dict_buffer_nooverwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testdict = {(0x80 + n): [b for b in testdata2[n:n + 0x10]] for n in range(0, 0x100, 0x10)}
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
        mp1.add(testdict, overwrite=False)
        self.assertEqual(mp1, mpb)

    def test_add_list_byte(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testlist = [(n, byte) for n, byte in enumerate(testdata2, start=0x1000)]
        mp1 = MultiPartBuffer().set(0x0000, testdata1)
        mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
        mp1.add(testlist)
        self.assertEqual(mp1, mpb)

    def test_add_list_byte_overwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testlist = [(n, byte) for n, byte in enumerate(testdata2, start=0x80)]
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
        mp1.add(testlist, overwrite=True)
        self.assertEqual(mp1, mpb)

    def test_add_list_byte_nooverwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testlist = [(n, byte) for n, byte in enumerate(testdata2, start=0x80)]
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
        mp1.add(testlist, overwrite=False)
        self.assertEqual(mp1, mpb)

    def test_add_list_buffer(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testlist = [((0x1000 + n), testdata2[n:n + 0x10]) for n in range(0, 0x100, 0x10)]
        mp1 = MultiPartBuffer().set(0x0000, testdata1)
        mpb = MultiPartBuffer().set(0x0000, testdata1).set(0x1000, testdata2)
        mp1.add(testlist)
        self.assertEqual(mp1, mpb)

    def test_add_list_buffer_overwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testlist = [((0x80 + n), testdata2[n:n + 0x10]) for n in range(0, 0x100, 0x10)]
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=True)
        mp1.add(testlist, overwrite=True)
        self.assertEqual(mp1, mpb)

    def test_add_list_buffer_nooverwrite(self):
        testdata1 = randomdata(0x100)
        testdata2 = randomdata(0x100)
        testlist = [((0x80 + n), [b for b in testdata2[n:n + 0x10]]) for n in range(0, 0x100, 0x10)]
        mp1 = MultiPartBuffer().set(0x00, testdata1)
        mpb = MultiPartBuffer().set(0x00, testdata1).set(0x80, testdata2, overwrite=False)
        mp1.add(testlist, overwrite=False)
        self.assertEqual(mp1, mpb)

    def test_add_failure(self):
        mp = MultiPartBuffer()
        with self.assertRaises(TypeError):
            mp.add(set(range(0, 10)))

    def test_fillfront_0(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer().set(0x20, testdata)
        ret = mp.fillfront()
        self.assertIs(mp, ret)
        self.assertEqual(mp.start(), 0)
        self.assertSequenceEqual(mp.get(None, None), (bytearray.fromhex("FF" * 0x20)) + testdata)

    def test_fillfront_1(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer().set(0x20, testdata)
        ret = mp.fillfront(fillpattern=0xA1)
        self.assertIs(mp, ret)
        self.assertEqual(mp.start(), 0)
        self.assertSequenceEqual(mp.get(None, None), (bytearray.fromhex("A1" * 0x20)) + testdata)

    def test_fillfront_2(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer().set(0x20, testdata)
        ret = mp.fillfront(0x20, 0xAA)
        self.assertIs(mp, ret)
        self.assertEqual(mp.start(), 0x20)
        self.assertSequenceEqual(mp.get(None, None), testdata)

    def test_fillfront_3(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer().set(0x20, testdata)
        ret = mp.fillfront(0x30, 0xAA)
        self.assertIs(mp, ret)
        self.assertEqual(mp.start(), 0x20)
        self.assertSequenceEqual(mp.get(None, None), testdata)

    def test_fillfront_4(self):
        mp = MultiPartBuffer()
        ret = mp.fillfront()
        self.assertIs(mp, ret)
        self.assertEqual(mp.start(), 0)
        self.assertEqual(mp.end(), 0)

    def test_fillend_1(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer().set(0x20, testdata)
        ret = mp.fillend(0x200)
        self.assertIs(mp, ret)
        self.assertEqual(mp.end(), 0x200)
        self.assertSequenceEqual(mp.get(None, None), testdata + (bytearray.fromhex("FF" * (0x100 - 0x20))))

    def test_fillend_2(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer().set(0x20, testdata)
        ret = mp.fillend(0x200, 0x5A)
        self.assertIs(mp, ret)
        self.assertEqual(mp.end(), 0x200)
        self.assertSequenceEqual(mp.get(None, None), testdata + (bytearray.fromhex("5A" * (0x100 - 0x20))))

    def test_fillend_3(self):
        testdata = randomdata(0x100)
        mp = MultiPartBuffer().set(0x20, testdata)
        ret = mp.fillend(0x30, 0xAA)
        self.assertIs(mp, ret)
        self.assertEqual(mp.start(), 0x20)
        self.assertSequenceEqual(mp.get(None, None), testdata)

    def test_fillend_4(self):
        mp = MultiPartBuffer()
        ret = mp.fillend(0x100, 0x2E)
        self.assertIs(mp, ret)
        self.assertEqual(mp.start(), 0)
        self.assertEqual(mp.end(), 0x100)
        self.assertSequenceEqual(mp.get(None, None), (bytearray.fromhex("2E" * 0x100)))

    def test_todict(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer().set(1000, testdata)
        d1 = {n: b for n, b in enumerate(testdata, 1000)}
        d2 = mp.todict()
        self.assertEqual(d1, d2)

    def test_tobinfile_1(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(100, testdata)
        ret = mp.tobinfile(filename)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfile_2(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(1000, testdata)
        ret = mp.tobinfile(filename, address=1000)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfile_3(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(1000, testdata)
        ret = mp.tobinfile(filename, size=1024)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfile_4(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(1000, testdata)
        ret = mp.tobinfile(filename, address=1000, size=1024)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfile_5(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(0, testdata)
        ret = mp.tobinfile(filename, address=-1, size=1024)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfile_6(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(0, testdata)
        ret = mp.tobinfile(filename, address=12000)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(bytearray(), readdata)

    def test_tobinfh_1(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(100, testdata)
        with open(filename, "wb") as fh:
            ret = mp.tobinfh(fh)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfh_2(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(1000, testdata)
        with open(filename, "wb") as fh:
            ret = mp.tobinfh(fh, address=1000)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfh_3(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(1000, testdata)
        with open(filename, "wb") as fh:
            ret = mp.tobinfh(fh, size=1024)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfh_4(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(1000, testdata)
        with open(filename, "wb") as fh:
            ret = mp.tobinfh(fh, address=1000, size=1024)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfh_5(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(0, testdata)
        with open(filename, "wb") as fh:
            ret = mp.tobinfh(fh, address=-1, size=1024)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(testdata, readdata)

    def test_tobinfh_6(self):
        testdata = randomdata(1024)
        mp = MultiPartBuffer().set(0, testdata)
        with open(filename, "wb") as fh:
            ret = mp.tobinfh(fh, address=12000)
        self.assertIs(ret, mp)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(bytearray(), readdata)

    def test_filter_nonpositivesize(self):
        mp = MultiPartBuffer().set(123, bytearray(456))

        def nevercalled():
            raise Exception

        self.assertIs(mp, mp.filter(nevercalled, size=0))
        self.assertIs(mp, mp.filter(nevercalled, size=-1))
        self.assertIs(mp, mp.filter(nevercalled, address=0, size=0))
        self.assertIs(mp, mp.filter(nevercalled, address=1000, size=0))

    def test_filter_outsiderange(self):
        mp = MultiPartBuffer().set(123, bytearray(456))

        def nevercalled():
            raise Exception

        self.assertIs(mp, mp.filter(nevercalled, address=100, size=10))
        self.assertIs(mp, mp.filter(nevercalled, address=900, size=10))

    def test_filter_fill_1(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2)
        filler = bytearray((0xFF,))
        global callcount
        callcount = 0

        def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
            global callcount
            callcount += 1
            self.assertEqual(callcount, 1)
            self.assertEqual(bufferaddr, 100)
            self.assertSequenceEqual(buffer, testdata1 + bytearray(filler * 100) + testdata2)
            self.assertEqual(bufferstartindex, 0)
            self.assertEqual(bufferendindex, 300)

        self.assertIs(mp, mp.filter(filterfunc, fillpattern=filler))

    def test_filter_fill_2(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2)
        filler = bytearray((0xFF,))
        global callcount
        callcount = 0

        def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
            global callcount
            callcount += 1
            self.assertEqual(callcount, 1)
            self.assertEqual(bufferaddr, 100)
            self.assertSequenceEqual(buffer, testdata1 + bytearray(filler * 100) + testdata2)
            self.assertEqual(bufferstartindex, 50)
            self.assertEqual(bufferendindex, 250)
            self.assertSequenceEqual(buffer[bufferstartindex:bufferendindex],
                                     testdata1[50:] + bytearray(filler * 100) + testdata2[:50])

        self.assertIs(mp, mp.filter(filterfunc, address=150, size=200, fillpattern=filler))

    def test_filter_overlap_1(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2)
        global callcount
        callcount = 0

        def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
            global callcount
            callcount += 1
            self.assertEqual(callcount, 1)
            self.assertEqual(bufferaddr, 100)
            self.assertSequenceEqual(buffer, testdata1)
            self.assertEqual(bufferstartindex, 50)
            self.assertEqual(bufferendindex, 100)
            self.assertSequenceEqual(buffer[bufferstartindex:bufferendindex], testdata1[50:])

        self.assertIs(mp, mp.filter(filterfunc, address=150, size=100))

    def test_filter_overlap_2(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2)
        global callcount
        callcount = 0

        def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
            global callcount
            callcount += 1
            self.assertLessEqual(callcount, 2)
            if callcount == 1:
                self.assertEqual(bufferaddr, 100)
                self.assertSequenceEqual(buffer, testdata1)
                self.assertEqual(bufferstartindex, 50)
                self.assertEqual(bufferendindex, 100)
                self.assertSequenceEqual(buffer[bufferstartindex:bufferendindex], testdata1[50:])
            else:
                self.assertEqual(bufferaddr, 300)
                self.assertSequenceEqual(buffer, testdata2)
                self.assertEqual(bufferstartindex, 0)
                self.assertEqual(bufferendindex, 50)
                self.assertSequenceEqual(buffer[bufferstartindex:bufferendindex], testdata2[:50])

        self.assertIs(mp, mp.filter(filterfunc, address=150, size=200))

    def test_filter_overlap_3(self):
        testdata1 = randomdata(100)
        testdata2 = randomdata(100)
        mp = MultiPartBuffer().set(100, testdata1).set(300, testdata2).set(500, bytearray(100))
        global callcount
        callcount = 0

        def filterfunc(bufferaddr, buffer, bufferstartindex, bufferendindex):
            global callcount
            callcount += 1
            self.assertLessEqual(callcount, 2)
            if callcount == 1:
                self.assertEqual(bufferaddr, 100)
                self.assertSequenceEqual(buffer, testdata1)
                self.assertEqual(bufferstartindex, 50)
                self.assertEqual(bufferendindex, 100)
                self.assertSequenceEqual(buffer[bufferstartindex:bufferendindex], testdata1[50:])
            else:
                self.assertEqual(bufferaddr, 300)
                self.assertSequenceEqual(buffer, testdata2)
                self.assertEqual(bufferstartindex, 0)
                self.assertEqual(bufferendindex, 100)
                self.assertSequenceEqual(buffer[bufferstartindex:bufferendindex], testdata2)

        self.assertIs(mp, mp.filter(filterfunc, address=150, size=300))

    def test_tofile_failure(self):
        testdata = randomdata(1)
        mp = MultiPartBuffer().set(0, testdata)
        with self.assertRaises(ValueError):
            mp.tofile(filename, 'invalid')

    def test_tofh_failure(self):
        testdata = randomdata(1)
        mp = MultiPartBuffer().set(0, testdata)
        with open(filename, "wb") as fh:
            with self.assertRaises(ValueError):
                mp.tofh(fh, 'invalid')

    def test_tofh(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer().set(0, testdata)
        with open(filename, "wb") as fh:
            mp.tofh(fh)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(readdata, testdata)

    def test_tofh_bin(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer().set(0, testdata)
        with open(filename, "wb") as fh:
            mp.tofh(fh, 'bin')
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(readdata, testdata)

    def test_tofile(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer().set(0, testdata)
        mp.tofile(filename)
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(readdata, testdata)

    def test_tofile_bin(self):
        testdata = randomdata(100)
        mp = MultiPartBuffer().set(0, testdata)
        mp.tofile(filename, 'bin')
        with open(filename, "rb") as fh:
            readdata = fh.read()
        self.assertSequenceEqual(readdata, testdata)
