"""Test case for base package.

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
from tests import TestCase

from hexformat.intelhex import IntelHex
from hexformat.srecord import SRecord


class FakeFileHandle(list):
    def write(self, line):
        self.append(line)


class TestBase(TestCase):

    def test_settings_1(self):
        srec = SRecord(
            startaddress=0x123,
            addresslength=4,
            bytesperline=32,
            header=b"Bla",
            write_number_of_records=True,
        )
        self.assertEqual(srec.startaddress, 0x123)
        self.assertEqual(srec.addresslength, 4)
        self.assertEqual(srec.bytesperline, 32)
        self.assertEqual(srec.header, b"Bla")
        self.assertEqual(srec.write_number_of_records, True)

    def test_settings_2(self):
        srec = SRecord()
        srec.settings(
            startaddress=0x2345,
            addresslength=2,
            bytesperline=16,
            header=b"Test it",
            write_number_of_records=False,
        )
        self.assertEqual(srec.startaddress, 0x2345)
        self.assertEqual(srec.addresslength, 2)
        self.assertEqual(srec.bytesperline, 16)
        self.assertSequenceEqual(srec.header, b"Test it")
        self.assertEqual(srec.write_number_of_records, False)

    def test_settings_3(self):
        with self.assertRaises(AttributeError):
            SRecord(
                startaddress=0x123,
                addresslength=4,
                invalidsetting=32,
                header=b"Bla",
                write_number_of_records=True,
            )

    def test_settings_4(self):
        srec = SRecord()
        with self.assertRaises(AttributeError):
            srec.settings(
                addresslength=2,
                bytesperline=16,
                header=b"Test it",
                write_number_of_records=False,
                invalid=0x2345,
            )

    def test_settings_tofh(self):
        srec = SRecord(header=b"\xAA\xBB\xCC\xDD")
        fh = FakeFileHandle()
        srec.set(0x0, b"\x01\x23\x45\x67\x89\xAB\xCD\xEF")
        srec.tosrecfh(fh, bytesperline=4)
        testdata = ['S0070000AABBCCDDEA\n', 'S10700000123456728\n', 'S107000489ABCDEF04\n', 'S9030000FC\n']
        self.assertListEqual(testdata, fh)

    # noinspection PyProtectedMember
    def test_fromother_1(self):
        srec = SRecord()
        srec.set(0, bytearray.fromhex("0123456789"))
        srec.startaddress = 0x4
        ihex = IntelHex.fromother(srec)
        self.assertEqual(srec._parts, ihex._parts)

    # noinspection PyProtectedMember
    def test_fromother_2(self):
        srec = SRecord()
        srec.set(0, bytearray.fromhex("0123456789"))
        srec.startaddress = 0x4
        ihex = IntelHex.fromother(srec, True)
        self.assertEqual(srec._parts, ihex._parts)
        self.assertIs(srec._parts[0][1], ihex._parts[0][1])

    def test_fromother_3(self):
        with self.assertRaises(TypeError):
            SRecord.fromother({0x100: 0xDE, 0x101: 0xAD, 0x102: 0xBE, 0x103: 0xEF, 0x200: 0xFF})
