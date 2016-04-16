from hexformat.intelhex import IntelHex
from nose.tools import raises, assert_equal, assert_is, assert_true, assert_dict_equal
from nose.tools import assert_is_instance, assert_not_equal, assert_raises, assert_sequence_equal
from mock import patch
import random
import tempfile
import os
import sys
import shutil
from .test_multipartbuffer import randomdata
from .test_srecord import randomdict
from hexformat.base import DecodeError, EncodeError

dirname = ""
testfilename = ""


class FakeFileHandle(list):
    def write(self, line):
        self.append(line)

    def readline(self):
        try:
            return self.pop(0)
        except IndexError:
            return ''


def setup():
    global dirname
    global testfilename
    dirname = tempfile.mkdtemp(prefix="test_intelhex_")
    sys.stderr.write("Tempdir: {:s}\n".format(dirname))
    testfilename = os.path.join(dirname, "testdata.hex")


def teardown():
    # noinspection PyBroadException
    try:
        shutil.rmtree(dirname)
    except:
        pass


# noinspection PyProtectedMember
def test_bytesperline_getter():
    ih = IntelHex()
    for n in range(0, 255):
        ih._bytesperline = n
        assert_equal(ih._bytesperline, n)
        assert_equal(ih._bytesperline, ih.bytesperline)


# noinspection PyProtectedMember
def test_bytesperline_setter():
    ih = IntelHex()
    for n in range(1, 255):
        ih.bytesperline = n
        assert_equal(ih.bytesperline, n)
        assert_equal(ih._bytesperline, ih.bytesperline)


# noinspection PyProtectedMember
def test_bytesperline_setter_none():
    ih = IntelHex()
    ih.bytesperline = None
    assert_is(ih.bytesperline, None)
    assert_is(ih.bytesperline, ih._bytesperline)


@raises(ValueError)
def test_bytesperline_setter_invalid():
    ih = IntelHex()
    ih.bytesperline = 0


@raises(ValueError)
def test_bytesperline_setter_invalid_2():
    ih = IntelHex()
    ih.bytesperline = 256


@raises(ValueError, TypeError)
def test_bytesperline_setter_invalid_3():
    ih = IntelHex()
    ih.bytesperline = "invalid"


@raises(TypeError)
def test_bytesperline_setter_invalid_4():
    ih = IntelHex()
    ih.bytesperline = set()


# noinspection PyProtectedMember
def test_variant_getter():
    ih = IntelHex()
    for n in (8, 16, 32):
        ih._variant = n
        assert_equal(ih._variant, n)
        assert_equal(ih._variant, ih.variant)


# noinspection PyProtectedMember
def test_variant_setter():
    ih = IntelHex()
    for n in (8, 16, 32):
        ih.variant = n
        assert_equal(ih.variant, n)
        assert_equal(ih._variant, ih.variant)
    ih.variant = 'I08HEX'
    assert_equal(ih._variant, 8)
    assert_equal(ih._variant, ih.variant)
    ih.variant = 'I8HEX'
    assert_equal(ih._variant, 8)
    assert_equal(ih._variant, ih.variant)
    ih.variant = 'I16HEX'
    assert_equal(ih._variant, 16)
    assert_equal(ih._variant, ih.variant)
    ih.variant = 'I32HEX'
    assert_equal(ih._variant, 32)
    assert_equal(ih._variant, ih.variant)


# noinspection PyProtectedMember
def test_variant_setter_none():
    ih = IntelHex()
    ih.variant = None
    assert_is(ih.variant, None)
    assert_is(ih.variant, ih._variant)


@raises(ValueError)
def test_variant_setter_invalid():
    ih = IntelHex()
    ih.variant = 0


@raises(ValueError)
def test_variant_setter_invalid_2():
    ih = IntelHex()
    ih.variant = "invalid"


@raises(TypeError)
def test_variant_setter_invalid_3():
    ih = IntelHex()
    ih.variant = set()


# noinspection PyProtectedMember
def test_cs_ip_getter():
    ih = IntelHex()
    ih._cs_ip = 0
    assert_equal(ih._cs_ip, 0)
    assert_equal(ih._cs_ip, ih.cs_ip)
    for n in range(0, 4*8):
        m = 1 << n
        ih._cs_ip = m
        assert_equal(ih._cs_ip, m)
        assert_equal(ih._cs_ip, ih.cs_ip)


# noinspection PyProtectedMember
def test_cs_ip_setter():
    ih = IntelHex()
    ih.cs_ip = 0
    assert_equal(ih.cs_ip, 0)
    assert_equal(ih._cs_ip, ih.cs_ip)
    for n in range(0, 4*8):
        m = 1 << n
        ih.cs_ip = m
        assert_equal(ih.cs_ip, m)
        assert_equal(ih._cs_ip, ih.cs_ip)


# noinspection PyProtectedMember
def test_cs_ip_setter_none():
    ih = IntelHex()
    ih.cs_ip = None
    assert_is(ih.cs_ip, None)
    assert_is(ih.cs_ip, ih._cs_ip)


@raises(ValueError)
def test_cs_ip_setter_invalid():
    ih = IntelHex()
    ih.cs_ip = -1


@raises(ValueError)
def test_cs_ip_setter_invalid_2():
    ih = IntelHex()
    ih.cs_ip = 2**32


@raises(ValueError, TypeError)
def test_cs_ip_setter_invalid_3():
    ih = IntelHex()
    ih.cs_ip = "invalid"


@raises(TypeError)
def test_cs_ip_setter_invalid_4():
    ih = IntelHex()
    ih.cs_ip = set()


# noinspection PyProtectedMember
def test_eip_getter():
    ih = IntelHex()
    ih._eip = 0
    assert_equal(ih._eip, 0)
    assert_equal(ih._eip, ih.eip)
    for n in range(0, 4*8):
        m = 1 << n
        ih._eip = m
        assert_equal(ih._eip, m)
        assert_equal(ih._eip, ih.eip)


# noinspection PyProtectedMember
def test_eip_setter():
    ih = IntelHex()
    ih.eip = 0
    assert_equal(ih.eip, 0)
    assert_equal(ih._eip, ih.eip)
    for n in range(0, 4*8):
        m = 1 << n
        ih.eip = m
        assert_equal(ih.eip, m)
        assert_equal(ih._eip, ih.eip)


# noinspection PyProtectedMember
def test_eip_setter_none():
    ih = IntelHex()
    ih.eip = None
    assert_is(ih.eip, None)
    assert_is(ih.eip, ih._eip)


@raises(ValueError)
def test_eip_setter_invalid():
    ih = IntelHex()
    ih.eip = -1


@raises(ValueError)
def test_eip_setter_invalid_2():
    ih = IntelHex()
    ih.eip = 2**32


@raises(ValueError, TypeError)
def test_eip_setter_invalid_3():
    ih = IntelHex()
    ih.eip = "invalid"


@raises(TypeError)
def test_eip_setter_invalid_4():
    ih = IntelHex()
    ih.eip = set()


def test_toihexfile_interface():
    testdict = randomdict()

    def toihexfh_replacement(self, fh, **settings):
        assert_dict_equal(settings, testdict)
        assert_equal(fh.name, testfilename)
        if sys.version_info >= (3,):
            assert_true(fh.writable())
        assert_true(hasattr(fh, "write"))
        assert_true(hasattr(fh, "encoding"))  # is text file
        assert_equal(fh.tell(), 0)
        return self

    @patch('hexformat.intelhex.IntelHex.toihexfh', toihexfh_replacement)
    def do():
        ihex = IntelHex()
        ret = ihex.toihexfile(testfilename, **testdict)
        assert_is(ret, ihex)

    do()


def test_fromihexfile_interface():
    test_ignore_checksum_errors = random.randint(0, 1024)

    # noinspection PyDecorator
    @classmethod
    def fromihexfh_replacement(cls, fh, ignore_checksum_errors=False):
        assert_equal(ignore_checksum_errors, test_ignore_checksum_errors)
        assert_equal(fh.name, testfilename)
        if sys.version_info >= (3,):
            assert_true(fh.readable())
        assert_true(hasattr(fh, "read"))
        assert_true(hasattr(fh, "encoding"))  # is text file
        assert_equal(fh.tell(), 0)
        return cls()

    @patch('hexformat.intelhex.IntelHex.fromihexfh', fromihexfh_replacement)
    def do():
        ih = IntelHex.fromihexfile(testfilename, test_ignore_checksum_errors)
        assert_is_instance(ih, IntelHex)

    do()


def test_fromihexfh_interface():
    testfh = object()
    test_ignore_checksum_errors = random.randint(0, 1024)

    def loadihexfh_replacement(self, fh, ignore_checksum_errors=False):
        assert_equal(ignore_checksum_errors, test_ignore_checksum_errors)
        assert_is(fh, testfh)
        return self

    @patch('hexformat.intelhex.IntelHex.loadihexfh', loadihexfh_replacement)
    def do():
        ih = IntelHex.fromihexfh(testfh, test_ignore_checksum_errors)
        assert_is_instance(ih, IntelHex)

    do()


def test_loadihexfile_interface():
    test_ignore_checksum_errors = random.randint(0, 1024)

    def loadihexfile_replacement(self, fh, ignore_checksum_errors=False):
        assert_equal(ignore_checksum_errors, test_ignore_checksum_errors)
        assert_equal(fh.name, testfilename)
        if sys.version_info >= (3,):
            assert_true(fh.readable())
        assert_true(hasattr(fh, "read"))
        assert_true(hasattr(fh, "encoding"))  # is text file
        assert_equal(fh.tell(), 0)
        return self

    @patch('hexformat.intelhex.IntelHex.loadihexfh', loadihexfile_replacement)
    def do():
        ih = IntelHex()
        ret = ih.loadihexfile(testfilename, test_ignore_checksum_errors)
        assert_is(ret, ih)

    do()


def test_eq():
    testdata1 = randomdata(random.randint(10, 2**16))
    testaddr1 = random.randint(0, 2**32-1)
    testdata2 = randomdata(random.randint(10, 2**16))
    testaddr2 = random.randint(0, 2**32-1)
    testdata3 = randomdata(random.randint(10, 2**16))
    testaddr3 = random.randint(0, 2**32-1)
    testeid = random.randint(0, 2**32-1)
    testcsip = random.randint(0, 2**32-1)

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

    assert_equal(ih1, ih2)
    assert_equal(ih1, ih1.copy())
    ih3 = ih2.copy()
    ih3.eip -= 1
    assert_not_equal(ih1, ih3)
    ih2.cs_ip += 1
    assert_not_equal(ih1, ih2)


# noinspection PyProtectedMember
@raises(ValueError)
def test_parseihexline_failure_startchar():
    ih = IntelHex()
    return ih._parseihexline("S020000000")


# noinspection PyProtectedMember
@raises(ValueError)
def test_parseihexline_failure_hexmiscount():
    ih = IntelHex()
    return ih._parseihexline(":000102030")


# noinspection PyProtectedMember
@raises(DecodeError)
def test_parseihexline_failure_bytecount_high():
    ih = IntelHex()
    return ih._parseihexline(":04000000FFFFFF00")


# noinspection PyProtectedMember
@raises(DecodeError)
def test_parseihexline_failure_bytecount_low():
    ih = IntelHex()
    return ih._parseihexline(":02000000FFFFFF00")


# noinspection PyProtectedMember
@raises(DecodeError)
def test_parseihexline_failure_recordtype():
    ih = IntelHex()
    return ih._parseihexline(":030000ABFFFFFF00")


# noinspection PyProtectedMember
@raises(DecodeError)
def test_parseihexline_failure_recordtype_bytecount_mismatch():
    ih = IntelHex()
    return ih._parseihexline(":03000003FFFFFF00")


# noinspection PyProtectedMember
def test_parseihexline_r0():
    testline = ":10010000214601360121470136007EFE09D2190140\n"
    testbytecount = 0x10
    testaddress = 0x0100
    testrecordtype = 0x00
    testdata = bytearray.fromhex("214601360121470136007EFE09D21901")
    testchecksumcorrect = True

    ih = IntelHex()
    (recordtype, address, data, bytecount, checksumcorrect) = ih._parseihexline(testline)
    assert_equal(recordtype, testrecordtype)
    assert_equal(address, testaddress)
    assert_equal(data, testdata)
    assert_equal(bytecount, testbytecount)
    assert_equal(checksumcorrect, testchecksumcorrect)


# noinspection PyProtectedMember
def test_parseihexline_r0_wrongcrc():
    testline = ":10010000214601360121470136007EFE09D21901F3\n"
    testbytecount = 0x10
    testaddress = 0x0100
    testrecordtype = 0x00
    testdata = bytearray.fromhex("214601360121470136007EFE09D21901")
    testchecksumcorrect = False

    ih = IntelHex()
    (recordtype, address, data, bytecount, checksumcorrect) = ih._parseihexline(testline)
    assert_equal(recordtype, testrecordtype)
    assert_equal(address, testaddress)
    assert_equal(data, testdata)
    assert_equal(bytecount, testbytecount)
    assert_equal(checksumcorrect, testchecksumcorrect)


try:
    # noinspection PyStatementEffect
    bytearray.hex
except AttributeError:
    pass
else:
    # noinspection PyProtectedMember
    def test_parseihexline_r0_random():
        for r in range(0, 10):
            testbytecount = random.randint(1, 255)
            testaddress = random.randint(0, 0xFFFF)
            testrecordtype = 0x00
            testdata = randomdata(testbytecount)
            allbytes = bytearray((testbytecount, (testaddress >> 8) & 0xFF, testaddress & 0xFF, testrecordtype))
            allbytes += testdata
            allbytes += bytearray(1)
            testline = ":" + allbytes.hex().upper()
            sys.stdout.write(testline)

            ih = IntelHex()
            (recordtype, address, data, bytecount, checksumcorrect) = ih._parseihexline(testline)
            assert_equal(recordtype, testrecordtype)
            assert_equal(address, testaddress)
            assert_equal(data, testdata)
            assert_equal(bytecount, testbytecount)


RECORDTYPE_LENGTH = {
    0: None,
    1: 0,
    2: 2,
    3: 4,
    4: 2,
    5: 4,
}


# noinspection PyProtectedMember
def test_encodeihexline_recordtype_valid():
    for rt, l in RECORDTYPE_LENGTH.items():
        if l is None:
            l = random.randint(0, 200)
        ih = IntelHex()
        ih._encodeihexline(rt, 0, bytearray(l))


# noinspection PyProtectedMember
def test_encodeihexline_recordtype_invalid():
    ih = IntelHex()
    for n in list(range(6, 256)) + list(range(-128, -1)):
        yield assert_raises, EncodeError, ih._encodeihexline, n, 0, bytearray(2)


# noinspection PyProtectedMember
def test_encodeihexline_recordtype_datalength_mismatch():
    for rt, l in RECORDTYPE_LENGTH.items():
        if l is None:
            continue
        ih = IntelHex()
        if l > 1:
            yield assert_raises, EncodeError, ih._encodeihexline, rt, 0, bytearray(l - 1)
        yield assert_raises, EncodeError, ih._encodeihexline, rt, 0, bytearray(l + 1)


# noinspection PyProtectedMember
@raises(DecodeError)
def test_loadihexfh_unsupported_record_type():
    ih = IntelHex()
    ih._DATALENGTH = list(ih._DATALENGTH) + [0, ]  # Add other record type to reach last clause
    fh = FakeFileHandle((":00000006FA\n",))
    ih.loadihexfh(fh)


@raises(DecodeError)
def test_loadihexfh_checksum_error():
    ih = IntelHex()
    fh = FakeFileHandle((":00000001FE\n",))
    ih.loadihexfh(fh)


def test_loadihexfh_empty():
    ih = IntelHex()
    fh = FakeFileHandle()
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 0)


def test_loadihexfh_r0_1():
    ih = IntelHex()
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0xDEAD
    fh = FakeFileHandle((':08DEAD000123456789ABCDEFAD', ))
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.bytesperline, 8)


def test_loadihexfh_r0_2():
    ih = IntelHex()
    ih.settings(bytesperline=32)
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0xDEAD
    fh = FakeFileHandle((':08DEAD000123456789ABCDEFAD', ))
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.bytesperline, 32)


def test_loadihexfh_r1_1():
    ih = IntelHex()
    fh = FakeFileHandle((':00000001FF', ))
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 0)


def test_loadihexfh_r1_2():
    ih = IntelHex()
    fh = FakeFileHandle((':00000001FF', ':00000001FF'))
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 0)
    assert_equal(len(fh), 1)


def test_loadihexfh_r2_1():
    ih = IntelHex()
    fh = FakeFileHandle((':020000022BC011', ':08DEAD000123456789ABCDEFAD'))
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0x2BC0 * 16 + 0xDEAD
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.variant, 16)


def test_loadihexfh_r2_2():
    ih = IntelHex()
    ih.variant = 32
    fh = FakeFileHandle((':020000022BC011', ':08DEAD000123456789ABCDEFAD'))
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0x2BC0 * 16 + 0xDEAD
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.variant, 32)


def test_loadihexfh_r3_1():
    ih = IntelHex()
    fh = FakeFileHandle((':040000032BC0F0100E', ':08DEAD000123456789ABCDEFAD'))
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0xDEAD
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.variant, 16)
    assert_equal(ih.cs_ip, 0x2BC0F010)


def test_loadihexfh_r3_2():
    ih = IntelHex()
    ih.variant = 32
    fh = FakeFileHandle((':040000032BC0F0100E', ':08DEAD000123456789ABCDEFAD'))
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0xDEAD
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.variant, 32)
    assert_equal(ih.cs_ip, 0x2BC0F010)


def test_loadihexfh_r4_1():
    ih = IntelHex()
    fh = FakeFileHandle((':020000042BC00F', ':08DEAD000123456789ABCDEFAD'))
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0x2BC0DEAD
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.variant, 32)


def test_loadihexfh_r4_2():
    ih = IntelHex()
    ih.variant = 16
    fh = FakeFileHandle((':020000042BC00F', ':08DEAD000123456789ABCDEFAD'))
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0x2BC0DEAD
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.variant, 16)


def test_loadihexfh_r5_1():
    ih = IntelHex()
    fh = FakeFileHandle((':040000052BC0F0100C', ':08DEAD000123456789ABCDEFAD'))
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0xDEAD
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.variant, 32)
    assert_equal(ih.eip, 0x2BC0F010)


def test_loadihexfh_r5_2():
    ih = IntelHex()
    ih.variant = 16
    fh = FakeFileHandle((':040000052BC0F0100C', ':08DEAD000123456789ABCDEFAD'))
    testdata = bytearray.fromhex("0123456789ABCDEF")
    testaddr = 0xDEAD
    ret = ih.loadihexfh(fh)
    assert_is(ret, ih)
    assert_equal(ih.usedsize(), 8)
    assert_equal(ih.start(), testaddr)
    assert_sequence_equal(ih[:], testdata)
    assert_equal(ih.variant, 16)
    assert_equal(ih.eip, 0x2BC0F010)

