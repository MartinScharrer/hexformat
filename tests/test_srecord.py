from hexformat.srecord import SRecord
from nose.tools import assert_sequence_equal, assert_equal, assert_is, assert_raises, assert_dict_equal, assert_true
from nose.tools import raises, assert_is_instance
from mock import patch
from .test_multipartbuffer import randomdata
import random
import tempfile
import sys
import os
import shutil

dirname = ""
testfilename = ""


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
    for n in (0, 1, 2**16-1, 2**16, 2**16+1, 2**24-1, 2**24, 2**24+1, 2**32-2, 2**32-1):
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
    for n in (0, 1, 2**16-1, 2**16, 2**16+1, 2**24-1, 2**24, 2**24+1, 2**32-2, 2**32-1):
        srec.startaddress = n
        assert_equal(n, srec.startaddress)
        assert_equal(srec._startaddress, srec.startaddress)
        r = random.randint(0, 2**32-1)
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
    srec.startaddress = 2**32


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
    for n in (0, 1, 2**16-1, 2**16, 2**16+1, 2**24-1, 2**24, 2**24+1, 2**32-2, 2**32-1):
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
    for n in range(0, 254):
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
    for n in (b"", b"Test", b"Long string Long string Long string Long string Long string Long string ",
              "Some string which will be encoded".encode(),
              bytearray((random.randint(0, 255) for r in range(0, random.randint(0, 253))))):
        srec._header = n
        assert_equal(n, srec.header)
        assert_equal(srec._header, srec.header)


# noinspection PyProtectedMember
def test_header_setter():
    srec = SRecord()
    # noinspection PyUnusedLocal
    for n in (b"", b"Test", b"Long string Long string Long string Long string Long string Long string ",
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
    for n in (True, False, 0, 1, 2, -1, 2**32, -2**32):
        srec._write_number_of_records = bool(n)
        assert_equal(bool(n), srec.write_number_of_records)
        assert_equal(srec._write_number_of_records, srec.write_number_of_records)


# noinspection PyProtectedMember
def test_write_number_of_records_setter():
    srec = SRecord()
    for n in (True, False, 0, 1, 2, -1, 2**32, -2**32):
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
        compare(n-1)
        compare(n+1)

    assert_raises(ValueError, SRecord._minaddresslength, 2**32)


# noinspection PyProtectedMember
def test__s123addr():

    # noinspection PyProtectedMember
    def compare(al, val):
        retdata = bytearray(iter(SRecord._s123addr(al, val)))
        compdata = bytearray.fromhex((("00" * al) + hex(val)[2:].replace('L', ''))[-2*al:])
        assert_sequence_equal(retdata, compdata)

    for adrlen in (2, 3, 4):
        for s in range(1, 8*adrlen):
            n = 1 << s
            compare(adrlen, n)
            compare(adrlen, n-1)
            compare(adrlen, n+1)

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
