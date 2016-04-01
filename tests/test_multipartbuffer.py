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
from nose.tools import assert_equal
from hexformat.multipartbuffer import MultiPartBuffer, Buffer

sys.path.append('..')


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
