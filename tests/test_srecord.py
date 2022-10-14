""" Unit tests for SRecord class.

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
from tests import TestCaseWithTempfile, randbytes, randint, randdict, patch, skipunlessslow
from hexformat.base import EncodeError, DecodeError
from hexformat.srecord import SRecord
import sys


class FakeFileHandle(list):
    def write(self, line):
        self.append(line)

    def readline(self):
        try:
            return self.pop(0)
        except IndexError:
            return ''


class TestSRecord(TestCaseWithTempfile):

    # noinspection PyProtectedMember
    def test_startaddress_getter(self):
        srec = SRecord()
        for n in (0, 1, 2 ** 16 - 1, 2 ** 16, 2 ** 16 + 1, 2 ** 24 - 1, 2 ** 24, 2 ** 24 + 1, 2 ** 32 - 2, 2 ** 32 - 1):
            srec._startaddress = n
            self.assertEqual(srec._startaddress, n)
            self.assertEqual(srec._startaddress, srec.startaddress)
            r = randint(0, 2 ** 32 - 1)
            srec._startaddress = r
            self.assertEqual(srec._startaddress, r)
            self.assertEqual(srec._startaddress, srec.startaddress)

    # noinspection PyProtectedMember
    def test_startaddress_setter(self):
        srec = SRecord()
        for n in (0, 1, 2 ** 16 - 1, 2 ** 16, 2 ** 16 + 1, 2 ** 24 - 1, 2 ** 24, 2 ** 24 + 1, 2 ** 32 - 2, 2 ** 32 - 1):
            srec.startaddress = n
            self.assertEqual(n, srec.startaddress)
            self.assertEqual(srec._startaddress, srec.startaddress)
            r = randint(0, 2 ** 32 - 1)
            srec.startaddress = r
            self.assertEqual(r, srec.startaddress)
            self.assertEqual(srec._startaddress, srec.startaddress)

    # noinspection PyProtectedMember
    def test_startaddress_setter_none(self):
        srec = SRecord()
        srec.startaddress = None
        self.assertIs(srec.startaddress, None)
        self.assertIs(srec.startaddress, srec._startaddress)

    def test_startaddress_setter_invalid(self):
        srec = SRecord()
        with self.assertRaises(ValueError):
            srec.startaddress = -1

    def test_startaddress_setter_invalid_2(self):
        srec = SRecord()
        with self.assertRaises(ValueError):
            srec.startaddress = 2 ** 32

    def test_startaddress_setter_invalid_3(self):
        srec = SRecord()
        with self.assertRaises((ValueError, TypeError)):
            srec.startaddress = "invalid"

    def test_startaddress_setter_invalid_4(self):
        srec = SRecord()
        with self.assertRaises(TypeError):
            srec.startaddress = dict()

    # noinspection PyProtectedMember
    def test_addresslength_getter(self):
        srec = SRecord()
        for n in (0, 1, 2 ** 16 - 1, 2 ** 16, 2 ** 16 + 1, 2 ** 24 - 1, 2 ** 24, 2 ** 24 + 1, 2 ** 32 - 2, 2 ** 32 - 1):
            with self.subTest(n):
                srec._addresslength = n
                self.assertEqual(srec._addresslength, n)
                self.assertEqual(srec._addresslength, srec.addresslength)
                r = randint(0, 2 ** 32 - 1)
                srec._addresslength = r
                self.assertEqual(srec._addresslength, r)
                self.assertEqual(srec._addresslength, srec.addresslength)

    # noinspection PyProtectedMember
    def test_addresslength_setter(self):
        srec = SRecord()
        for n in (2, 3, 4):
            with self.subTest(n):
                srec.addresslength = n
                self.assertEqual(n, srec.addresslength)
                self.assertEqual(srec._addresslength, srec.addresslength)

    # noinspection PyProtectedMember
    def test_addresslength_setter_none(self):
        srec = SRecord()
        srec.addresslength = None
        self.assertIs(srec.addresslength, None)
        self.assertIs(srec.addresslength, srec._addresslength)

    def test_addresslength_setter_invalid(self):
        srec = SRecord()
        with self.assertRaises(ValueError):
            srec.addresslength = 1

    def test_addresslength_setter_invalid_2(self):
        srec = SRecord()
        with self.assertRaises(ValueError):
            srec.addresslength = 5

    def test_addresslength_setter_invalid_3(self):
        srec = SRecord()
        with self.assertRaises((ValueError, TypeError)):
            srec.addresslength = "invalid"

    def test_addresslength_setter_invalid_4(self):
        srec = SRecord()
        with self.assertRaises(TypeError):
            srec.addresslength = dict()

    # noinspection PyProtectedMember
    def test_bytesperline_getter(self):
        srec = SRecord()
        for n in range(1, 254):
            with self.subTest(n):
                srec._bytesperline = n
                self.assertEqual(srec._bytesperline, n)
                self.assertEqual(srec._bytesperline, srec.bytesperline)

    # noinspection PyProtectedMember
    def test_bytesperline_setter(self):
        srec = SRecord()
        for n in range(1, 254):
            with self.subTest(n):
                srec.bytesperline = n
                self.assertEqual(srec.bytesperline, n)
                self.assertEqual(srec._bytesperline, srec.bytesperline)

    # noinspection PyProtectedMember
    def test_bytesperline_setter_none(self):
        srec = SRecord()
        srec.bytesperline = None
        self.assertIs(srec.bytesperline, None)
        self.assertIs(srec.bytesperline, srec._bytesperline)

    def test_bytesperline_setter_invalid(self):
        srec = SRecord()
        with self.assertRaises(ValueError):
            srec.bytesperline = 0

    def test_bytesperline_setter_invalid_2(self):
        srec = SRecord()
        with self.assertRaises(ValueError):
            srec.bytesperline = 254

    def test_bytesperline_setter_invalid_3(self):
        srec = SRecord()
        with self.assertRaises((ValueError, TypeError)):
            srec.bytesperline = "invalid"

    def test_bytesperline_setter_invalid_4(self):
        srec = SRecord()
        with self.assertRaises(TypeError):
            srec.bytesperline = dict()

    # noinspection PyProtectedMember
    def test_header_getter(self):
        srec = SRecord()
        # noinspection PyUnusedLocal
        for n in (b"", b"Test", b"Long string " * 10, randbytes(253),
                  "Some string which will be encoded".encode(),
                  bytearray((randint(0, 255) for r in range(0, randint(0, 253))))):
            with self.subTest(n):
                srec._header = n
                self.assertEqual(n, srec.header)
                self.assertEqual(srec._header, srec.header)

    # noinspection PyProtectedMember
    def test_header_setter(self):
        srec = SRecord()
        # noinspection PyUnusedLocal
        for n in (b"", b"Test", b"Long string " * 10, randbytes(253),
                  "Some string which will be encoded".encode(),
                  bytearray((randint(0, 255) for r in range(0, randint(0, 253))))):
            srec.header = n
            self.assertEqual(n, srec.header)
            self.assertEqual(srec._header, srec.header)

    # noinspection PyProtectedMember
    def test_header_setter_none(self):
        srec = SRecord()
        srec.header = None
        self.assertIs(srec.header, None)
        self.assertIs(srec.header, srec._header)

    # noinspection PyProtectedMember
    def test_header_setter_large(self):
        testdata = randbytes(254)
        srec = SRecord()
        srec.header = testdata
        self.assertEqual(srec.header, testdata[0:253])
        self.assertEqual(srec.header, srec._header)

    def test_header_setter_invalid(self):
        srec = SRecord()
        with self.assertRaises(TypeError):
            srec.header = 0

    def test_header_setter_invalid_4(self):
        srec = SRecord()
        with self.assertRaises(TypeError):
            srec.header = object()

    # noinspection PyProtectedMember
    def test_write_number_of_records_getter(self):
        srec = SRecord()
        for n in (True, False, 0, 1, 2, -1, 2 ** 32, -2 ** 32):
            with self.subTest(n):
                srec._write_number_of_records = bool(n)
                self.assertEqual(bool(n), srec.write_number_of_records)
                self.assertEqual(srec._write_number_of_records, srec.write_number_of_records)

    # noinspection PyProtectedMember
    def test_write_number_of_records_setter(self):
        srec = SRecord()
        for n in (True, False, 0, 1, 2, -1, 2 ** 32, -2 ** 32):
            with self.subTest(n):
                srec.write_number_of_records = n
                self.assertEqual(bool(n), srec.write_number_of_records)
                self.assertEqual(srec._write_number_of_records, srec.write_number_of_records)

    # noinspection PyProtectedMember
    def test_write_number_of_records_setter_none(self):
        srec = SRecord()
        srec.write_number_of_records = None
        self.assertIs(srec.write_number_of_records, None)
        self.assertIs(srec.write_number_of_records, srec._write_number_of_records)

    # noinspection PyProtectedMember
    def test__minaddresslength(self):
        self.assertEqual(SRecord._minaddresslength(0), 2)

        # noinspection PyProtectedMember
        def compare(num):
            minlen = SRecord._minaddresslength(num)
            m = int(("0000" + hex(num)[2:].replace('L', ''))[-2 * minlen:], 16)
            self.assertEqual(num, m)

        for s in range(1, 32):
            n = 1 << s
            compare(n)
            compare(n - 1)
            compare(n + 1)

        with self.assertRaises(ValueError):
            SRecord._minaddresslength(2 ** 32)

    # noinspection PyProtectedMember
    def test__s123addr(self):
        # noinspection PyProtectedMember
        def compare(al, val):
            retdata = bytearray(iter(SRecord._s123addr(al, val)))
            compdata = bytearray.fromhex((("00" * al) + hex(val)[2:].replace('L', ''))[-2 * al:])
            self.assertSequenceEqual(retdata, compdata)

        for adrlen in (2, 3, 4):
            for s in range(1, 8 * adrlen):
                n = 1 << s
                compare(adrlen, n)
                compare(adrlen, n - 1)
                compare(adrlen, n + 1)

        with self.assertRaises(ValueError):
            SRecord._s123addr(0, 0)
        with self.assertRaises(ValueError):
            SRecord._s123addr(1, 0)
        with self.assertRaises(ValueError):
            SRecord._s123addr(5, 0)

    def test_tosrecfile_interface(self):
        testdict = randdict()

        def tosrecfh_replacement(instance, fh, **settings):
            self.assertDictEqual(settings, testdict)
            self.assertEqual(fh.name, self.testfilename)
            if sys.version_info >= (3,):
                self.assertTrue(fh.writable())
            self.assertTrue(hasattr(fh, "write"))
            self.assertTrue(hasattr(fh, "encoding"))  # is text file
            self.assertEqual(fh.tell(), 0)
            return instance

        @patch('hexformat.srecord.SRecord.tosrecfh', tosrecfh_replacement)
        def do():
            srec = SRecord()
            ret = srec.tosrecfile(self.testfilename, **testdict)
            self.assertIs(ret, srec)

        do()

    def test_fromsrecfile_interface(self):
        test_raise_error_on_miscount = randint(0, 1024)

        # noinspection PyDecorator
        @classmethod
        def fromsrecfh_replacement(cls, fh, raise_error_on_miscount=True):
            self.assertEqual(raise_error_on_miscount, test_raise_error_on_miscount)
            self.assertEqual(fh.name, self.testfilename)
            if sys.version_info >= (3,):
                self.assertTrue(fh.readable())
            self.assertTrue(hasattr(fh, "read"))
            self.assertTrue(hasattr(fh, "encoding"))  # is text file
            self.assertEqual(fh.tell(), 0)
            return cls()

        @patch('hexformat.srecord.SRecord.fromsrecfh', fromsrecfh_replacement)
        def do():
            srec = SRecord.fromsrecfile(self.testfilename, test_raise_error_on_miscount)
            self.assertIsInstance(srec, SRecord)

        with open(self.testfilename, "w") as fh:
            fh.write("")

        do()

    def test_fromsrecfh_interface(self):
        testfh = object()
        test_raise_error_on_miscount = randint(0, 1024)

        def loadsrecfh_replacement(instance, fh, raise_error_on_miscount=True):
            self.assertEqual(raise_error_on_miscount, test_raise_error_on_miscount)
            self.assertIs(fh, testfh)
            return instance

        @patch('hexformat.srecord.SRecord.loadsrecfh', loadsrecfh_replacement)
        def do():
            srec = SRecord.fromsrecfh(testfh, test_raise_error_on_miscount)
            self.assertIsInstance(srec, SRecord)

        do()

    def test_loadsrecfile_interface(self):
        test_overwrite_metadata = randint(0, 1024)
        test_overwrite_data = randint(0, 1024)
        test_raise_error_on_miscount = randint(0, 1024)

        def loadsrecfile_replacement(instance, fh, overwrite_metadata=False, overwrite_data=True,
                                     raise_error_on_miscount=True):
            self.assertEqual(overwrite_metadata, test_overwrite_metadata)
            self.assertEqual(overwrite_data, test_overwrite_data)
            self.assertEqual(raise_error_on_miscount, test_raise_error_on_miscount)
            self.assertEqual(fh.name, self.testfilename)
            if sys.version_info >= (3,):
                self.assertTrue(fh.readable())
            self.assertTrue(hasattr(fh, "read"))
            self.assertTrue(hasattr(fh, "encoding"))  # is text file
            self.assertEqual(fh.tell(), 0)
            return instance

        @patch('hexformat.srecord.SRecord.loadsrecfh', loadsrecfile_replacement)
        def do():
            srec = SRecord()
            ret = srec.loadsrecfile(self.testfilename, test_overwrite_metadata,
                                    test_overwrite_data, test_raise_error_on_miscount)
            self.assertIs(ret, srec)

        with open(self.testfilename, "w") as fh:
            fh.write("")

        do()

    def test_encodesrecline_failure(self):
        # noinspection PyProtectedMember
        for recordtype in (10, 11, "invalid"):
            with self.subTest(recordtype):
                with self.assertRaises(EncodeError):
                    SRecord._encodesrecline(None, recordtype, 0, bytearray())

    def test_tosrecfh_addresslength2(self):
        srec = SRecord().set(0x8CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
        expected = [
            "S00700005465737458\n",
            "S1138CE0FACEDEEDCAFEBEEF1234567890ABCDEF6D\n",
            "S903FFFFFE\n",
        ]
        fh = FakeFileHandle()
        srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFF, addresslength=2, write_number_of_records=False)
        self.assertListEqual(fh, expected)
        fh = FakeFileHandle()
        srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFF, write_number_of_records=False)
        self.assertListEqual(fh, expected)

    def test_tosrecfh_addresslength3(self):
        srec = SRecord().set(0xFF8CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
        expected = [
            "S00700005465737458\n",
            "S214FF8CE0FACEDEEDCAFEBEEF1234567890ABCDEF6D\n",
            "S804FFFFFFFE\n",
        ]
        fh = FakeFileHandle()
        srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFFFF, addresslength=3, write_number_of_records=False)
        yield self.assertListEqual, fh, expected
        fh = FakeFileHandle()
        srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFFFF, write_number_of_records=False)
        yield self.assertListEqual, fh, expected

    def test_tosrecfh_addresslength4(self):
        srec = SRecord().set(0xFF008CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
        expected = [
            "S00700005465737458\n",
            "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
            "S705FFFFFFFFFE\n",
        ]
        fh = FakeFileHandle()
        srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFFFFFF, addresslength=4, write_number_of_records=False)
        yield self.assertListEqual, fh, expected
        fh = FakeFileHandle()
        srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFFFFFF, write_number_of_records=False)
        yield self.assertListEqual, fh, expected

    def test_tosrecfh_write_number_of_records(self):
        srec = SRecord().set(0xFF008CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
        expected = [
            "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
            "S5030001FB\n",
            "S70500000000FA\n",
        ]
        fh = FakeFileHandle()
        srec.tosrecfh(fh, write_number_of_records=True)
        yield self.assertListEqual, fh, expected

    def test_tosrecfh_write_number_of_records_s5(self):
        srec = SRecord().fill(0x0, 0xFFFF)
        fh = FakeFileHandle()
        expected = "S503FFFFFE\n"
        srec.tosrecfh(fh, bytesperline=1, write_number_of_records=True)
        self.assertEqual(fh[-2], expected)

    def test_tosrecfh_write_number_of_records_s6(self):
        srec = SRecord().fill(0x0, 0x10000)
        fh = FakeFileHandle()
        expected = "S604010000FA\n"
        srec.tosrecfh(fh, bytesperline=1, write_number_of_records=True)
        self.assertEqual(fh[-2], expected)

    @skipunlessslow
    def test_tosrecfh_write_number_of_records_too_large(self):
        srec = SRecord().fill(0x0, 0x1000000)
        fh = FakeFileHandle()
        srec.tosrecfh(fh, bytesperline=1, addresslength=3, write_number_of_records=True, header=b'Test')
        self.assertFalse(fh[-2].startswith('S3'))
        self.assertEqual(len(fh), 0x1000002)

    test_tosrecfh_write_number_of_records_too_large.slow = 1

    # noinspection PyProtectedMember
    def test_parsesrecline_failure1(self):
        with self.assertRaises(DecodeError):
            return SRecord._parsesrecline(":0000000000000")

    # noinspection PyProtectedMember
    def test_parsesrecline_failure2(self):
        with self.assertRaises(DecodeError):
            return SRecord._parsesrecline("s000000000000")

    # noinspection PyProtectedMember
    def test_parsesrecline_failure4(self):
        """ Missing hexdigit """
        with self.assertRaises(DecodeError):
            return SRecord._parsesrecline("S101000")

    # noinspection PyProtectedMember
    def test_parsesrecline_failure5(self):
        with self.assertRaises(DecodeError):
            return SRecord._parsesrecline("S10800")

    # noinspection PyProtectedMember
    def test_parsesrecline_failure6(self):
        with self.assertRaises(DecodeError):
            return SRecord._parsesrecline("SX0800")

    # noinspection PyProtectedMember
    def test_parsesrecline_ok(self):
        testaddress = 0xFF008CE0
        testdata = bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF")
        yield (self.assertTupleEqual, SRecord._parsesrecline("S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C"),
               (3, testaddress, testdata, len(testdata), True))

    def test_loadsrecfh_1(self):
        expectedsrec = SRecord(bytesperline=32, addresslength=2, write_number_of_records=True, header=b"some").set(
            0xFF008CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
        fh = FakeFileHandle((
            "S00700005465737458\n",
            "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
            "S5030001FB\n",
            "S70500000000FA\n",
        ))
        srec = SRecord(bytesperline=32, addresslength=2, write_number_of_records=True, header=b"some")
        srec.loadsrecfh(fh, overwrite_metadata=False)
        yield self.assertEqual, srec, expectedsrec
        yield self.assertEqual, srec.bytesperline, expectedsrec.bytesperline
        yield self.assertEqual, srec.write_number_of_records, expectedsrec.write_number_of_records
        yield self.assertEqual, srec.header, expectedsrec.header

    def test_loadsrecfh_2(self):
        expectedsrec = SRecord(bytesperline=32, addresslength=2, header=b"some").set(
            0xFF008CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
        fh = FakeFileHandle((
            "S00700005465737458\n",
            "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
            "S5030001FB\n",
            "S70500000000FA\n",
        ))
        srec = SRecord(bytesperline=32, addresslength=2, header=b"some")
        srec.loadsrecfh(fh, overwrite_metadata=False)
        yield self.assertEqual, srec, expectedsrec
        yield self.assertEqual, srec.bytesperline, expectedsrec.bytesperline
        yield self.assertTrue, srec.write_number_of_records
        yield self.assertEqual, srec.header, expectedsrec.header

    def test_loadsrecfh_countmissmatch_1(self):
        fh = FakeFileHandle((
            "S00700005465737458\n",
            "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
            "S5030002FA\n",
            "S70500000000FA\n",
        ))
        srec = SRecord()
        with self.assertRaises(DecodeError):
            srec.loadsrecfh(fh)

    def test_loadsrecfh_countmissmatch_s5_true(self):
        fh = FakeFileHandle((
            "S00700005465737458\n",
            "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
            "S5030002FA\n",
            "S70500000000FA\n",
        ))
        srec = SRecord()
        with self.assertRaises(DecodeError):
            srec.loadsrecfh(fh, raise_error_on_miscount=True)

    def test_loadsrecfh_countmissmatch_s5_false(self):
        fh = FakeFileHandle((
            "S00700005465737458\n",
            "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
            "S5030002FA\n",
            "S70500000000FA\n",
        ))
        srec = SRecord()
        srec.loadsrecfh(fh, raise_error_on_miscount=False)

    def test_loadsrecfh_countmissmatch_s6_true(self):
        fh = FakeFileHandle((
            "S00700005465737458\n",
            "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
            "S604000002F8\n",
            "S70500000000FA\n",
        ))
        srec = SRecord()
        with self.assertRaises(DecodeError):
            srec.loadsrecfh(fh, raise_error_on_miscount=True)

    def test_loadsrecfh_countmissmatch_s6_false(self):
        fh = FakeFileHandle((
            "S00700005465737458\n",
            "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
            "S604000002F8\n",
            "S70500000000FA\n",
        ))
        srec = SRecord()
        srec.loadsrecfh(fh, raise_error_on_miscount=False)

    def test_loadsrecfh_startaddress_1(self):
        fh = FakeFileHandle((
            "S705000001FFFA\n",
        ))
        srec = SRecord()
        srec.loadsrecfh(fh)
        yield self.assertEqual, srec.startaddress, 0x1FF

    def test_loadsrecfh_startaddress_2(self):
        fh = FakeFileHandle((
            "S705000001FFFA\n",
        ))
        srec = SRecord(startaddress=0xDEADBEEF)
        srec.loadsrecfh(fh)
        yield self.assertEqual, srec.startaddress, 0xDEADBEEF

    def test_loadsrecfh_invalid_recordtype(self):
        fh = FakeFileHandle((
            "S405000301FFFA\n",
        ))
        srec = SRecord(startaddress=0xDEADBEEF)
        with self.assertRaises(DecodeError):
            srec.loadsrecfh(fh)
