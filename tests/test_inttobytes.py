from hexformat.fillpattern import int_to_bytes
from nose.tools import assert_equal
import random
from nose.plugins.skip import SkipTest

try:
    if int_to_bytes is int.to_bytes:
        raise SkipTest

    def skipifnotpython3():
        pass
except AttributeError:
    def skipifnotpython3():
        raise SkipTest


def do(value, length, byteorder, signed, expected):
    assert_equal(int_to_bytes(value, length, byteorder, signed=signed), bytearray.fromhex(expected))


def test_0():
    testvector = (
            (0, 1, 'big', False, "00"),
            (0, 2, 'big', False, "0000"),
            (0, 3, 'big', False, "000000"),
            (0, 4, 'big', False, "00000000"),
            (0, 8, 'big', False, "00000000 00000000"),
            (0, 1, 'big', True, "00"),
            (0, 2, 'big', True, "0000"),
            (0, 3, 'big', True, "000000"),
            (0, 4, 'big', True, "00000000"),
            (0, 8, 'big', True, "00000000 00000000"),
            (0, 1, 'little', False, "00"),
            (0, 2, 'little', False, "0000"),
            (0, 3, 'little', False, "000000"),
            (0, 4, 'little', False, "00000000"),
            (0, 8, 'little', False, "00000000 00000000"),
            (0, 1, 'little', True, "00"),
            (0, 2, 'little', True, "0000"),
            (0, 3, 'little', True, "000000"),
            (0, 4, 'little', True, "00000000"),
            (0, 8, 'little', True, "00000000 00000000"),
            (0xDEADBEEF, 4, 'big', False, "DEADBEEF"),
            (0xDEADBEEF, 4, 'little', False, "EFBEADDE"),
    )
    for tv in testvector:
        yield do, tv[0], tv[1], tv[2], tv[3], tv[4]


def test_signed():
    yield do, -1, 1, 'big', True, "FF"
    yield do, -1, 2, 'big', True, "FFFF"
    yield do, -1, 3, 'big', True, "FFFFFF"
    yield do, -1, 4, 'big', True, "FFFF FFFF"
    yield do, -1, 8, 'big', True, "FFFF FFFF FFFF FFFF"
    yield do, -1, 1, 'little', True, "FF"
    yield do, -1, 2, 'little', True, "FFFF"
    yield do, -1, 3, 'little', True, "FFFFFF"
    yield do, -1, 4, 'little', True, "FFFF FFFF"
    yield do, -1, 8, 'little', True, "FFFF FFFF FFFF FFFF"


def do2(value, length, byteorder, signed):
    assert_equal(int_to_bytes(value, length, byteorder, signed=signed),
                 value.to_bytes(length, byteorder, signed=signed))


def test_int():
    skipifnotpython3()
    for n in range(1, 17):
        limit = 2**(n*8-1)
        maxvalue = 2 * limit - 1
        for bo in ('big', 'little'):
            yield do2, maxvalue, n, bo, False
            yield do2, -limit, n, bo, True
            yield do2, -limit+1, n, bo, True
            yield do2, limit - 1, n, bo, True
            yield do2, limit - 2, n, bo, True
            for i in range(0, 100):
                yield do2, random.randint(0, maxvalue), n, bo, False
                yield do2, random.randint(-limit, limit-1), n, bo, True
