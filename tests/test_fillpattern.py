import random
import unittest

from hexformat.fillpattern import FillPattern


class TestFillpattern(TestCase):

    def test_init_noargs(self):
        fp = FillPattern()
        self.assertEqual(len(fp), 1)

    def test_init_length(self):
        for length in (1, 2, 100, 1024, 0xFFFFFFFF, 0xFFFFFFFFFF, randint(0, 0xFFFFFFFFFF)):
            self.assertEqual(len(FillPattern(length=length)), length)

    def test_init_pattern(self):
        for b in (bytearray(100), bytearray.fromhex("05"), 0, 0xFF, (0xDE, 0xAD, 0xBE, 0xEF)):
            try:
                length = len(b)
            except TypeError:
                length = 1
            self.assertEqual(len(FillPattern(b)), length)
            self.assertEqual(len(FillPattern(b, 1)), 1)
            self.assertEqual(len(FillPattern(b, 5)), 5)
            self.assertEqual(len(FillPattern(b, 1024)), 1024)

    def test_index(self):
        testbytes = bytearray((0xDE, 0xAD, 0xBE, 0xEF))
        fp = FillPattern(testbytes)
        self.assertEqual(fp[0], testbytes[0])
        self.assertEqual(fp[1], testbytes[1])
        self.assertEqual(fp[2], testbytes[2])
        self.assertEqual(fp[3], testbytes[3])
        self.assertEqual(fp[4], testbytes[0])
        self.assertEqual(fp[-1], testbytes[-1])
        self.assertEqual(fp[-2], testbytes[-2])
        self.assertEqual(fp[len(testbytes) * 10], testbytes[0])

    def test_slice(self):
        testbytes = bytearray((0xDE, 0xAD, 0xBE, 0xEF))
        fp = FillPattern(testbytes)
        testvector = (
            # FillPattern, Expected
            (bytearray(fp[:]), bytearray(fp)),
            (bytearray(fp[:]), testbytes),
            (bytearray(fp[1:]), testbytes[1:]),
            (bytearray(fp[:-1]), testbytes[:-1]),
            (bytearray(fp[1:-2]), testbytes[1:-2]),
            (bytearray(fp[1:3]), testbytes[1:3]),
            (bytearray(fp[-2:-1]), testbytes[-2:-1]),
            (bytearray(fp[8:12][0:4]), testbytes[0:4]),
            (len(fp[8:12]), 4),
        )
        for n, tv in enumerate(testvector):
            with self.subTest(n):
                self.assertEqual(*tv)

    def test_slice_step(self):
        fp = FillPattern(bytearray(100))
        with self.assertRaises(KeyError):
            return fp[::2]

    def test_fromnumber_big(self):
        fp = FillPattern.fromnumber(0xDEADBEEF, width=4, byteorder='big')
        self.assertEqual(len(fp), 4)
        self.assertEqual(bytearray(fp), bytearray((0xDE, 0xAD, 0xBE, 0xEF)))

    def test_fromnumber_little(self):
        fp = FillPattern.fromnumber(0xDEADBEEF, width=4, byteorder='little')
        self.assertEqual(len(fp), 4)
        self.assertEqual(bytearray(fp), bytearray(reversed((0xDE, 0xAD, 0xBE, 0xEF))))

    def test_frompattern_instance(self):
        fp1 = FillPattern((0xDE, 0xAD, 0xBE, 0xEF))
        fp2 = FillPattern.frompattern(fp1)
        self.assertEqual(bytearray(fp1), bytearray(fp2))
        fp3 = FillPattern.frompattern(fp1, len(fp1) * 2)
        self.assertEqual(len(fp3), len(fp1) * 2)
        fp4 = FillPattern.frompattern(fp1, len(fp1) - 1)
        self.assertEqual(len(fp4), len(fp1) - 1)
        self.assertEqual(bytearray(fp4), bytearray(fp1[:-1]))
        self.assertEqual(bytearray(fp4 * 2), bytearray(fp1[:-1] * 2))

    def test_frompattern_iterable(self):
        testbytes = bytearray((0xDE, 0xAD, 0xBE, 0xEF))
        fp = FillPattern.frompattern(testbytes)
        self.assertEqual(bytearray(fp), bytearray(testbytes))

    def test_setlength(self):
        fp = FillPattern()
        for n in range(1, 1500):
            fp.setlength(n)
            self.assertEqual(len(fp), n)

    def test_mul(self):
        fp = FillPattern()
        for n in range(1, 1500):
            fp2 = fp * n
            self.assertEqual(len(fp2), n)

    def test_imul(self):
        for n in range(1, 1500):
            fp = FillPattern()
            fp *= n
            self.assertEqual(len(fp), n)

    def test_iter(self):
        testdata = randbytes(100)
        fp = FillPattern(testdata)
        self.assertEqual(bytearray((b for b in fp)), testdata)
        self.assertEqual(bytearray((b for b in fp[:])), testdata)
        fp2 = fp[10:]
        self.assertEqual(bytearray((b for b in fp2)), testdata[10:])
        fp3 = fp2[10:]
        self.assertEqual(bytearray((b for b in fp3)), testdata[20:])

    def test_mul_error_1(self):
        with self.assertRaises(ValueError):
            FillPattern() * -1

    def test_mul_error_2(self):
        with self.assertRaises(ValueError):
            FillPattern() * 1.5

    def test_imul_error_1(self):
        fp = FillPattern()
        with self.assertRaises(ValueError):
            fp *= -2

    def test_imul_error_2(self):
        fp = FillPattern()
        with self.assertRaises(ValueError):
            fp *= 1.4

    def test_init_error(self):
        with self.assertRaises(ValueError):
            FillPattern(256)
