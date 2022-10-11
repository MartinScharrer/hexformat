import random
from hexformat.fillpattern import RandomContent
import unittest
from unittest.mock import patch


class TestRandomContent(unittest.TestCase):

    def test_init_noargs(self):
        fp = RandomContent()
        self.assertEqual(len(fp), 1)


    def test_init_length(self):
        for l in (1, 2, 100, 1024, 0xFFFFFFFF, 0xFFFFFFFFFF, random.randint(0, 0xFFFFFFFFFF)):
            self.assertEqual(len(RandomContent(length=l)), l)


    def test_mul(self):
        fp = RandomContent()
        for n in range(1, 1500):
            fp2 = fp * n
            self.assertEqual(len(fp2), n)


    def test_iter(self):
        fp = RandomContent(100)
        self.assertEqual(len(bytearray((b for b in fp))), 100)


    def test_index(self):
        with patch('random.randint') as randint_function:
            fp = RandomContent(5)
            randint_function.return_value = 0x45
            self.assertEqual(fp[0], 0x45)
            randint_function.return_value = 0x8A
            self.assertEqual(fp[len(fp) * 5 + 1], 0x8a)
            randint_function.return_value = 0xc4
            self.assertEqual(fp[-1], 0xc4)


    def test_slice(self):
        with patch('random.randint') as randint_function:
            testdata = bytearray.fromhex("DEAD BEEF FEED")
            fp = RandomContent(len(testdata))
            randint_function.side_effect = bytearray(testdata)
            self.assertEqual(bytearray(fp[:]), testdata[:])
            randint_function.side_effect = bytearray(testdata)
            self.assertEqual(bytearray(fp[:]), testdata[:])
            randint_function.side_effect = bytearray(testdata)
            self.assertEqual(bytearray(fp[1:]), testdata[:-1])
            randint_function.side_effect = bytearray(testdata)
            self.assertEqual(bytearray(fp[1:-2]), testdata[:-3])
            randint_function.side_effect = bytearray(testdata)
            self.assertEqual(bytearray(fp[1:3]), testdata[:-4])


    def test_imul_error_1(self):
        fp = RandomContent()
        with self.assertRaises(ValueError):
            fp * -2


    def test_imul_error_2(self):
        fp = RandomContent()
        with self.assertRaises(ValueError):
            fp * 1.4
