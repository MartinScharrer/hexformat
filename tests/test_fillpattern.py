from hexformat.fillpattern import FillPattern, RandomContent
import random


def test_init_noargs():
    fp = FillPattern()
    assert len(fp) == 1


def test_init_length():
    def do(x):
        assert len(FillPattern(length=x)) == x
    for l in (1, 2, 100, 1024, 0xFFFFFFFF, 0xFFFFFFFFFF, random.randint(0, 0xFFFFFFFFFF)):
        yield do, l


def test_init_pattern():
    def do(x):
        try:
            l = len(x)
        except TypeError:
            l = 1
        assert len(FillPattern(x)) == l
        assert len(FillPattern(x, 1)) == 1
        assert len(FillPattern(x, 5)) == 5
        assert len(FillPattern(x, 1024)) == 1024
    for p in (bytearray(100), bytearray.fromhex("05"), 0, 0xFF, (0xDE, 0xAD, 0xBE, 0xEF)):
        yield do, p


def test_index():
    testbytes = bytearray((0xDE, 0xED, 0xBE, 0xEF))
    fp = FillPattern(testbytes)
    assert fp[0] == testbytes[0]
    assert fp[1] == testbytes[1]
    assert fp[2] == testbytes[2]
    assert fp[3] == testbytes[3]
    assert fp[4] == testbytes[0]
    assert fp[-1] == testbytes[-1]
    assert fp[-2] == testbytes[-2]
    assert fp[len(testbytes)*10] == testbytes[0]


def test_slice():
    testbytes = bytearray((0xDE, 0xED, 0xBE, 0xEF))
    fp = FillPattern(testbytes)
    assert bytearray(fp[:]) == bytearray(fp)
    assert bytearray(fp[:]) == testbytes
    assert bytearray(fp[1:]) == testbytes[1:]
    assert bytearray(fp[:-1]) == testbytes[:-1]
    assert bytearray(fp[1:-2]) == testbytes[1:-2]
    assert bytearray(fp[1:3]) == testbytes[1:3]


def test_slice_step():
    fp = FillPattern(bytearray(100))
    try:
        fp[::2]
    except KeyError:
        pass
    else:
        raise AttributeError


def test_fromnumber_big():
    fp = FillPattern.fromnumber(0xDEADBEEF, width=4, byteorder='big')
    assert len(fp) == 4
    assert bytearray(fp) == bytearray((0xDE, 0xAD, 0xBE, 0xEF))


def test_fromnumber_little():
    fp = FillPattern.fromnumber(0xDEADBEEF, width=4, byteorder='little')
    assert len(fp) == 4
    assert bytearray(fp) == bytearray(reversed((0xDE, 0xAD, 0xBE, 0xEF)))


def test_frompattern_instance():
    fp1 = FillPattern((0xDE, 0xED, 0xBE, 0xEF))
    fp2 = FillPattern.frompattern(fp1)
    assert bytearray(fp1) == bytearray(fp2)
    fp3 = FillPattern.frompattern(fp1, len(fp1)*2)
    assert len(fp3) == len(fp1)*2
    fp4 = FillPattern.frompattern(fp1, len(fp1) - 1)
    assert len(fp4) == len(fp1) - 1
    assert bytearray(fp4) == bytearray(fp1[:-1])
    assert bytearray(fp4*2) == bytearray(fp1[:-1]*2)


def test_frompattern_iterable():
    testbytes = bytearray((0xDE, 0xED, 0xBE, 0xEF))
    fp = FillPattern.frompattern(testbytes)
    assert bytearray(fp) == bytearray(testbytes)


def test_setlength():
    fp = FillPattern()
    for n in range(1, 1500):
        fp.setlength(n)
        assert len(fp) == n


def test_mul():
    fp = FillPattern()
    for n in range(1, 1500):
        fp2 = fp * n
        assert len(fp2) == n


def test_imul():
    for n in range(1, 1500):
        fp = FillPattern()
        fp *= n
        assert len(fp) == n

