from hexformat.srecord import SRecord
from nose.tools import assert_sequence_equal, assert_equal, assert_is, raises, assert_raises
import random


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
    srec.header = dict(a=1)


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
        m = int(("0000" + hex(num)[2:])[-2 * minlen:], 16)
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
        compdata = bytearray.fromhex((("00" * al) + hex(val)[2:])[-2*al:])
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

