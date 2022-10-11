from hexformat.fillpattern import int_to_bytes
import unittest
import random


testit = True
refavailable = False
try:
    if int_to_bytes is int.to_bytes:
        testit = False
        refavailable = True
except AttributeError:
    pass


class TestIntToBytes(unittest.TestCase):

    def do(self, value, length, byteorder, signed, expected):
        self.assertEqual(int_to_bytes(value, length, byteorder, signed=signed), bytearray.fromhex(expected))

    def test_0(self):
        testvector = (
            # value, length, byteorder, signed, expected
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
            with self.subTest(repr(tv)):
                self.do(*tv)

    def test_signed(self):
        testvector = (
            # value, length, byteorder, signed, expected
            (-1, 1, 'big', True, "FF"),
            (-1, 2, 'big', True, "FFFF"),
            (-1, 3, 'big', True, "FFFFFF"),
            (-1, 4, 'big', True, "FFFF FFFF"),
            (-1, 8, 'big', True, "FFFF FFFF FFFF FFFF"),
            (-1, 1, 'little', True, "FF"),
            (-1, 2, 'little', True, "FFFF"),
            (-1, 3, 'little', True, "FFFFFF"),
            (-1, 4, 'little', True, "FFFF FFFF"),
            (-1, 8, 'little', True, "FFFF FFFF FFFF FFFF"),
        )
        for tv in testvector:
            with self.subTest(repr(tv)):
                self.do(*tv)

    def test_overflow_1(self):
        with self.assertRaises(OverflowError):
            int_to_bytes(-1, 1, 'big', signed=False)

    def test_overflow_2(self):
        with self.assertRaises(OverflowError):
            int_to_bytes(256, 1, 'big', signed=False)

    def test_overflow_3(self):
        with self.assertRaises(OverflowError):
            int_to_bytes(128, 1, 'big', signed=True)

    def test_overflow_4(self):
        with self.assertRaises(OverflowError):
            int_to_bytes(-129, 1, 'big', signed=True)

    def test_valueerror(self):
        with self.assertRaises(ValueError):
            int_to_bytes(0, 1, 'something else')

    def do2(self, value, length, byteorder, signed):
        self.assertEqual(int_to_bytes(value, length, byteorder, signed=signed),
                         value.to_bytes(length, byteorder, signed=signed))

    def test_int(self):
        if testit and refavailable:
            for n in range(1, 17):
                limit = 2 ** (n * 8 - 1)
                maxvalue = 2 * limit - 1
                for bo in ('big', 'little'):
                    self.do2(maxvalue, n, bo, False)
                    self.do2(-limit, n, bo, True)
                    self.do2(-limit + 1, n, bo, True)
                    self.do2(limit - 1, n, bo, True)
                    self.do2(limit - 2, n, bo, True)
                    for i in range(0, 100):
                        self.do2(random.randint(0, maxvalue), n, bo, False)
                        self.do2(random.randint(-limit, limit - 1), n, bo, True)
