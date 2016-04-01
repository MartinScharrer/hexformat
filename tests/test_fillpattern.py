from hexformat.fillpattern import FillPattern
import random
from nose.tools import assert_equal, raises


def test_init_noargs():
    fp = FillPattern()
    assert_equal(len(fp), 1)


def test_init_length():
    for l in (1, 2, 100, 1024, 0xFFFFFFFF, 0xFFFFFFFFFF, random.randint(0, 0xFFFFFFFFFF)):
        assert_equal(len(FillPattern(length=l)), l)


def test_init_pattern():
    for b in (bytearray(100), bytearray.fromhex("05"), 0, 0xFF, (0xDE, 0xAD, 0xBE, 0xEF)):
        try:
            l = len(b)
        except TypeError:
            l = 1
        assert_equal(len(FillPattern(b)), l)
        assert_equal(len(FillPattern(b, 1)), 1)
        assert_equal(len(FillPattern(b, 5)), 5)
        assert_equal(len(FillPattern(b, 1024)), 1024)


def test_index():
    testbytes = bytearray((0xDE, 0xAD, 0xBE, 0xEF))
    fp = FillPattern(testbytes)
    assert_equal(fp[0], testbytes[0])
    assert_equal(fp[1], testbytes[1])
    assert_equal(fp[2], testbytes[2])
    assert_equal(fp[3], testbytes[3])
    assert_equal(fp[4], testbytes[0])
    assert_equal(fp[-1], testbytes[-1])
    assert_equal(fp[-2], testbytes[-2])
    assert_equal(fp[len(testbytes)*10], testbytes[0])


def test_slice():
    testbytes = bytearray((0xDE, 0xAD, 0xBE, 0xEF))
    fp = FillPattern(testbytes)
    assert_equal(bytearray(fp[:]), bytearray(fp))
    assert_equal(bytearray(fp[:]), testbytes)
    assert_equal(bytearray(fp[1:]), testbytes[1:])
    assert_equal(bytearray(fp[:-1]), testbytes[:-1])
    assert_equal(bytearray(fp[1:-2]), testbytes[1:-2])
    assert_equal(bytearray(fp[1:3]), testbytes[1:3])


@raises(KeyError)
def test_slice_step():
    fp = FillPattern(bytearray(100))
    fp[::2]


def test_fromnumber_big():
    fp = FillPattern.fromnumber(0xDEADBEEF, width=4, byteorder='big')
    assert_equal(len(fp), 4)
    assert_equal(bytearray(fp), bytearray((0xDE, 0xAD, 0xBE, 0xEF)))


def test_fromnumber_little():
    fp = FillPattern.fromnumber(0xDEADBEEF, width=4, byteorder='little')
    assert_equal(len(fp), 4)
    assert_equal(bytearray(fp), bytearray(reversed((0xDE, 0xAD, 0xBE, 0xEF))))


def test_frompattern_instance():
    fp1 = FillPattern((0xDE, 0xAD, 0xBE, 0xEF))
    fp2 = FillPattern.frompattern(fp1)
    assert_equal(bytearray(fp1), bytearray(fp2))
    fp3 = FillPattern.frompattern(fp1, len(fp1)*2)
    assert_equal(len(fp3), len(fp1)*2)
    fp4 = FillPattern.frompattern(fp1, len(fp1) - 1)
    assert_equal(len(fp4), len(fp1) - 1)
    assert_equal(bytearray(fp4), bytearray(fp1[:-1]))
    assert_equal(bytearray(fp4*2), bytearray(fp1[:-1]*2))


def test_frompattern_iterable():
    testbytes = bytearray((0xDE, 0xAD, 0xBE, 0xEF))
    fp = FillPattern.frompattern(testbytes)
    assert_equal(bytearray(fp), bytearray(testbytes))


def test_setlength():
    fp = FillPattern()
    for n in range(1, 1500):
        fp.setlength(n)
        assert_equal(len(fp), n)


def test_mul():
    fp = FillPattern()
    for n in range(1, 1500):
        fp2 = fp * n
        assert_equal(len(fp2), n)


def test_imul():
    for n in range(1, 1500):
        fp = FillPattern()
        fp *= n
        assert_equal(len(fp), n)


def test_iter():
    testdata = bytearray((random.randint(0, 255) for n in range(0, 100)))
    fp = FillPattern(testdata)
    assert_equal(bytearray((b for b in fp)), testdata)
    assert_equal(bytearray((b for b in fp[:])), testdata)
    fp2 = fp[10:]
    assert_equal(bytearray((b for b in fp2)), testdata[10:])
    fp3 = fp2[10:]
    assert_equal(bytearray((b for b in fp3)), testdata[20:])

