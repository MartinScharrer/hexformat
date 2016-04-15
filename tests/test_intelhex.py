from hexformat.intelhex import IntelHex
from nose.tools import raises, assert_equal, assert_sequence_equal, assert_is


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
