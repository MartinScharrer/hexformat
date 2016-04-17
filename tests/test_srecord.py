from hexformat.srecord import SRecord
from hexformat.base import EncodeError, DecodeError
from nose.tools import assert_sequence_equal, assert_equal, assert_is, assert_raises, assert_dict_equal, assert_true
from nose.tools import raises, assert_is_instance, assert_list_equal, assert_false, assert_tuple_equal
from mock import patch
from .test_multipartbuffer import randomdata
import random
import tempfile
import sys
import os
import shutil

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
    dirname = tempfile.mkdtemp(prefix="test_srecord_")
    sys.stderr.write("Tempdir: {:s}\n".format(dirname))
    testfilename = os.path.join(dirname, "testdata.srec")


def teardown():
    # noinspection PyBroadException
    try:
        shutil.rmtree(dirname)
    except:
        pass


def randomstr(length):
    # noinspection PyUnusedLocal
    return bytearray((random.randint(ord('a'), ord('z')) for n in range(0, length))).decode()


def randomdict(number=None):
    if number is None:
        number = random.randint(1, 16)
    # noinspection PyUnusedLocal
    return {randomstr(random.randint(1, 16)): randomdata(random.randint(1, 16)) for n in range(0, number)}


# noinspection PyProtectedMember
def test_startaddress_getter():
    srec = SRecord()
    for n in (0, 1, 2 ** 16 - 1, 2 ** 16, 2 ** 16 + 1, 2 ** 24 - 1, 2 ** 24, 2 ** 24 + 1, 2 ** 32 - 2, 2 ** 32 - 1):
        srec._startaddress = n
        assert_equal(srec._startaddress, n)
        assert_equal(srec._startaddress, srec.startaddress)
        r = random.randint(0, 2 ** 32 - 1)
        srec._startaddress = r
        assert_equal(srec._startaddress, r)
        assert_equal(srec._startaddress, srec.startaddress)


# noinspection PyProtectedMember
def test_startaddress_setter():
    srec = SRecord()
    for n in (0, 1, 2 ** 16 - 1, 2 ** 16, 2 ** 16 + 1, 2 ** 24 - 1, 2 ** 24, 2 ** 24 + 1, 2 ** 32 - 2, 2 ** 32 - 1):
        srec.startaddress = n
        assert_equal(n, srec.startaddress)
        assert_equal(srec._startaddress, srec.startaddress)
        r = random.randint(0, 2 ** 32 - 1)
        srec.startaddress = r
        assert_equal(r, srec.startaddress)
        assert_equal(srec._startaddress, srec.startaddress)


# noinspection PyProtectedMember
def test_startaddress_setter_none():
    srec = SRecord()
    srec.startaddress = None
    assert_is(srec.startaddress, None)
    assert_is(srec.startaddress, srec._startaddress)


@raises(ValueError)
def test_startaddress_setter_invalid():
    srec = SRecord()
    srec.startaddress = -1


@raises(ValueError)
def test_startaddress_setter_invalid_2():
    srec = SRecord()
    srec.startaddress = 2 ** 32


@raises(ValueError, TypeError)
def test_startaddress_setter_invalid_3():
    srec = SRecord()
    srec.startaddress = "invalid"


@raises(TypeError)
def test_startaddress_setter_invalid_4():
    srec = SRecord()
    srec.startaddress = dict()


# noinspection PyProtectedMember
def test_addresslength_getter():
    srec = SRecord()
    for n in (0, 1, 2 ** 16 - 1, 2 ** 16, 2 ** 16 + 1, 2 ** 24 - 1, 2 ** 24, 2 ** 24 + 1, 2 ** 32 - 2, 2 ** 32 - 1):
        srec._addresslength = n
        assert_equal(srec._addresslength, n)
        assert_equal(srec._addresslength, srec.addresslength)
        r = random.randint(0, 2 ** 32 - 1)
        srec._addresslength = r
        assert_equal(srec._addresslength, r)
        assert_equal(srec._addresslength, srec.addresslength)


# noinspection PyProtectedMember
def test_addresslength_setter():
    srec = SRecord()
    for n in (2, 3, 4):
        srec.addresslength = n
        assert_equal(n, srec.addresslength)
        assert_equal(srec._addresslength, srec.addresslength)


# noinspection PyProtectedMember
def test_addresslength_setter_none():
    srec = SRecord()
    srec.addresslength = None
    assert_is(srec.addresslength, None)
    assert_is(srec.addresslength, srec._addresslength)


@raises(ValueError)
def test_addresslength_setter_invalid():
    srec = SRecord()
    srec.addresslength = 1


@raises(ValueError)
def test_addresslength_setter_invalid_2():
    srec = SRecord()
    srec.addresslength = 5


@raises(ValueError, TypeError)
def test_addresslength_setter_invalid_3():
    srec = SRecord()
    srec.addresslength = "invalid"


@raises(TypeError)
def test_addresslength_setter_invalid_4():
    srec = SRecord()
    srec.addresslength = dict()


# noinspection PyProtectedMember
def test_bytesperline_getter():
    srec = SRecord()
    for n in range(1, 254):
        srec._bytesperline = n
        assert_equal(srec._bytesperline, n)
        assert_equal(srec._bytesperline, srec.bytesperline)


# noinspection PyProtectedMember
def test_bytesperline_setter():
    srec = SRecord()
    for n in range(1, 254):
        srec.bytesperline = n
        assert_equal(srec.bytesperline, n)
        assert_equal(srec._bytesperline, srec.bytesperline)


# noinspection PyProtectedMember
def test_bytesperline_setter_none():
    srec = SRecord()
    srec.bytesperline = None
    assert_is(srec.bytesperline, None)
    assert_is(srec.bytesperline, srec._bytesperline)


@raises(ValueError)
def test_bytesperline_setter_invalid():
    srec = SRecord()
    srec.bytesperline = 0


@raises(ValueError)
def test_bytesperline_setter_invalid_2():
    srec = SRecord()
    srec.bytesperline = 254


@raises(ValueError, TypeError)
def test_bytesperline_setter_invalid_3():
    srec = SRecord()
    srec.bytesperline = "invalid"


@raises(TypeError)
def test_bytesperline_setter_invalid_4():
    srec = SRecord()
    srec.bytesperline = dict()


# noinspection PyProtectedMember
def test_header_getter():
    srec = SRecord()
    # noinspection PyUnusedLocal
    for n in (b"", b"Test", b"Long string " * 10, randomdata(253),
              "Some string which will be encoded".encode(),
              bytearray((random.randint(0, 255) for r in range(0, random.randint(0, 253))))):
        srec._header = n
        assert_equal(n, srec.header)
        assert_equal(srec._header, srec.header)


# noinspection PyProtectedMember
def test_header_setter():
    srec = SRecord()
    # noinspection PyUnusedLocal
    for n in (b"", b"Test", b"Long string " * 10, randomdata(253),
              "Some string which will be encoded".encode(),
              bytearray((random.randint(0, 255) for r in range(0, random.randint(0, 253))))):
        srec.header = n
        assert_equal(n, srec.header)
        assert_equal(srec._header, srec.header)


# noinspection PyProtectedMember
def test_header_setter_none():
    srec = SRecord()
    srec.header = None
    assert_is(srec.header, None)
    assert_is(srec.header, srec._header)


# noinspection PyProtectedMember
def test_header_setter_large():
    testdata = randomdata(254)
    srec = SRecord()
    srec.header = testdata
    assert_equal(srec.header, testdata[0:253])
    assert_equal(srec.header, srec._header)


@raises(TypeError)
def test_header_setter_invalid():
    srec = SRecord()
    srec.header = 0


@raises(TypeError)
def test_header_setter_invalid_4():
    srec = SRecord()
    srec.header = object()


# noinspection PyProtectedMember
def test_write_number_of_records_getter():
    srec = SRecord()
    for n in (True, False, 0, 1, 2, -1, 2 ** 32, -2 ** 32):
        srec._write_number_of_records = bool(n)
        assert_equal(bool(n), srec.write_number_of_records)
        assert_equal(srec._write_number_of_records, srec.write_number_of_records)


# noinspection PyProtectedMember
def test_write_number_of_records_setter():
    srec = SRecord()
    for n in (True, False, 0, 1, 2, -1, 2 ** 32, -2 ** 32):
        srec.write_number_of_records = n
        assert_equal(bool(n), srec.write_number_of_records)
        assert_equal(srec._write_number_of_records, srec.write_number_of_records)


# noinspection PyProtectedMember
def test_write_number_of_records_setter_none():
    srec = SRecord()
    srec.write_number_of_records = None
    assert_is(srec.write_number_of_records, None)
    assert_is(srec.write_number_of_records, srec._write_number_of_records)


# noinspection PyProtectedMember
def test__minaddresslength():
    assert_equal(SRecord._minaddresslength(0), 2)

    # noinspection PyProtectedMember
    def compare(num):
        minlen = SRecord._minaddresslength(num)
        m = int(("0000" + hex(num)[2:].replace('L', ''))[-2 * minlen:], 16)
        assert_equal(num, m)

    for s in range(1, 32):
        n = 1 << s
        compare(n)
        compare(n - 1)
        compare(n + 1)

    assert_raises(ValueError, SRecord._minaddresslength, 2 ** 32)


# noinspection PyProtectedMember
def test__s123addr():
    # noinspection PyProtectedMember
    def compare(al, val):
        retdata = bytearray(iter(SRecord._s123addr(al, val)))
        compdata = bytearray.fromhex((("00" * al) + hex(val)[2:].replace('L', ''))[-2 * al:])
        assert_sequence_equal(retdata, compdata)

    for adrlen in (2, 3, 4):
        for s in range(1, 8 * adrlen):
            n = 1 << s
            compare(adrlen, n)
            compare(adrlen, n - 1)
            compare(adrlen, n + 1)

    assert_raises(ValueError, SRecord._s123addr, 0, 0)
    assert_raises(ValueError, SRecord._s123addr, 1, 0)
    assert_raises(ValueError, SRecord._s123addr, 5, 0)


def test_tosrecfile_interface():
    testdict = randomdict()

    def tosrecfh_replacement(self, fh, **settings):
        assert_dict_equal(settings, testdict)
        assert_equal(fh.name, testfilename)
        if sys.version_info >= (3,):
            assert_true(fh.writable())
        assert_true(hasattr(fh, "write"))
        assert_true(hasattr(fh, "encoding"))  # is text file
        assert_equal(fh.tell(), 0)
        return self

    @patch('hexformat.srecord.SRecord.tosrecfh', tosrecfh_replacement)
    def do():
        srec = SRecord()
        ret = srec.tosrecfile(testfilename, **testdict)
        assert_is(ret, srec)

    do()


def test_fromsrecfile_interface():
    test_raise_error_on_miscount = random.randint(0, 1024)

    # noinspection PyDecorator
    @classmethod
    def fromsrecfh_replacement(cls, fh, raise_error_on_miscount=True):
        assert_equal(raise_error_on_miscount, test_raise_error_on_miscount)
        assert_equal(fh.name, testfilename)
        if sys.version_info >= (3,):
            assert_true(fh.readable())
        assert_true(hasattr(fh, "read"))
        assert_true(hasattr(fh, "encoding"))  # is text file
        assert_equal(fh.tell(), 0)
        return cls()

    @patch('hexformat.srecord.SRecord.fromsrecfh', fromsrecfh_replacement)
    def do():
        srec = SRecord.fromsrecfile(testfilename, test_raise_error_on_miscount)
        assert_is_instance(srec, SRecord)

    do()


def test_fromsrecfh_interface():
    testfh = object()
    test_raise_error_on_miscount = random.randint(0, 1024)

    def loadsrecfh_replacement(self, fh, raise_error_on_miscount=True):
        assert_equal(raise_error_on_miscount, test_raise_error_on_miscount)
        assert_is(fh, testfh)
        return self

    @patch('hexformat.srecord.SRecord.loadsrecfh', loadsrecfh_replacement)
    def do():
        srec = SRecord.fromsrecfh(testfh, test_raise_error_on_miscount)
        assert_is_instance(srec, SRecord)

    do()


def test_loadsrecfile_interface():
    test_overwrite_metadata = random.randint(0, 1024)
    test_overwrite_data = random.randint(0, 1024)
    test_raise_error_on_miscount = random.randint(0, 1024)

    def loadsrecfile_replacement(self, fh, overwrite_metadata=False, overwrite_data=True, raise_error_on_miscount=True):
        assert_equal(overwrite_metadata, test_overwrite_metadata)
        assert_equal(overwrite_data, test_overwrite_data)
        assert_equal(raise_error_on_miscount, test_raise_error_on_miscount)
        assert_equal(fh.name, testfilename)
        if sys.version_info >= (3,):
            assert_true(fh.readable())
        assert_true(hasattr(fh, "read"))
        assert_true(hasattr(fh, "encoding"))  # is text file
        assert_equal(fh.tell(), 0)
        return self

    @patch('hexformat.srecord.SRecord.loadsrecfh', loadsrecfile_replacement)
    def do():
        srec = SRecord()
        ret = srec.loadsrecfile(testfilename, test_overwrite_metadata,
                                test_overwrite_data, test_raise_error_on_miscount)
        assert_is(ret, srec)

    do()


def test_encodesrecline_failure():
    # noinspection PyProtectedMember
    @raises(EncodeError)
    def do(recordtype):
        SRecord._encodesrecline(None, recordtype, 0, bytearray())

    yield do, 10
    yield do, 11
    yield do, "invalid"


def test_tosrecfh_addresslength2():
    srec = SRecord().set(0x8CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
    expected = [
        "S00700005465737458\n",
        "S1138CE0FACEDEEDCAFEBEEF1234567890ABCDEF6D\n",
        "S903FFFFFE\n",
    ]
    fh = FakeFileHandle()
    srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFF, addresslength=2, write_number_of_records=False)
    assert_list_equal(fh, expected)
    fh = FakeFileHandle()
    srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFF, write_number_of_records=False)
    assert_list_equal(fh, expected)


def test_tosrecfh_addresslength3():
    srec = SRecord().set(0xFF8CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
    expected = [
        "S00700005465737458\n",
        "S214FF8CE0FACEDEEDCAFEBEEF1234567890ABCDEF6D\n",
        "S804FFFFFFFE\n",
    ]
    fh = FakeFileHandle()
    srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFFFF, addresslength=3, write_number_of_records=False)
    yield assert_list_equal, fh, expected
    fh = FakeFileHandle()
    srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFFFF, write_number_of_records=False)
    yield assert_list_equal, fh, expected


def test_tosrecfh_addresslength4():
    srec = SRecord().set(0xFF008CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
    expected = [
        "S00700005465737458\n",
        "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
        "S705FFFFFFFFFE\n",
    ]
    fh = FakeFileHandle()
    srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFFFFFF, addresslength=4, write_number_of_records=False)
    yield assert_list_equal, fh, expected
    fh = FakeFileHandle()
    srec.tosrecfh(fh, header=b"Test", startaddress=0xFFFFFFFF, write_number_of_records=False)
    yield assert_list_equal, fh, expected


def test_tosrecfh_write_number_of_records():
    srec = SRecord().set(0xFF008CE0, bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF"))
    expected = [
        "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
        "S5030001FB\n",
        "S70500000000FA\n",
    ]
    fh = FakeFileHandle()
    srec.tosrecfh(fh, write_number_of_records=True)
    yield assert_list_equal, fh, expected


def test_tosrecfh_write_number_of_records_s5():
    srec = SRecord().fill(0x0, 0xFFFF)
    fh = FakeFileHandle()
    expected = "S503FFFFFE\n"
    srec.tosrecfh(fh, bytesperline=1, write_number_of_records=True)
    assert_equal(fh[-2], expected)


def test_tosrecfh_write_number_of_records_s6():
    srec = SRecord().fill(0x0, 0x10000)
    fh = FakeFileHandle()
    expected = "S604010000FA\n"
    srec.tosrecfh(fh, bytesperline=1, write_number_of_records=True)
    assert_equal(fh[-2], expected)


def test_tosrecfh_write_number_of_records_too_large():
    srec = SRecord().fill(0x0, 0x1000000)
    fh = FakeFileHandle()
    srec.tosrecfh(fh, bytesperline=1, addresslength=3, write_number_of_records=True, header=b'Test')
    assert_false(fh[-2].startswith('S3'))
    assert_equal(len(fh), 0x1000002)


test_tosrecfh_write_number_of_records_too_large.slow = 1


# noinspection PyProtectedMember
@raises(DecodeError)
def test_parsesrecline_failure1():
    return SRecord._parsesrecline(":0000000000000")


# noinspection PyProtectedMember
@raises(DecodeError)
def test_parsesrecline_failure2():
    return SRecord._parsesrecline("s000000000000")


# noinspection PyProtectedMember
@raises(DecodeError)
def test_parsesrecline_failure4():
    """ Missing hexdigit """
    return SRecord._parsesrecline("S101000")


# noinspection PyProtectedMember
@raises(DecodeError)
def test_parsesrecline_failure5():
    return SRecord._parsesrecline("S10800")


# noinspection PyProtectedMember
@raises(DecodeError)
def test_parsesrecline_failure6():
    return SRecord._parsesrecline("SX0800")


# noinspection PyProtectedMember
def test_parsesrecline_ok():
    testaddress = 0xFF008CE0
    testdata = bytearray.fromhex("FACE DEED CAFE BEEF 1234 5678 90AB CDEF")
    yield (assert_tuple_equal, SRecord._parsesrecline("S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C"),
           (3, testaddress, testdata, len(testdata), True))


def test_loadsrecfh_1():
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
    yield assert_equal, srec, expectedsrec
    yield assert_equal, srec.bytesperline, expectedsrec.bytesperline
    yield assert_equal, srec.write_number_of_records, expectedsrec.write_number_of_records
    yield assert_equal, srec.header, expectedsrec.header


def test_loadsrecfh_2():
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
    yield assert_equal, srec, expectedsrec
    yield assert_equal, srec.bytesperline, expectedsrec.bytesperline
    yield assert_true, srec.write_number_of_records
    yield assert_equal, srec.header, expectedsrec.header


@raises(DecodeError)
def test_loadsrecfh_countmissmatch_1():
    fh = FakeFileHandle((
        "S00700005465737458\n",
        "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
        "S5030002FA\n",
        "S70500000000FA\n",
    ))
    srec = SRecord()
    srec.loadsrecfh(fh)


@raises(DecodeError)
def test_loadsrecfh_countmissmatch_s5_true():
    fh = FakeFileHandle((
        "S00700005465737458\n",
        "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
        "S5030002FA\n",
        "S70500000000FA\n",
    ))
    srec = SRecord()
    srec.loadsrecfh(fh, raise_error_on_miscount=True)


def test_loadsrecfh_countmissmatch_s5_false():
    fh = FakeFileHandle((
        "S00700005465737458\n",
        "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
        "S5030002FA\n",
        "S70500000000FA\n",
    ))
    srec = SRecord()
    srec.loadsrecfh(fh, raise_error_on_miscount=False)


@raises(DecodeError)
def test_loadsrecfh_countmissmatch_s6_true():
    fh = FakeFileHandle((
        "S00700005465737458\n",
        "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
        "S604000002F8\n",
        "S70500000000FA\n",
    ))
    srec = SRecord()
    srec.loadsrecfh(fh, raise_error_on_miscount=True)


def test_loadsrecfh_countmissmatch_s6_false():
    fh = FakeFileHandle((
        "S00700005465737458\n",
        "S315FF008CE0FACEDEEDCAFEBEEF1234567890ABCDEF6C\n",
        "S604000002F8\n",
        "S70500000000FA\n",
    ))
    srec = SRecord()
    srec.loadsrecfh(fh, raise_error_on_miscount=False)


def test_loadsrecfh_startaddress_1():
    fh = FakeFileHandle((
        "S705000001FFFA\n",
    ))
    srec = SRecord()
    srec.loadsrecfh(fh)
    yield assert_equal, srec.startaddress, 0x1FF


def test_loadsrecfh_startaddress_2():
    fh = FakeFileHandle((
        "S705000001FFFA\n",
    ))
    srec = SRecord(startaddress=0xDEADBEEF)
    srec.loadsrecfh(fh)
    yield assert_equal, srec.startaddress, 0xDEADBEEF


@raises(DecodeError)
def test_loadsrecfh_invalid_recordtype():
    fh = FakeFileHandle((
        "S405000301FFFA\n",
    ))
    srec = SRecord(startaddress=0xDEADBEEF)
    srec.loadsrecfh(fh)
