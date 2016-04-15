from hexformat.intelhex import IntelHex
from nose.tools import raises, assert_equal, assert_sequence_equal, assert_is, assert_true, assert_dict_equal
from nose.tools import assert_is_instance, assert_not_equal
from mock import patch
import random
import tempfile
import os
import sys
import shutil
from .test_multipartbuffer import randomdata
from .test_srecord import randomdict, randomstr

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
