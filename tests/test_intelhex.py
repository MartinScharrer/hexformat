from hexformat.intelhex import IntelHex
import sys
from tests import TestCaseWithTempfile, patch, randbytes, randint, randdict

from hexformat.base import DecodeError, EncodeError


class FakeFileHandle(list):
    def write(self, line):
        self.append(line)

    def readline(self):
        try:
            return self.pop(0)
        except IndexError:
            return ''


class TestIntelHex(TestCaseWithTempfile):

    # noinspection PyProtectedMember
    def test_bytesperline_getter(self):
        ih = IntelHex()
        for n in range(0, 255):
            ih._bytesperline = n
            self.assertEqual(ih._bytesperline, n)
            self.assertEqual(ih._bytesperline, ih.bytesperline)

    # noinspection PyProtectedMember
    def test_bytesperline_setter(self):
        ih = IntelHex()
        for n in range(1, 255):
            ih.bytesperline = n
            self.assertEqual(ih.bytesperline, n)
            self.assertEqual(ih._bytesperline, ih.bytesperline)

    # noinspection PyProtectedMember
    def test_bytesperline_setter_none(self):
        ih = IntelHex()
        ih.bytesperline = None
        self.assertIs(ih.bytesperline, None)
        self.assertIs(ih.bytesperline, ih._bytesperline)

    def test_bytesperline_setter_invalid(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            ih.bytesperline = 0

    def test_bytesperline_setter_invalid_2(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            ih.bytesperline = 256

    def test_bytesperline_setter_invalid_3(self):
        ih = IntelHex()
        with self.assertRaises((ValueError, TypeError)):
            ih.bytesperline = "invalid"

    def test_bytesperline_setter_invalid_4(self):
        ih = IntelHex()
        with self.assertRaises(TypeError):
            ih.bytesperline = set()

    # noinspection PyProtectedMember
    def test_variant_getter(self):
        ih = IntelHex()
        for n in (8, 16, 32):
            ih._variant = n
            self.assertEqual(ih._variant, n)
            self.assertEqual(ih._variant, ih.variant)

    # noinspection PyProtectedMember
    def test_variant_setter(self):
        ih = IntelHex()
        for n in (8, 16, 32):
            ih.variant = n
            self.assertEqual(ih.variant, n)
            self.assertEqual(ih._variant, ih.variant)
        ih.variant = 'I08HEX'
        self.assertEqual(ih._variant, 8)
        self.assertEqual(ih._variant, ih.variant)
        ih.variant = 'I8HEX'
        self.assertEqual(ih._variant, 8)
        self.assertEqual(ih._variant, ih.variant)
        ih.variant = 'I16HEX'
        self.assertEqual(ih._variant, 16)
        self.assertEqual(ih._variant, ih.variant)
        ih.variant = 'I32HEX'
        self.assertEqual(ih._variant, 32)
        self.assertEqual(ih._variant, ih.variant)

    # noinspection PyProtectedMember
    def test_variant_setter_none(self):
        ih = IntelHex()
        ih.variant = None
        self.assertIs(ih.variant, None)
        self.assertIs(ih.variant, ih._variant)

    def test_variant_setter_invalid(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            ih.variant = 0

    def test_variant_setter_invalid_2(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            ih.variant = "invalid"

    def test_variant_setter_invalid_3(self):
        ih = IntelHex()
        with self.assertRaises(TypeError):
            ih.variant = set()

    # noinspection PyProtectedMember
    def test_cs_ip_getter(self):
        ih = IntelHex()
        ih._cs_ip = 0
        self.assertEqual(ih._cs_ip, 0)
        self.assertEqual(ih._cs_ip, ih.cs_ip)
        for n in range(0, 4 * 8):
            m = 1 << n
            ih._cs_ip = m
            self.assertEqual(ih._cs_ip, m)
            self.assertEqual(ih._cs_ip, ih.cs_ip)

    # noinspection PyProtectedMember
    def test_cs_ip_setter(self):
        ih = IntelHex()
        ih.cs_ip = 0
        self.assertEqual(ih.cs_ip, 0)
        self.assertEqual(ih._cs_ip, ih.cs_ip)
        for n in range(0, 4 * 8):
            m = 1 << n
            ih.cs_ip = m
            self.assertEqual(ih.cs_ip, m)
            self.assertEqual(ih._cs_ip, ih.cs_ip)

    # noinspection PyProtectedMember
    def test_cs_ip_setter_none(self):
        ih = IntelHex()
        ih.cs_ip = None
        self.assertIs(ih.cs_ip, None)
        self.assertIs(ih.cs_ip, ih._cs_ip)

    def test_cs_ip_setter_invalid(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            ih.cs_ip = -1

    def test_cs_ip_setter_invalid_2(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            ih.cs_ip = 2 ** 32

    def test_cs_ip_setter_invalid_3(self):
        ih = IntelHex()
        with self.assertRaises((ValueError, TypeError)):
            ih.cs_ip = "invalid"

    def test_cs_ip_setter_invalid_4(self):
        ih = IntelHex()
        with self.assertRaises(TypeError):
            ih.cs_ip = set()

    # noinspection PyProtectedMember
    def test_eip_getter(self):
        ih = IntelHex()
        ih._eip = 0
        self.assertEqual(ih._eip, 0)
        self.assertEqual(ih._eip, ih.eip)
        for n in range(0, 4 * 8):
            m = 1 << n
            ih._eip = m
            self.assertEqual(ih._eip, m)
            self.assertEqual(ih._eip, ih.eip)

    # noinspection PyProtectedMember
    def test_eip_setter(self):
        ih = IntelHex()
        ih.eip = 0
        self.assertEqual(ih.eip, 0)
        self.assertEqual(ih._eip, ih.eip)
        for n in range(0, 4 * 8):
            m = 1 << n
            ih.eip = m
            self.assertEqual(ih.eip, m)
            self.assertEqual(ih._eip, ih.eip)

    # noinspection PyProtectedMember
    def test_eip_setter_none(self):
        ih = IntelHex()
        ih.eip = None
        self.assertIs(ih.eip, None)
        self.assertIs(ih.eip, ih._eip)

    def test_eip_setter_invalid(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            ih.eip = -1

    def test_eip_setter_invalid_2(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            ih.eip = 2 ** 32

    def test_eip_setter_invalid_3(self):
        ih = IntelHex()
        with self.assertRaises((ValueError, TypeError)):
            ih.eip = "invalid"

    def test_eip_setter_invalid_4(self):
        ih = IntelHex()
        with self.assertRaises(TypeError):
            ih.eip = set()

    def test_toihexfile_interface(self):
        testdict = randdict()

        def toihexfh_replacement(instance, fh, **settings):
            self.assertDictEqual(settings, testdict)
            self.assertEqual(fh.name, self.testfilename)
            if sys.version_info >= (3,):
                self.assertTrue(fh.writable())
            self.assertTrue(hasattr(fh, "write"))
            self.assertTrue(hasattr(fh, "encoding"))  # is text file
            self.assertEqual(fh.tell(), 0)
            return instance

        @patch('hexformat.intelhex.IntelHex.toihexfh', toihexfh_replacement)
        def do():
            ihex = IntelHex()
            ret = ihex.toihexfile(self.testfilename, **testdict)
            self.assertIs(ret, ihex)

        do()

    def test_fromihexfile_interface(self):
        test_ignore_checksum_errors = randint(0, 1024)

        # noinspection PyDecorator
        @classmethod
        def fromihexfh_replacement(cls, fh, ignore_checksum_errors=False):
            self.assertEqual(ignore_checksum_errors, test_ignore_checksum_errors)
            self.assertEqual(fh.name, self.testfilename)
            if sys.version_info >= (3,):
                self.assertTrue(fh.readable())
            self.assertTrue(hasattr(fh, "read"))
            self.assertTrue(hasattr(fh, "encoding"))  # is text file
            self.assertEqual(fh.tell(), 0)
            return cls()

        @patch('hexformat.intelhex.IntelHex.fromihexfh', fromihexfh_replacement)
        def do():
            ih = IntelHex.fromihexfile(self.testfilename, test_ignore_checksum_errors)
            self.assertIsInstance(ih, IntelHex)

        with open(self.testfilename, "w") as fh:
            fh.write("")

        do()

    def test_fromihexfh_interface(self):
        testfh = object()
        test_ignore_checksum_errors = randint(0, 1024)

        @classmethod
        def loadihexfh_replacement(cls, fh, ignore_checksum_errors=False):
            self.assertEqual(ignore_checksum_errors, test_ignore_checksum_errors)
            self.assertIs(fh, testfh)
            return cls()

        @patch('hexformat.intelhex.IntelHex.loadihexfh', loadihexfh_replacement)
        def do():
            ih = IntelHex.fromihexfh(testfh, test_ignore_checksum_errors)
            self.assertIsInstance(ih, IntelHex)

        do()

    def test_loadihexfile_interface(self):
        test_ignore_checksum_errors = randint(0, 1024)

        def loadihexfile_replacement(instance, fh, ignore_checksum_errors=False):
            self.assertEqual(ignore_checksum_errors, test_ignore_checksum_errors)
            self.assertEqual(fh.name, self.testfilename)
            if sys.version_info >= (3,):
                self.assertTrue(fh.readable())
            self.assertTrue(hasattr(fh, "read"))
            self.assertTrue(hasattr(fh, "encoding"))  # is text file
            self.assertEqual(fh.tell(), 0)
            return instance

        @patch('hexformat.intelhex.IntelHex.loadihexfh', loadihexfile_replacement)
        def do():
            ih = IntelHex()
            ret = ih.loadihexfile(self.testfilename, test_ignore_checksum_errors)
            self.assertIs(ret, ih)

        with open(self.testfilename, "w") as fh:
            fh.write("")

        do()

    def test_eq(self):
        testdata1 = randbytes(randint(10, 2 ** 16))
        testaddr1 = randint(0, 2 ** 32 - 1)
        testdata2 = randbytes(randint(10, 2 ** 16))
        testaddr2 = randint(0, 2 ** 32 - 1)
        testdata3 = randbytes(randint(10, 2 ** 16))
        testaddr3 = randint(0, 2 ** 32 - 1)
        testeid = randint(0, 2 ** 32 - 1)
        testcsip = randint(0, 2 ** 32 - 1)

        ih1 = IntelHex()
        ih1.set(testaddr1, testdata1)
        ih1.set(testaddr2, testdata2)
        ih1.set(testaddr3, testdata3)
        ih1.eip = testeid
        ih1.cs_ip = testcsip

        ih2 = IntelHex()
        ih2.set(testaddr1, testdata1)
        ih2.set(testaddr2, testdata2)
        ih2.set(testaddr3, testdata3)
        ih2.eip = testeid
        ih2.cs_ip = testcsip

        self.assertEqual(ih1, ih2)
        self.assertEqual(ih1, ih1.copy())
        ih3 = ih2.copy()
        ih3.eip -= 1
        self.assertNotEqual(ih1, ih3)
        ih2.cs_ip += 1
        self.assertNotEqual(ih1, ih2)

    # noinspection PyProtectedMember
    def test_parseihexline_failure_startchar(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            return ih._parseihexline("S020000000")

    # noinspection PyProtectedMember
    def test_parseihexline_failure_hexmiscount(self):
        ih = IntelHex()
        with self.assertRaises(ValueError):
            return ih._parseihexline(":000102030")

    # noinspection PyProtectedMember
    def test_parseihexline_failure_bytecount_high(self):
        ih = IntelHex()
        with self.assertRaises(DecodeError):
            return ih._parseihexline(":04000000FFFFFF00")

    # noinspection PyProtectedMember
    def test_parseihexline_failure_bytecount_low(self):
        ih = IntelHex()
        with self.assertRaises(DecodeError):
            return ih._parseihexline(":02000000FFFFFF00")

    # noinspection PyProtectedMember
    def test_parseihexline_failure_recordtype(self):
        ih = IntelHex()
        with self.assertRaises(DecodeError):
            return ih._parseihexline(":030000ABFFFFFF00")

    # noinspection PyProtectedMember
    def test_parseihexline_failure_recordtype_bytecount_mismatch(self):
        ih = IntelHex()
        with self.assertRaises(DecodeError):
            return ih._parseihexline(":03000003FFFFFF00")

    # noinspection PyProtectedMember
    def test_parseihexline_r0(self):
        testline = ":10010000214601360121470136007EFE09D2190140\n"
        testbytecount = 0x10
        testaddress = 0x0100
        testrecordtype = 0x00
        testdata = bytearray.fromhex("214601360121470136007EFE09D21901")
        testchecksumcorrect = True

        ih = IntelHex()
        (recordtype, address, data, bytecount, checksumcorrect) = ih._parseihexline(testline)
        self.assertEqual(recordtype, testrecordtype)
        self.assertEqual(address, testaddress)
        self.assertEqual(data, testdata)
        self.assertEqual(bytecount, testbytecount)
        self.assertEqual(checksumcorrect, testchecksumcorrect)

    # noinspection PyProtectedMember
    def test_parseihexline_r0_wrongcrc(self):
        testline = ":10010000214601360121470136007EFE09D21901F3\n"
        testbytecount = 0x10
        testaddress = 0x0100
        testrecordtype = 0x00
        testdata = bytearray.fromhex("214601360121470136007EFE09D21901")
        testchecksumcorrect = False

        ih = IntelHex()
        (recordtype, address, data, bytecount, checksumcorrect) = ih._parseihexline(testline)
        self.assertEqual(recordtype, testrecordtype)
        self.assertEqual(address, testaddress)
        self.assertEqual(data, testdata)
        self.assertEqual(bytecount, testbytecount)
        self.assertEqual(checksumcorrect, testchecksumcorrect)

    try:
        # noinspection PyStatementEffect
        bytearray.hex
    except AttributeError:
        pass
    else:
        # noinspection PyProtectedMember
        def test_parseihexline_r0_random(self):
            for r in range(0, 10):
                testbytecount = randint(1, 255)
                testaddress = randint(0, 0xFFFF)
                testrecordtype = 0x00
                testdata = randbytes(testbytecount)
                allbytes = bytearray((testbytecount, (testaddress >> 8) & 0xFF, testaddress & 0xFF, testrecordtype))
                allbytes += testdata
                allbytes += bytearray(1)
                testline = ":" + allbytes.hex().upper()
                # sys.stdout.write(testline)

                ih = IntelHex()
                (recordtype, address, data, bytecount, checksumcorrect) = ih._parseihexline(testline)
                self.assertEqual(recordtype, testrecordtype)
                self.assertEqual(address, testaddress)
                self.assertEqual(data, testdata)
                self.assertEqual(bytecount, testbytecount)

    RECORDTYPE_LENGTH = {
        0: None,
        1: 0,
        2: 2,
        3: 4,
        4: 2,
        5: 4,
    }

    # noinspection PyProtectedMember
    def test_encodeihexline_recordtype_valid(self):
        for rt, l in self.RECORDTYPE_LENGTH.items():
            if l is None:
                l = randint(0, 200)
            ih = IntelHex()
            ih._encodeihexline(rt, 0, bytearray(l))

    # noinspection PyProtectedMember
    def test_encodeihexline_recordtype_invalid(self):
        ih = IntelHex()
        for n in list(range(6, 256)) + list(range(-128, -1)):
            yield self.assertRaises, EncodeError, ih._encodeihexline, n, 0, bytearray(2)

    # noinspection PyProtectedMember
    def test_encodeihexline_recordtype_datalength_mismatch(self):
        for rt, l in self.RECORDTYPE_LENGTH.items():
            if l is None:
                continue
            ih = IntelHex()
            if l > 1:
                yield self.assertRaises, EncodeError, ih._encodeihexline, rt, 0, bytearray(l - 1)
            yield self.assertRaises, EncodeError, ih._encodeihexline, rt, 0, bytearray(l + 1)

    # noinspection PyProtectedMember
    def test_loadihexfh_unsupported_record_type(self):
        ih = IntelHex()
        ih._DATALENGTH = list(ih._DATALENGTH) + [0, ]  # Add other record type to reach last clause
        fh = FakeFileHandle((":00000006FA\n",))
        with self.assertRaises(DecodeError):
            ih.loadihexfh(fh)

    def test_loadihexfh_checksum_error(self):
        ih = IntelHex()
        fh = FakeFileHandle((":00000001FE\n",))
        with self.assertRaises(DecodeError):
            ih.loadihexfh(fh)

    def test_loadihexfh_empty(self):
        ih = IntelHex()
        fh = FakeFileHandle()
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 0)

    def test_loadihexfh_r0_1(self):
        ih = IntelHex()
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0xDEAD
        fh = FakeFileHandle((':08DEAD000123456789ABCDEFAD',))
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.bytesperline, 8)

    def test_loadihexfh_r0_2(self):
        ih = IntelHex()
        ih.settings(bytesperline=32)
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0xDEAD
        fh = FakeFileHandle((':08DEAD000123456789ABCDEFAD',))
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.bytesperline, 32)

    def test_loadihexfh_r1_1(self):
        ih = IntelHex()
        fh = FakeFileHandle((':00000001FF',))
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 0)

    def test_loadihexfh_r1_2(self):
        ih = IntelHex()
        fh = FakeFileHandle((':00000001FF', ':00000001FF'))
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 0)
        self.assertEqual(len(fh), 1)

    def test_loadihexfh_r2_1(self):
        ih = IntelHex()
        fh = FakeFileHandle((':020000022BC011', ':08DEAD000123456789ABCDEFAD'))
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0x2BC0 * 16 + 0xDEAD
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.variant, 16)

    def test_loadihexfh_r2_2(self):
        ih = IntelHex()
        ih.variant = 32
        fh = FakeFileHandle((':020000022BC011', ':08DEAD000123456789ABCDEFAD'))
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0x2BC0 * 16 + 0xDEAD
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.variant, 32)

    def test_loadihexfh_r3_1(self):
        ih = IntelHex()
        fh = FakeFileHandle((':040000032BC0F0100E', ':08DEAD000123456789ABCDEFAD'))
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0xDEAD
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.variant, 16)
        self.assertEqual(ih.cs_ip, 0x2BC0F010)

    def test_loadihexfh_r3_2(self):
        ih = IntelHex()
        ih.variant = 32
        fh = FakeFileHandle((':040000032BC0F0100E', ':08DEAD000123456789ABCDEFAD'))
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0xDEAD
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.variant, 32)
        self.assertEqual(ih.cs_ip, 0x2BC0F010)

    def test_loadihexfh_r4_1(self):
        ih = IntelHex()
        fh = FakeFileHandle((':020000042BC00F', ':08DEAD000123456789ABCDEFAD'))
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0x2BC0DEAD
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.variant, 32)

    def test_loadihexfh_r4_2(self):
        ih = IntelHex()
        ih.variant = 16
        fh = FakeFileHandle((':020000042BC00F', ':08DEAD000123456789ABCDEFAD'))
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0x2BC0DEAD
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.variant, 16)

    def test_loadihexfh_r5_1(self):
        ih = IntelHex()
        fh = FakeFileHandle((':040000052BC0F0100C', ':08DEAD000123456789ABCDEFAD'))
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0xDEAD
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.variant, 32)
        self.assertEqual(ih.eip, 0x2BC0F010)

    def test_loadihexfh_r5_2(self):
        ih = IntelHex()
        ih.variant = 16
        fh = FakeFileHandle((':040000052BC0F0100C', ':08DEAD000123456789ABCDEFAD'))
        testdata = bytearray.fromhex("0123456789ABCDEF")
        testaddr = 0xDEAD
        ret = ih.loadihexfh(fh)
        self.assertIs(ret, ih)
        self.assertEqual(ih.usedsize(), 8)
        self.assertEqual(ih.start(), testaddr)
        self.assertSequenceEqual(ih[:], testdata)
        self.assertEqual(ih.variant, 16)
        self.assertEqual(ih.eip, 0x2BC0F010)

    def test_toihexfh_eip_1(self):
        testlist = [":04000005A5880123A6\n", ":00000001FF\n"]
        ih = IntelHex()
        ih.eip = 0xA5880123
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=32)
        self.assertListEqual(fh, testlist)

    def test_toihexfh_eip_2(self):
        testlist = [":00000001FF\n", ]
        ih = IntelHex()
        ih.eip = 0xA5880123
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=16)
        self.assertListEqual(fh, testlist)

    def test_toihexfh_eip_3(self):
        testlist = [":00000001FF\n", ]
        ih = IntelHex()
        ih.eip = None
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=32)
        self.assertListEqual(fh, testlist)

    def test_toihexfh_csip_1(self):
        testlist = [":04000003A5880123A8\n", ":00000001FF\n"]
        ih = IntelHex()
        ih.cs_ip = 0xA5880123
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=16)
        self.assertListEqual(fh, testlist)

    def test_toihexfh_csip_2(self):
        testlist = [":00000001FF\n", ]
        ih = IntelHex()
        ih.cs_ip = 0xA5880123
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=32)
        self.assertListEqual(fh, testlist)

    def test_toihexfh_csip_3(self):
        testlist = [":00000001FF\n", ]
        ih = IntelHex()
        ih.cs_ip = None
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=16)
        self.assertListEqual(fh, testlist)

    def test_toihexfh_address_too_large_32(self):
        ih = IntelHex()
        ih.set(0x100000000, bytearray(1))
        fh = FakeFileHandle()
        with self.assertRaises(EncodeError):
            ih.toihexfh(fh, variant=32)

    def test_toihexfh_address_too_large_16(self):
        ih = IntelHex()
        ih.set(0x100000, bytearray(1))
        fh = FakeFileHandle()
        with self.assertRaises(EncodeError):
            ih.toihexfh(fh, variant=16)

    def test_toihexfh_address_too_large_8(self):
        ih = IntelHex()
        ih.set(0x10000, bytearray(1))
        fh = FakeFileHandle()
        with self.assertRaises(EncodeError):
            ih.toihexfh(fh, variant=8)

    def test_toihexfh_address_max_32(self):
        testlist = [":02000004FFFFFC\n", ":01FFFF00AA57\n", ":00000001FF\n"]
        ih = IntelHex()
        ih.set(0xFFFFFFFF, bytearray((0xAA,)))
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=32)
        self.assertListEqual(fh, testlist)

    def test_toihexfh_address_max_16(self):
        testlist = [":02000002FFF00D\n", ":0100FF00AA56\n", ":00000001FF\n"]
        ih = IntelHex()
        ih.set(0xFFFFF, bytearray((0xAA,)))
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=16)
        self.assertListEqual(fh, testlist)

    def test_toihexfh_address_max_8(self):
        testlist = [":01FFFF00AA57\n", ":00000001FF\n"]
        ih = IntelHex()
        ih.set(0xFFFF, bytearray((0xAA,)))
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=8)
        self.assertListEqual(fh, testlist)

    def test_toihexfh_address_section_16(self):
        testlist = [":01FFFF00AA57\n", ":00000001FF\n"]
        ih = IntelHex()
        ih.set(0x0FFFF, bytearray((0xAA,)))
        fh = FakeFileHandle()
        ih.toihexfh(fh, variant=16)
        self.assertListEqual(fh, testlist)

    # noinspection PyProtectedMember
    def test_toihexfh_segment_wrap(self):
        fh = FakeFileHandle([":02000002E0001C\n", ":02FFFF00DEAD75\n", ":00000001FF\n"])
        testih = IntelHex()
        testih.set(0xEFFFF, (0xDE,))
        testih.set(0xE0000, (0xAD,))
        ih = IntelHex.fromfh(fh)
        yield self.assertListEqual, ih._parts, testih._parts
        yield self.assertEqual, ih, testih
