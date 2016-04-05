from hexformat.srecord import SRecord
from hexformat.intelhex import IntelHex
from nose.tools import assert_equal, assert_list_equal, assert_is, raises


class FakeFileHandle(list):
    def write(self, line):
        self.append(line)


def test_settings_1():
    srec = SRecord(
        startaddress=0x123,
        addresslength=4,
        bytesperline=32,
        header=b"Bla",
        write_number_of_records=True,
    )
    assert_equal(srec.startaddress, 0x123)
    assert_equal(srec.addresslength, 4)
    assert_equal(srec.bytesperline, 32)
    assert_equal(srec.header, b"Bla")
    assert_equal(srec.write_number_of_records, True)


def test_settings_2():
    srec = SRecord()
    srec.settings(
        startaddress=0x2345,
        addresslength=2,
        bytesperline=16,
        header=b"Test it",
        write_number_of_records=False,
    )
    assert_equal(srec.startaddress, 0x2345)
    assert_equal(srec.addresslength, 2)
    assert_equal(srec.bytesperline, 16)
    assert_equal(srec.header, b"Test it")
    assert_equal(srec.write_number_of_records, False)


@raises(AttributeError)
def test_settings_3():
    SRecord(
        startaddress=0x123,
        addresslength=4,
        invalidsetting=32,
        header=b"Bla",
        write_number_of_records=True,
    )


@raises(AttributeError)
def test_settings_4():
    srec = SRecord()
    srec.settings(
        addresslength=2,
        bytesperline=16,
        header=b"Test it",
        write_number_of_records=False,
        invalid=0x2345,
    )


def test_settings_tofh():
    srec = SRecord(header=b"\xAA\xBB\xCC\xDD")
    fh = FakeFileHandle()
    srec.set(0x0, b"\x01\x23\x45\x67\x89\xAB\xCD\xEF")
    srec.tosrecfh(fh, bytesperline=4)
    testdata = ['S0070000AABBCCDDEA\n', 'S10700000123456728\n', 'S107000489ABCDEF04\n', 'S9030000FC\n']
    assert_list_equal(testdata, fh)


# noinspection PyProtectedMember
def test_fromother_1():
    srec = SRecord()
    srec.set(0, bytearray.fromhex("0123456789"))
    srec.startaddress = 0x4
    ihex = IntelHex.fromother(srec)
    assert_equal(srec._parts, ihex._parts)


# noinspection PyProtectedMember
def test_fromother_2():
    srec = SRecord()
    srec.set(0, bytearray.fromhex("0123456789"))
    srec.startaddress = 0x4
    ihex = IntelHex.fromother(srec, True)
    assert_equal(srec._parts, ihex._parts)
    assert_is(srec._parts[0][1], ihex._parts[0][1])


@raises(TypeError)
def test_fromother_3():
    SRecord.fromother({0x100: 0xDE, 0x101: 0xAD, 0x102: 0xBE, 0x103: 0xEF, 0x200: 0xFF})
