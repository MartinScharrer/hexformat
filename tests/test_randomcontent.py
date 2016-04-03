from hexformat.fillpattern import RandomContent
import random
from nose.tools import assert_equal, raises
import mock


def test_init_noargs():
    fp = RandomContent()
    assert_equal(len(fp), 1)


def test_init_length():
    for l in (1, 2, 100, 1024, 0xFFFFFFFF, 0xFFFFFFFFFF, random.randint(0, 0xFFFFFFFFFF)):
        assert_equal(len(RandomContent(length=l)), l)


def test_mul():
    fp = RandomContent()
    for n in range(1, 1500):
        fp2 = fp * n
        assert_equal(len(fp2), n)


def test_iter():
    fp = RandomContent(100)
    assert_equal(len(bytearray((b for b in fp))), 100)


@mock.patch('random.randint')
def test_index(randint_function):
    fp = RandomContent(5)
    randint_function.return_value = 0x45
    assert_equal(fp[0], 0x45)
    randint_function.return_value = 0x8A
    assert_equal(fp[len(fp)*5+1], 0x8a)
    randint_function.return_value = 0xc4
    assert_equal(fp[-1], 0xc4)


@mock.patch('random.randint')
def test_slice(randint_function):
    testdata = bytearray.fromhex("DEAD BEEF FEED")
    fp = RandomContent(len(testdata))
    randint_function.side_effect = bytearray(testdata)
    assert_equal(bytearray(fp[:]), testdata[:])
    randint_function.side_effect = bytearray(testdata)
    assert_equal(bytearray(fp[:]), testdata[:])
    randint_function.side_effect = bytearray(testdata)
    assert_equal(bytearray(fp[1:]), testdata[:-1])
    randint_function.side_effect = bytearray(testdata)
    assert_equal(bytearray(fp[1:-2]), testdata[:-3])
    randint_function.side_effect = bytearray(testdata)
    assert_equal(bytearray(fp[1:3]), testdata[:-4])


@raises(ValueError)
def test_imul_error_1():
    fp = RandomContent()
    fp * -2


@raises(ValueError)
def test_imul_error_2():
    fp = RandomContent()
    fp * 1.4
